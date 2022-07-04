#!$BLENDER_PATH/python/bin python

import os
import pathlib
import re

import bpy

from nft_blender.nft_bpy import nft_io
from nft_blender.nft_bpy import nft_scn
from nft_blender.nft_bpy import nft_ui


def rndr_append_anim_for_render():
    """TODO"""
    os.system('cls')

    anim_file_path = nft_ui.ui_get_file(
        caption='Select File',
        dir='{scenes_dir}/ANIM/published',
        filter='Blend Files (*.blend)'
    )
    if anim_file_path:

        variant_pattern = re.compile('^{proj_name}_ANIM_(?P<variant_name>.+)$')
        variant_name = variant_pattern.match(anim_file_path.stem).group('variant_name')

        # Append ANIM collection
        collection_name = '{proj_name}_CHAR_Base'
        inner_path = 'Collection'
        nft_io.io_append_file(anim_file_path, inner_path, collection_name)

        # Set output range from root bone
        collection = bpy.data.collections.get(collection_name)
        collection_armatures = [obj for obj in collection.all_objects if obj.type == 'ARMATURE']
        for collection_armature in collection_armatures:
            if not collection_armature.hide_render:

                # Root bone variables
                bone_name = 'root'
                bone_name_pattern = re.compile(rf'^pose.bones\["{bone_name}"\].+$')

                frame_start, frame_end = bpy.context.scene.frame_start, bpy.context.scene.frame_end

                # Delete f-curves on root bone
                fcurves = collection_armature.animation_data.action.fcurves
                for fcurve in fcurves:
                    if bone_name_pattern.match(fcurve.data_path):
                        frame_start, frame_end = fcurve.range()
                        collection_armature.animation_data.action.fcurves.remove(fcurve)
                        break

                # Set frame range from transform keyframes on root bone
                nft_scn.scn_set_frame_range(
                    frame_start=int(frame_start),
                    frame_end=int(frame_end),
                )

                # Set root bone to cursor
                if nft_ui.ui_message_box(
                    title='Update Root Location?',
                    text=f'Set the location of "{bone_name}" bone to cursor?',
                    message_box_type='question',
                ):
                    root_bone = collection_armature.pose.bones[bone_name]
                    root_bone.location = bpy.context.scene.cursor.location

        # Save new version file for variant
        rndr_template_file_path = pathlib.Path(bpy.data.filepath)
        rndr_scenes_dir_path = rndr_template_file_path.parent

        rndr_version_dir_path = rndr_scenes_dir_path.joinpath('versions')
        rndr_version_file_name = f'{proj_name}_RNDR_{variant_name}.001{rndr_template_file_path.suffix}'
        rndr_version_file_path = rndr_version_dir_path.joinpath(rndr_version_file_name)
        bpy.ops.wm.save_as_mainfile(filepath=rndr_version_file_path.as_posix())


def rndr_batch_render():
    """TODO"""
    batch_render_dir_path = nft_ui.ui_get_directory(
        caption='Select directory with files to batch render',
        dir='{scenes_dir}/RNDR',
    )
    if batch_render_dir_path.is_dir():
        batch_render_file_paths = [f.as_posix() for f in batch_render_dir_path.glob('*.blend')]

        ui_blender_process = nft_ui.UI_BlenderProcess(blend_files=batch_render_file_paths)
        ui_blender_process.startDetached()


