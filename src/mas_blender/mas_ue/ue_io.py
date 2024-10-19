#!$BLENDER_PATH/python/bin python

"""
MAS Unreal Engine

"""

import pathlib
import re
import typing

import unreal


UE_ASSET_REGISTRY = unreal.AssetRegistryHelpers.get_asset_registry()
UE_ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()

UE_NAMING_CONVENTION = {
    unreal.ActorComponent: 'AC',
    unreal.AnimBlueprint: 'ABP',
    unreal.AnimMontage: 'AM',
    unreal.AnimSequence: 'AS',
    unreal.BlendSpace: 'BS',
    unreal.Blueprint: 'BP',
    unreal.BlueprintInterfaceFactory: 'BI',
    unreal.ControlRig: 'RIG',
    unreal.CurveTable : 'CT',
    unreal.DataTable: 'DT',
    unreal.Enum: 'E',
    unreal.LevelSequence: 'LS',
    unreal.Material: 'M',
    unreal.MaterialInstance: 'MI',
    unreal.MediaSource: 'MS',
    unreal.MediaPlayer: 'MP',
    unreal.NiagaraEmitter: 'FXE',
    unreal.NiagaraFunctionLibrary: 'FXF',
    unreal.NiagaraSystem: 'FXS',
    unreal.ParticleSystem: 'PS',
    unreal.PhysicsAsset: 'PHYS',
    unreal.PhysicalMaterial: 'PM',
    unreal.SkeletalMesh: 'SK',
    unreal.Skeleton: 'SKEL',
    unreal.StaticMesh: 'SM',
    unreal.Struct: 'F',
    unreal.Texture: 'T',
    unreal.WidgetBlueprint: 'WBP'
}


ASSET_IMPORT_TASK = {
    'automated': True,
    'destination_name': '', # Override optional
    'destination_path': '/Game/', # Override optional
    'filename': None, # Override required
    'options': None, # Override required
    'save': False,
    'replace_existing': True, # Override optional
}

FBX_ANIM_SEQUENCE_IMPORT_DATA = {
    'animation_length': unreal.FBXAnimationLengthImportType.FBXALIT_ANIMATED_KEY,
    'convert_scene': True,
    'import_meshes_in_bone_hierarchy': False,
    'import_uniform_scale': 1.0,
    'remove_redundant_keys': False,
    'use_default_sample_rate': True,
}

FBX_IMPORT_UI = {
    'anim_sequence_import_data': None, # Override required
    'automated_import_should_detect_type': False,
    'create_physics_asset': False,
    'import_animations': True, # Override optional
    'import_as_skeletal': True,
    'import_materials': False,
    'import_mesh': True,
    'import_textures': False,
    'mesh_type_to_import': unreal.FBXImportType.FBXIT_SKELETAL_MESH,
    'override_full_name': True,
    'physics_asset': None,
    'skeletal_mesh_import_data': None, # Override required
    'skeleton': None, # Override optional
    'original_import_type': unreal.FBXImportType.FBXIT_ANIMATION,
}

FBX_SKELETAL_MESH_IMPORT_DATA = {
    'convert_scene': True,
    'convert_scene_unit': False,
    'force_front_x_axis': False,
    'import_meshes_in_bone_hierarchy': False,
    'import_morph_targets': True,
    'normal_generation_method': unreal.FBXNormalGenerationMethod.MIKK_T_SPACE,
    'normal_import_method': unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS,
    'preserve_smoothing_groups': 1,
    'threshold_position':  0.00002,
    'threshold_tangent_normal': 0.00002,
    'threshold_uv': 0.000977,
    'update_skeleton_reference_pose': False,
    'use_t0_as_ref_pose': True,
}

FBX_STATIC_MESH_IMPORT_DATA = {
    'combine_meshes': True,
}