def rndr_update_render_template():
    """TODO"""
    os.system('cls')

    # Get the substring to replace in file name, texture image names, outpuit file names, etc.
    search_for = nft_ui.ui_get_text(
        title='Update Template',
        label='Search for...',
        text='_TEMPLATE'
    )

    prop_texture_dir_path = pathlib.Path(COLLECTION_DATA['PROP']['textures_dir_path'])
    replace_with_list = []
    variant_pattern = re.compile('.*?\-(?P<variant_name>.+)')
    # for variant_dir_path in prop_texture_dir_path.glob('*-[!_]*'):
    for variant_dir_path in prop_texture_dir_path.glob('*-*'):
        variant_match = variant_pattern.match(variant_dir_path.name)
        if variant_match:
            variant_name = variant_match.groupdict().get('variant_name')
            replace_with_list.append(variant_name)
    replace_with_list.sort()
    # Get the replacement substring to use from the variant names of the folders in the prop texture directory
    replace_with = nft_ui.ui_get_item(
        title='Update Template',
        label='Replace with...',
        items=replace_with_list,
    )

    confirm = nft_ui.ui_message_box(
        title='Update Template',
        text=f'{search_for} will be replaced with {replace_with}.\nGood?',
        message_box_type='question',
    )

    if confirm:

        crypto_nodes = [n for n in bpy.context.scene.node_tree.nodes if n.type == 'CRYPTOMATTE_V2']
        # Get the Output File node in the compositing tab
        output_file_nodes = [n for n in bpy.context.scene.node_tree.nodes if n.type == 'OUTPUT_FILE']
        # Get the Render Layer node in the compositing tab
        render_layer_node = next(n for n in bpy.context.scene.node_tree.nodes if n.type == 'R_LAYERS')

        # Get the RNDR scenes directory path
        rndr_template_file_path = pathlib.Path(bpy.data.filepath)
        rndr_scenes_dir_path = rndr_template_file_path.parent
        while rndr_scenes_dir_path.parent.name != 'scenes':
            rndr_scenes_dir_path = rndr_scenes_dir_path.parent

        rndr_blend_file_stem = rndr_template_file_path.stem.split('.')[0]
        rndr_blend_dir_path = rndr_scenes_dir_path.joinpath(replace_with)
        rndr_blend_dir_path.mkdir(parents=True, exist_ok=True)

        for asset_type, collection_data in COLLECTION_DATA.items():

            # Get collection in scene from collection name
            collection = bpy.data.collections.get(collection_data['collection'])

            # Set texture image paths for meshes in the collection that use them
            nft_mtl.mtl_search_replace_image_dir_paths(search_for, replace_with, collection)

            # Set the view layer from collection_data to be renderable,
            # and all others to not be (if more than one exists)
            for scene in bpy.data.scenes:

                view_layers = scene.view_layers if len(scene.view_layers) > 1 else []
                for view_layer in view_layers:

                    # Enable the view layer to be used and rendered
                    if view_layer.name == collection_data['view_layer']:
                        view_layer.use = True
                        bpy.context.window.view_layer = view_layer
                    # Disable it otherwise
                    else:
                        view_layer.use = False

                    root_layer_collections = nft_scn.scn_get_child_layer_collections(view_layer.layer_collection)
                    for root_layer_collection in root_layer_collections:
                        layer_hierarchy_collections = [root_layer_collection]
                        layer_hierarchy_collections.extend(
                            nft_scn.scn_get_child_layer_collections(
                                root_layer_collection,
                                recursive=True,
                            )
                        )

                        for layer_collection in layer_hierarchy_collections:

                            if any((
                                asset_type == 'LGHT',
                                'LGHT' in root_layer_collection.name,
                                root_layer_collection.name == collection_data['collection'],
                            )):
                                holdout, indirect_only = False, False

                            else:
                                holdout = collection_data['secondary']['holdout']
                                indirect_only = collection_data['secondary']['indirect_only']

                            layer_collection.holdout = holdout
                            layer_collection.indirect_only = indirect_only

            # Change view layer in Cryptomatte nodes
            for crypto_node in crypto_nodes:
                crypto_prop = crypto_node.layer_name.split('.')[-1]
                crypto_lyr_name = '.'.join((collection_data['view_layer'], crypto_prop))
                crypto_node.layer_name = crypto_lyr_name

            # Set the View Layer property of the Render Node
            render_layer_node.layer = collection_data['view_layer']

            if collection_data['variants']:

                # Get armatures in collection
                collection_armatures = [obj for obj in collection.all_objects if obj.type == 'ARMATURE']
                for collection_armature in collection_armatures:

                    # If the armature is hidden in the viewport (ensure that just one is visible)
                    if collection_armature.hide_render:
                        continue

                    # Get list of collection variants to set up separate scenes/renders for
                    collection_variant_names = list(collection_data['variants'])

                    #
                    checked_col_variant_names = nft_ui.ui_get_checklist(
                        title=f'Create {asset_type} Variants',
                        text=f'Select the {asset_type} variants to create:',
                        items=collection_variant_names,
                    )

                    # Get the bone to apply variant data to (by default, it should be the one in collection_data)
                    collection_bone_names = [bone.name for bone in collection_armature.pose.bones]
                    collection_bone_names.sort()
                    collection_variant_bone_name = nft_ui.ui_get_item(
                        title='Select Bone',
                        label=f'Select {asset_type} bone with variant properties',
                        items=sorted(collection_bone_names),
                        default_item=collection_data['variant_bone'],
                    )
                    collection_variant_bone = collection_armature.pose.bones[collection_variant_bone_name]

                    # Set properties and save separate file for each variant
                    for col_variant_name, col_variant_data in collection_data['variants'].items():

                        # Skip if that variant name was not selected by the user
                        if col_variant_name not in checked_col_variant_names:
                            continue

                        # Create the base path and slot paths for output files
                        for output_file_node in output_file_nodes:

                            if output_file_node.name in col_variant_data['output_node']:
                                active_output_file_node = output_file_node
                                output_file_node.mute = False
                            else:
                                output_file_node.mute = True

                        default_output_file_base_path = pathlib.Path(active_output_file_node.base_path)
                        output_file_base_path = pathlib.Path(re.sub(search_for, replace_with, str(default_output_file_base_path)))
                        output_file_base_path = output_file_base_path.joinpath(asset_type)
                        active_output_file_node.base_path = str(output_file_base_path)
                        render_layer_node.scene.render.filepath = str(output_file_base_path)

                        # Create list of file slots for active output node
                        default_output_file_slot_paths = [(file_slot, file_slot.path) for file_slot in active_output_file_node.file_slots]
                        output_file_slot_paths = default_output_file_slot_paths[:]

                        #
                        for file_slot, output_file_slot_path in output_file_slot_paths:
                            output_file_slot_path = re.sub('_ASSET', asset_type, output_file_slot_path)
                            output_file_slot_path = re.sub('_VARIANT', col_variant_name, output_file_slot_path)
                            file_slot.path = output_file_slot_path

                        # Set properties of bone from variant data
                        default_variant_data = {}
                        for k, col_v in col_variant_data['props'].items():
                            default_variant_data[k] = collection_variant_bone.get(k)
                            collection_variant_bone[k] = col_v

                        # Save file for variant
                        # Set the name of the asset variant, i.e. CHAR1A
                        variant_blend_file_name = f'{rndr_blend_file_stem}_{asset_type}{col_variant_name}{rndr_template_file_path.suffix}'
                        variant_blend_file_path = rndr_blend_dir_path.joinpath(variant_blend_file_name)
                        #
                        bpy.ops.wm.save_as_mainfile(filepath=variant_blend_file_path.as_posix())

                        # Reset Output File paths
                        for file_slot, default_output_file_slot_path in default_output_file_slot_paths:
                            file_slot.path = default_output_file_slot_path

                        # Reset variant values on bone properties
                        for k, default_v in default_variant_data.items():
                            collection_variant_bone[k] = default_v

                        active_output_file_node.base_path = str(default_output_file_base_path)      

            else:

                # Create the base path and slot paths for output files
                for output_file_node in output_file_nodes:

                    if output_file_node.name in collection_data['output_node']:
                        active_output_file_node = output_file_node
                        output_file_node.mute = False
                    else:
                        output_file_node.mute = True

                default_output_file_base_path = pathlib.Path(active_output_file_node.base_path)
                output_file_base_path = pathlib.Path(re.sub(search_for, replace_with, str(default_output_file_base_path)))
                output_file_base_path = output_file_base_path.joinpath(asset_type)
                active_output_file_node.base_path = str(output_file_base_path)
                render_layer_node.scene.render.filepath = str(output_file_base_path)

                # Create list of file slots for active output node
                default_output_file_slot_paths = [(file_slot, file_slot.path) for file_slot in active_output_file_node.file_slots]
                output_file_slot_paths = default_output_file_slot_paths[:]

                for file_slot, output_file_slot_path in output_file_slot_paths:
                    output_file_slot_path = re.sub('_ASSET', asset_type, output_file_slot_path)
                    file_slot.path = output_file_slot_path

                # Save file for variant
                blend_file_name = f'{rndr_blend_file_stem}_{asset_type}{rndr_template_file_path.suffix}'
                blend_file_path = rndr_blend_dir_path.joinpath(blend_file_name)
                #
                bpy.ops.wm.save_as_mainfile(filepath=blend_file_path.as_posix())

                # Reset Output File paths
                active_output_file_node.base_path = str(default_output_file_base_path)
                for file_slot, default_output_file_slot_path in default_output_file_slot_paths:
                    file_slot.path = default_output_file_slot_path

                for scene in bpy.data.scenes:
                    scene.render.filepath = str(default_output_file_base_path)

            # Revert texture image paths for meshes in the collection that use them
            nft_mtl.mtl_search_replace_image_dir_paths(replace_with, search_for, collection)
        
        # Reopen the original file once all variant files have been created
        bpy.ops.wm.open_mainfile(filepath=rndr_template_file_path.as_posix())