def io_asset_import(
    fbx_file_paths: typing.Union[pathlib.Path, str],
    destination_path:  str = '',
    import_animations: bool = True,
    material_override: typing.Union[unreal.MaterialInterface, None] = None,
    replace_existing: bool = True,
    skeleton: typing.Union[unreal.Skeleton, None] = None
) -> list:
    """TODO"""
    def _set_editor_properties(ue_obj: unreal.Object, **prop_kwargs) -> list:
        """TODO"""
        for prop_k, prop_v in prop_kwargs.items():
            ue_obj.set_editor_property(prop_k, prop_v)

        return ue_obj

    destination_path = destination_path or ASSET_IMPORT_TASK['destination_path']
    temp_path = unreal.Paths.combine([ASSET_IMPORT_TASK['destination_path'], '_TEMP'])
    delete_path = unreal.Paths.combine([ASSET_IMPORT_TASK['destination_path'], '_DELETE'])
    imported_assets = []

    for fbx_file_path in fbx_file_paths:

        try:

            #
            fbx_file_path = pathlib.Path(fbx_file_path)
            assert fbx_file_path.suffix == '.fbx' and fbx_file_path.is_file(), \
            f'File either isn\'t an FBX file or doesn\'t exist. \
            Skipping:\n{fbx_file_path.as_posix()}'

            #
            sk_name = f'{UE_NAMING_CONVENTION[unreal.SkeletalMesh]}_{fbx_file_path.stem}'
            live_sk_list = _get_assets_filtered(
                asset_name=sk_name,
                asset_cls=unreal.SkeletalMesh,
                dir_path=destination_path
            )
            live_sk_asset = live_sk_list[0] if live_sk_list else None

            #
            if skeleton:
                live_skel_asset = skeleton
            else:
                live_skel_asset = live_sk_asset.skeleton if live_sk_asset else None

            #
            live_m_assets = live_sk_asset.materials if live_sk_asset is not None else []
            m_slot_names = [m.get_editor_property('material_slot_name') for m in live_m_assets]
            if isinstance(material_override, unreal.MaterialInterface):
                m_interfaces = [material_override] * len(live_m_assets)
            else:
                m_interfaces = [m.get_editor_property('material_interface') for m in live_m_assets]
            live_m_assets = dict(zip(m_slot_names, m_interfaces))
            live_as_assets = _get_assets_filtered(
                asset_cls=unreal.AnimSequence,
                dir_path=destination_path,
                skeleton=live_skel_asset
            )

            #
            fbx_anim_sequence_import_data_props = FBX_ANIM_SEQUENCE_IMPORT_DATA.copy()
            fbx_anim_sequence_import_data = _set_editor_properties(
                unreal.FbxAnimSequenceImportData(),
                **fbx_anim_sequence_import_data_props
            )

            #
            fbx_skeletal_mesh_import_data_props = FBX_SKELETAL_MESH_IMPORT_DATA.copy()
            fbx_skeletal_mesh_import_data = _set_editor_properties(
                unreal.FbxSkeletalMeshImportData(),
                **fbx_skeletal_mesh_import_data_props
            )

            #
            fbx_static_mesh_import_data_props = FBX_STATIC_MESH_IMPORT_DATA.copy()
            fbx_static_mesh_import_data = _set_editor_properties(
                unreal.FbxStaticMeshImportData(),
                **fbx_static_mesh_import_data_props
            )

            #
            fbx_import_ui_props = FBX_IMPORT_UI.copy()
            fbx_import_ui_props['anim_sequence_import_data'] = fbx_anim_sequence_import_data
            fbx_import_ui_props['import_animations'] = import_animations
            fbx_import_ui_props['skeletal_mesh_import_data'] = fbx_skeletal_mesh_import_data
            fbx_import_ui_props['skeleton'] = live_skel_asset
            fbx_import_ui_props['static_mesh_import_data'] = fbx_static_mesh_import_data
            fbx_import_ui = _set_editor_properties(
                unreal.FbxImportUI(),
                **fbx_import_ui_props
            )

            #
            asset_import_task_props = ASSET_IMPORT_TASK.copy()
            asset_import_task_props['destination_name'] = sk_name
            asset_import_task_props['destination_path'] = temp_path
            asset_import_task_props['filename'] = fbx_file_path.as_posix()
            asset_import_task_props['options'] = fbx_import_ui
            asset_import_task_props['replace_existing'] = replace_existing
            asset_import_task = _set_editor_properties(
                unreal.AssetImportTask(),
                **asset_import_task_props
            )

            UE_ASSET_TOOLS.import_asset_tasks([asset_import_task])
            imported_sk_asset = _get_asset(asset_import_task.imported_object_paths[0])
            imported_assets.append(imported_sk_asset)
            unreal.log(f'[MAS UE] Imported {imported_sk_asset.get_name()}')

            # Assign existing materials
            sk_mtl_array = unreal.Array(unreal.SkeletalMaterial)
            for sk_mtl in imported_sk_asset.materials:
                m_interface = live_m_assets.get(sk_mtl.material_slot_name, material_override)
                new_sk_mtl = _set_editor_properties(
                    unreal.SkeletalMaterial(),
                    material_interface=m_interface,
                    material_slot_name=sk_mtl.material_slot_name
                )
                sk_mtl_array.append(new_sk_mtl)
            imported_sk_asset = _set_editor_properties(imported_sk_asset, materials=sk_mtl_array)
            for sk_mi in [sk_mtl.material_interface for sk_mtl in sk_mtl_array]:
                sk_mi_name = sk_mi.get_name() if sk_mi is not None else None
                unreal.log(f'[MAS UE] {sk_mi_name} assigned to {imported_sk_asset.get_name()}')

            # rename imported skeleton
            if live_skel_asset is None:
                skel_name = f'{UE_NAMING_CONVENTION[unreal.Skeleton]}_{fbx_file_path.stem}'
                src_skel_path = _get_base_path(imported_sk_asset.skeleton)
                dst_skel_path = unreal.Paths.combine([temp_path, skel_name])
                unreal.EditorAssetLibrary.rename_asset(
                    source_asset_path=src_skel_path,
                    destination_asset_path=dst_skel_path
                )
                unreal.log(f'[MAS UE] {src_skel_path} renamed to {dst_skel_path}')

            # rename imported animation sequences
            as_assets = _get_assets_filtered(
                asset_cls=unreal.AnimSequence,
                dir_path=temp_path,
                recursive=False
            )
            for as_asset in as_assets:
                _set_editor_properties(as_asset, interpolation=unreal.AnimInterpolationType.STEP)
                as_name = as_asset.get_name().replace(
                    sk_name, UE_NAMING_CONVENTION[unreal.AnimSequence]
                )
                src_as_path = _get_base_path(as_asset)
                dst_as_path = unreal.Paths.combine([temp_path, as_name])
                unreal.EditorAssetLibrary.rename_asset(
                    source_asset_path=src_as_path,
                    destination_asset_path=dst_as_path
                )
                unreal.log(f'[MAS UE] {src_as_path} renamed to {dst_as_path}')

            # Consolidate skeletal mesh
            if live_sk_asset is not None:
                # Move current to temporary folder for deletion later
                del_sk_path = _get_base_path(
                    unreal.Paths.combine([delete_path, live_sk_asset.get_name()])
                )
                unreal.EditorAssetLibrary.rename_asset(
                    source_asset_path=_get_base_path(live_sk_asset),
                    destination_asset_path=del_sk_path
                )
                unreal.EditorAssetLibrary.consolidate_assets(
                    asset_to_consolidate_to=imported_sk_asset,
                    assets_to_consolidate=[live_sk_asset]
                )
                unreal.log(f'[MAS UE] Consolidated {live_sk_asset.get_name()}')

            # Consolidate animation sequences
            live_as_names = [as_asset.get_name() for as_asset in live_as_assets]
            for as_asset in as_assets:
                try:
                    live_as_index = live_as_names.index(as_asset.get_name())
                    if live_as_index >= 0:
                        live_as_asset = live_as_assets[live_as_index]
                        # Move current to temporary folder for deletion later
                        del_as_path = _get_base_path(
                            unreal.Paths.combine([delete_path, live_as_asset.get_name()])
                        )
                        unreal.EditorAssetLibrary.rename_asset(
                            source_asset_path=_get_base_path(live_as_asset),
                            destination_asset_path=del_as_path
                        )
                        unreal.EditorAssetLibrary.consolidate_assets(
                            asset_to_consolidate_to=as_asset,
                            assets_to_consolidate=[live_as_asset]
                        )
                    unreal.log(f'[MAS UE] Consolidated {live_as_asset.get_name()}')
                except ValueError:
                    continue

        except AssertionError as assert_e:

            unreal.log(f'[MAS UE] {assert_e}')
            continue

        except Exception as exception:

            unreal.log(f'[MAS UE] {exception}')
            break

    # Clean up TODO broken
    unreal.EditorAssetLibrary.delete_directory(delete_path)
    # UE_ASSET_REGISTRY.wait_for_completion()
    # ue_asset_paths = unreal.EditorAssetLibrary.list_assets(temp_path)
    # ue_asset_paths = [_get_base_path(path) for path in ue_asset_paths]
    # for ue_asset_path in ue_asset_paths:
    #     ue_asset = _get_asset(ue_asset_path)
    #     dst_folder_path = unreal.Paths.combine([
    #         destination_path, UE_NAMING_CONVENTION[type(ue_asset)]
    #     ])
    #     dst_path = _get_base_path(unreal.Paths.combine([dst_folder_path, ue_asset.get_name()]))
    #     unreal.EditorAssetLibrary.rename_asset(
    #         source_asset_path=ue_asset_path,
    #         destination_asset_path=dst_path
    #     )
    #     unreal.EditorAssetLibrary.save_asset(_get_base_path(ue_asset))
    #     unreal.log(f'[MAS UE] New/updated asset: {dst_path}')
    # unreal.EditorAssetLibrary.delete_directory(temp_path)

    return imported_assets


def _list_props(ue_cls: typing.Type[unreal.Object]):
    """TODO"""
    msg_list = [f'[MAS UE] Editor properties for {ue_cls.__name__}:']
    msg_list.extend([f'[MAS UE] {p}' for p in sorted(dir(ue_cls))])
    unreal.log('\n'.join(msg_list))


def _get_asset(asset_path: str) -> typing.Union[unreal.Object, None]:
    """TODO"""
    asset_path = _get_base_path(asset_path)
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        return unreal.EditorAssetLibrary.load_asset(asset_path)

    return None


def _get_assets_filtered(
    asset_name: str = '.*',
    asset_cls: typing.Type[unreal.Object] = unreal.Object,
    dir_path: str = '/Game/',
    recursive: bool = True,
    **kwargs
) -> list:
    """TODO"""
    ue_asset_paths = unreal.EditorAssetLibrary.list_assets(
        dir_path,
        recursive=recursive,
        include_folder=False
    )
    ue_assets = [_get_asset(ue_asset_path) for ue_asset_path in ue_asset_paths]
    ue_assets = [a for a in ue_assets if isinstance(a, asset_cls)]
    ue_assets = [a for a in ue_assets if re.match(asset_name, a.get_name())]
    for prop_k, prop_v in kwargs.items():
        ue_assets = [a for a in ue_assets if a.get_editor_property(prop_k) == prop_v]

    return ue_assets


def _get_base_path(asset_path: typing.Union[str, unreal.Object]):
    """TODO"""
    if isinstance(asset_path, unreal.Object):
        asset_path = asset_path.get_path_name()
    return unreal.Paths.get_base_filename(asset_path, remove_path=False)


if __name__ == '__main__':

    # def _set_editor_properties(ue_obj: unreal.Object, **prop_kwargs) -> list:
    #     """TODO"""
    #     for prop_k, prop_v in prop_kwargs.items():
    #         ue_obj.set_editor_property(prop_k, prop_v)

    #     return ue_obj

    # ue_assets = _get_assets_filtered(
    #     asset_cls=unreal.AnimSequence,
    #     dir_path='/Game/Characters/LD3D/'
    # )
    # for ue_asset in ue_assets:
    #     _set_editor_properties(ue_asset, interpolation=unreal.AnimInterpolationType.STEP)

    #
    VERSION = 173
    fbx_dir_path = pathlib.Path('/')

    # The default model will be imported with all animation.
    # If a skeletal mesh and animation sequences with the same name exist,
    # they will be overwritten.
    # The skeleton used by the replaced skeletal mesh will be used in this case.
    parent_fbx_file_path = fbx_dir_path.joinpath('LD3D_MASTER_POSE.fbx')
    sk_asset = io_asset_import(
        fbx_file_paths=[parent_fbx_file_path],
        destination_path='/Game/Characters/LD3D/'
    )[0]

    child_fbx_file_paths = fbx_dir_path.glob('*.fbx')
    child_fbx_file_paths = [
        path for path in child_fbx_file_paths if path != parent_fbx_file_path
    ]
    sk_assets = io_asset_import(
        fbx_file_paths=child_fbx_file_paths,
        destination_path='/Game/Characters/LD3D/',
        import_animations=False,
        skeleton=sk_asset.skeleton
    )
