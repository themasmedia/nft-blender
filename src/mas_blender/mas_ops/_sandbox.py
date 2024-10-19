import copy
import pathlib
import typing

import bpy

from mas_blender.mas_bpy import bpy_scn



"""
https://raw.githubusercontent.com/Masangri/vrm-storage/vrm-sw-temp/AVTR_CHAR_ShadowWolf_Main_0109.vrm
https://raw.githubusercontent.com/Masangri/vrm-storage/vrm-sw-temp/AVTR_CHAR_ShadowWolf_4665_0109.vrm
https://raw.githubusercontent.com/Masangri/vrm-storage/vrm-sw-temp/AVTR_CHAR_ShadowWolf_4666_0109.vrm


gm!
Thanks for you patience w/ me in getting back to you.
I've actually gotten a few DMs recently for cool cat-related 3D interest, & am thinking of ways to scale the work & value to more ppl, while also managing budget and time for everyone's sake.
I created a quick survey tht'll help us plan this out, and your input would rly help in creating what we're ultimately trying to create: 💙

https://forms.gle/VFpqxKgRSa8svEhd7


Hey!

Thanks for your patience - busy week, but been reviewing ppl's answers & trying see if I can make this work to get CC holders what they're after.
I feel I badly worded the budget question in the survey (getting non-answers), so I hope you don't mind me reaching out directly to follow up:
1- What would you consider to be a reasonable price for a single 3D asset (in USD and/or ETH)?
2- At what price would you consider it to be prohibitively too expensive?
I ask this so I can plan how many "orders" would be required for a feasible initial run while keeping quality as high as possible (too few would result in prices I'd normally quote to studios with production budgets, likely north of 3.5k+, which might not be a realistic option for individuals).
Not looking to accept every submission, but we likely need at least a couple more similar orders to move forward, so if you know anyone else in the community who would be serious and interested, link to the (revised) form is below.
https://forms.gle/VFpqxKgRSa8svEhd7

Regardless, I'll try to get some look-dev work going soon - got a couple ideas on how to get the CC look we're after, and early feedback is always best.


"""


IO_CONFIG_DATA = {
    "import": {
        "file_formats": {
            ".fbx": "fbx"
        },
        "platforms": {
            "Maya (FBX)": {
                "settings": {
                    "anim_offset": 0.0,
                    "automatic_bone_orientation": False,
                    "axis_forward": "-Z",
                    "axis_up": "Y",
                    "bake_space_transform": False,
                    "colors_type": "NONE",
                    "decal_offset": 0.0,
                    # "directory": "",
                    # "filepath": "",
                    # "files": "",
                    # "filter_glob": "",
                    "force_connect_children": False,
                    "global_scale": 1.0,
                    "ignore_leaf_bones": False,
                    "primary_bone_axis": "Y",
                    "secondary_bone_axis": "X",
                    "use_alpha_decals": False,
                    "use_anim": False,
                    "use_custom_normals": False,
                    "use_custom_props": False,
                    "use_custom_props_enum_as_string": False,
                    "use_image_search": False,
                    "use_manual_orientation": False,
                    "use_prepost_rot": True,
                    "use_subsurf": False,
                    "ui_tab": "MAIN"
                }
            }
        }
    }
}


class IOImporter(object):
    """TODO"""
    def __init__(
        self,
        import_file_path: typing.Union[pathlib.Path, str]
    ):
        """TODO"""
        self.import_file_path = pathlib.Path(import_file_path)

    def import_file(
        self,
        **import_settings
    ) -> list:
        """TODO"""
        import_file_suffix = self.import_file_path.suffix
        import_file_format = IO_CONFIG_DATA['import']['file_formats'][import_file_suffix]
        import_function = getattr(bpy.ops.import_scene, import_file_format)

        import_settings_copy = copy.deepcopy(import_settings)
        import_settings_copy['global_scale'] = bpy.context.scene.unit_settings.scale_length * 100

        import_function(
            filepath=self.import_file_path.as_posix(),
            **import_settings_copy
        )
        imported_objects = bpy.context.selected_objects
        bpy_scn.scn_select_items(items=[])

        for imp_obj in imported_objects:
            imp_obj.rotation_euler = [round(rot, 3) for rot in imp_obj.rotation_euler]

        return imported_objects


def io_import_file():
    """TODO"""
    import_file_path = pathlib.Path('')
    import_platform_name = 'Maya (FBX)'
    import_platform_data = IO_CONFIG_DATA['import']['platforms'][import_platform_name]
    import_settings = import_platform_data['settings']

    

    b3d_importer = IOImporter(
        import_file_path=import_file_path
    )
    b3d_importer.import_file(
        **import_settings
    )
    # prune rotations
    # remove spec on materials

import os
import re
import bpy


def mtl_script():
    os.system('cls')
    edited_mtls = []
    for obj in bpy.context.collection.objects:

        if obj.active_material not in edited_mtls:
            print(obj.name, obj.active_material.name)
            edited_mtls.append(obj.active_material)
            obj.active_material.use_backface_culling = True
            
            for mtl_node in obj.active_material.node_tree.nodes:
                if isinstance(mtl_node, bpy.types.ShaderNodeBsdfPrincipled):
                    mtl_node.inputs.get('Roughness').default_value = 1.0
                    mtl_node.inputs.get('Specular').default_value = 0.0
                elif isinstance(mtl_node, bpy.types.ShaderNodeNormalMap):
                    obj.active_material.node_tree.nodes.remove(mtl_node)
        

def rename_script():
    os.system('cls')
    records = {}
    finder1 = re.compile('^(.+)_(\d{3,4})$')
    finder2 = re.compile('^(.+)_(0\d{3,})$')
    for obj in bpy.context.collection.objects:
        results1 = finder1.match(obj.name)
        if results1:
            if results1.group(1) not in records:
                records[results1.group(1)] = 0
            if int(results1.group(2)) > records[results1.group(1)]:
                records[results1.group(1)] = int(results1.group(2))


    for obj in bpy.context.collection.objects:
        results2 = finder2.match(obj.name)
        if results2:
            if int(results2.group(2)) <= records[results2.group(1)]:
                records[results2.group(1)] += 1
                new_name = f'{results2.group(1)}_{str(records[results2.group(1)]).zfill(3)}'
                obj.name = new_name

mtl_script()


import re

import bpy

def scn_get_objects_of_type(
    obj_type: str,
    col_name: str = '',
) -> list:
    """
    Gets a list of allo objects of a specific data type in the current Blender Ccene.

    :param obj_type: Name of the data type (i.e. "ARMATURE").
    :returns: A list of objects.
    """
    col = bpy.data.collections.get(col_name)
    objs = col.all_objects if col is not None else bpy.data.objects
    return [obj for obj in objs if obj.type == obj_type]


def rename_and_single_uv_map_script():
    """"""
    mesh_objs = scn_get_objects_of_type(
        obj_type='MESH',
        col_name='Imported'
    )
    mesh_obj_tracker = {}
    mesh_obj_name_prefix = 'SM'
    re_finder = re.compile('^(?P<obj_name>[a-zA-Z_\s]+)(\d+)?')
    for mesh_obj in mesh_objs:
        mesh_obj_name_results = re_finder.match(mesh_obj.name)
        if mesh_obj_name_results is None:
            continue
        mesh_obj_name = mesh_obj_name_results.groupdict().get('obj_name')
        mesh_obj_name = re.sub('[_\s]', '', mesh_obj_name)
        mesh_obj_name = f'{mesh_obj_name[0].upper()}{mesh_obj_name[1:]}'
        if mesh_obj_name not in mesh_obj_tracker:
            mesh_obj_tracker[mesh_obj_name] = []
        mesh_obj_tracker[mesh_obj_name].append(mesh_obj)

    for mesh_obj_name, mesh_obj_list in mesh_obj_tracker.items():
        for i, mesh_obj in enumerate(mesh_obj_list, 1):
            new_mesh_obj_name = f'{mesh_obj_name_prefix}_{mesh_obj_name}_{i:03d}'
            mesh_obj.name = new_mesh_obj_name
            if mesh_obj.data != mesh_obj_name:
                mesh_obj.data.name = mesh_obj_name


    for mesh_obj in mesh_objs:
        for uv_lyr in mesh_obj.data.uv_layers:
            if uv_lyr != mesh_obj.data.uv_layers.active:
                mesh_obj.data.uv_layers.remove(uv_lyr)
            else:
                uv_lyr.name = 'UVMap'




import bpy
import mathutils

def pivot_corrector_script_for_instances():

    x_correct = -1.5708
    src_obj = bpy.data.objects.get('Staircase_Step_000')
    target_objs = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')

    for target_obj in target_objs:

        target_name = target_obj.name
        target_location = target_obj.location
        target_rotation = target_obj.rotation_euler
        target_rotation = target_rotation[0] + x_correct, target_rotation[1], target_rotation[2]
        target_rotation = mathutils.Vector(
            [round(rot, 4) for rot in target_rotation]
        )
        target_scale = target_obj.scale * 100
        target_scale = mathutils.Vector(
            [round(sc, 2) for sc in target_scale]
        )
        target_obj.name = '_' + target_name.strip('_')

        dup_obj = src_obj.copy()
        bpy.context.collection.objects.link(dup_obj)

        dup_obj.name = target_name
        dup_obj.location = target_location
        dup_obj.rotation_euler = target_rotation
        dup_obj.scale = target_scale







import json
import typing

import mathutils

import bpy

from mas_blender.mas_bpy import bpy_io


def io_cybr_create_cinematic_splines_data(
    camera_objs: typing.Iterable[bpy.types.Object]
) -> dict:
    """TODO"""
    export_dict={
        'export': []
    }

    for cam_obj in camera_objs:
        anim_data = cam_obj.animation_data
        if anim_data is not None:
            fcrvs = anim_data.action.fcurves if anim_data.action else []
            # anim_start_frame = int(bpy.context.scene.frame_start)
            anim_start_frame = int(min([fcrv.range()[0] for fcrv in fcrvs]))
            # anim_end_frame = int(bpy.context.scene.frame_end-bpy.context.scene.frame_start)
            anim_end_frame = int(max([fcrv.range()[1] for fcrv in fcrvs]))
            anim_frame_step = bpy.context.scene.frame_step
            anim_dict = {
                'distribution': 'exact',
                'duration': anim_end_frame / bpy.context.scene.render.fps,
                'lookat': [],
                'position': [],
            }

            for frame in range(anim_start_frame, anim_end_frame + 1, anim_frame_step):
                bpy.context.scene.frame_set(frame)
                obj_matrix = cam_obj.matrix_world.to_translation()
                anim_dict['position'].append(
                    [obj_matrix.x, obj_matrix.z, -obj_matrix.y]
                )
                # lookat_dir = cam_obj.matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))
                lookat_dir = cam_obj.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
                lookat_point = obj_matrix + lookat_dir
                anim_dict['lookat'].append(
                    [lookat_point.x, lookat_point.z, -lookat_point.y]
                )

            export_dict['export'].append(anim_dict)

    return export_dict

def bone_mapper():
    """
import os

import bpy

os.system('cls')
armature_obj = bpy.context.active_object
if isinstance(armature_obj.data, bpy.types.Armature):
    bone_names = sorted([b.name for b in armature_obj.data.bones])
    for bone in bone_names:
        print(bone)

    """
    name_map = {
        'mixamo-rokoko': {
            'chest': 'Spine1',
            'ear01.L': '',
            'ear01.R': '',
            'ear02.L': '',
            'ear02.R': '',
            'ear03.L': '',
            'ear03.R': '',
            'eye.L': 'LeftEye',
            'eye.R': 'RightEye',
            'foot.L': 'LeftFoot',
            'foot.R': 'RightFoot',
            'hand.L': 'LeftHand',
            'hand.R': 'RightHand',
            'head': 'Head',
            'hips': 'Hips',
            'index_distal.L': '',
            'index_distal.R': '',
            'index_intermediate.L': '',
            'index_intermediate.R': '',
            'index_proximal.L': '',
            'index_proximal.R': '',
            'lower_arm.L': 'LeftForeArm',
            'lower_arm.R': 'RightForeArm',
            'lower_leg.L': 'LeftLeg',
            'lower_leg.R': 'RightLeg',
            'middle_distal.L': '',
            'middle_distal.R': '',
            'middle_intermediate.L': '',
            'middle_intermediate.R': '',
            'middle_proximal.L': '',
            'middle_proximal.R': '',
            'neck': 'Neck',
            'ring_distal.L': '',
            'ring_distal.R': '',
            'ring_intermediate.L': '',
            'ring_intermediate.R': '',
            'ring_proximal.L': '',
            'ring_proximal.R': '',
            'root': None,
            'shoulder.L': 'LeftShoulder',
            'shoulder.R': 'RightShoulder',
            'spine': 'Spine',
            'tail01': '',
            'tail02': '',
            'tail03': '',
            'tail04': '',
            'tail05': '',
            'tail06': '',
            'tail07': '',
            'tail08': '',
            'tail09': '',
            'thumb_distal.L': '',
            'thumb_distal.R': '',
            'thumb_intermediate.L': '',
            'thumb_intermediate.R': '',
            'thumb_proximal.L': '',
            'thumb_proximal.R': '',
            'toes.L': 'LeftToeBase',
            'toes.R': 'RightToeBase',
            'upper_arm.L': 'LeftArm',
            'upper_arm.R': 'RightArm',
            'upper_chest': 'Spine2',
            'upper_leg.L': 'LeftUpLeg',
            'upper_leg.R': 'RightUpLeg',
        },

        'accurig-msquared': {
            'ball_l': 'ball_l',
            'ball_r': 'ball_r',
            'calf_l': 'calf_l',
            'calf_r': 'calf_r',
            'calf_twist_01_l': 'calf_twist_01_l',
            'calf_twist_01_r': 'calf_twist_01_r',
            'cc_base_facialbone': 'face',
            'cc_base_jawroot': 'jaw_01',
            'cc_base_l_bigtoe1': '',
            'cc_base_l_breast': '',
            'cc_base_l_calftwist02': 'calf_twist_02_l',
            'cc_base_l_elbowsharebone': '',
            'cc_base_l_eye': 'eye_l',
            'cc_base_l_forearmtwist01': 'lowerarm_twist_01_l',
            'cc_base_l_indextoe1': '',
            'cc_base_l_kneesharebone': '',
            'cc_base_l_midtoe1': '',
            'cc_base_l_pinkytoe1': '',
            'cc_base_l_ribstwist': '',
            'cc_base_l_ringtoe1': '',
            'cc_base_l_thightwist02': 'thigh_twist_02_l',
            'cc_base_l_toebasesharebone': '',
            'cc_base_l_upperarmtwist02': 'upperarm_twist_01_l',
            'cc_base_necktwist02': '',
            'cc_base_pelvis': '',
            'cc_base_r_bigtoe1': '',
            'cc_base_r_breast': '',
            'cc_base_r_calftwist02': 'calf_twist_02_r',
            'cc_base_r_elbowsharebone': '',
            'cc_base_r_eye': 'eye_r',
            'cc_base_r_forearmtwist01': 'lowerarm_twist_01_r',
            'cc_base_r_indextoe1': '',
            'cc_base_r_kneesharebone': '',
            'cc_base_r_midtoe1': '',
            'cc_base_r_pinkytoe1': '',
            'cc_base_r_ribstwist': '',
            'cc_base_r_ringtoe1': '',
            'cc_base_r_thightwist02': 'thigh_twist_02_r',
            'cc_base_r_toebasesharebone': '',
            'cc_base_r_upperarmtwist02': 'upperarm_twist_01_r',
            'cc_base_teeth01': 'teeth_01',
            'cc_base_teeth02': 'teeth_02',
            'cc_base_tongue01': 'tongue_01',
            'cc_base_tongue02': 'tongue_02',
            'cc_base_tongue03': 'tongue_03',
            'cc_base_upperjaw': 'jaw_02',
            'clavicle_l': 'clavicle_l',
            'clavicle_r': 'clavicle_r',
            'foot_l': 'foot_l',
            'foot_r': 'foot_r',
            'hand_l': 'hand_l',
            'hand_r': 'hand_r',
            'head': 'head',
            'ik_foot_l': 'ik_foot_l',
            'ik_foot_r': 'ik_foot_r',
            'ik_foot_root': 'ik_foot_root',
            'ik_hand_gun': 'ik_hand_gun',
            'ik_hand_l': 'ik_hand_l',
            'ik_hand_r': 'ik_hand_r',
            'ik_hand_root': 'ik_hand_root',
            'index_01_l': '',
            'index_01_r': '',
            'index_02_l': '',
            'index_02_r': '',
            'index_03_l': '',
            'index_03_r': '',
            'lowerarm_l': 'lowerarm_l',
            'lowerarm_r': 'lowerarm_r',
            'lowerarm_twist_01_l': 'lowerarm_twist_02_l',
            'lowerarm_twist_01_r': 'lowerarm_twist_02_r',
            'middle_01_l': '',
            'middle_01_r': '',
            'middle_02_l': '',
            'middle_02_r': '',
            'middle_03_l': '',
            'middle_03_r': '',
            'neck_01': 'neck_01',
            # 'neck_02': 'neck_02',
            'pelvis': 'pelvis',
            'pinky_01_l': '',
            'pinky_01_r': '',
            'pinky_02_l': '',
            'pinky_02_r': '',
            'pinky_03_l': '',
            'pinky_03_r': '',
            'ring_01_l': '',
            'ring_01_r': '',
            'ring_02_l': '',
            'ring_02_r': '',
            'ring_03_l': '',
            'ring_03_r': '',
            'root': 'root',
            'spine_01': 'spine_01',
            'spine_02': 'spine_02',
            'spine_03': 'spine_03',
            # 'spine_04': 'spine_04',
            # 'spine_05': 'spine_05',
            'thigh_l': 'thigh_l',
            'thigh_r': 'thigh_r',
            'thigh_twist_01_l': 'thigh_twist_01_l',
            'thigh_twist_01_r': 'thigh_twist_01_r',
            'thumb_01_l': '',
            'thumb_01_r': '',
            'thumb_02_l': '',
            'thumb_02_r': '',
            'thumb_03_l': '',
            'thumb_03_r': '',
            'upperarm_l': 'upperarm_l',
            'upperarm_r': 'upperarm_r',
            'upperarm_twist_01_l': 'upperarm_twist_01_l',
            'upperarm_twist_01_r': 'upperarm_twist_01_r',
        }
    }

    os.system('cls')
    armature_obj = bpy.context.active_object
    if isinstance(armature_obj.data, bpy.types.Armature):
        map_option = 'accurig-msquared'

        for bone in armature_obj.data.bones:
            new_bone_name = name_map[map_option].get(bone.name)
            if new_bone_name is None:
                print('Delete', bone.name)
            elif not new_bone_name:
                continue
            else:
                print(bone.name, '--->', new_bone_name)


if __name__ == '__main__':
    output_file_path = bpy_io.io_get_current_file_path().with_suffix('.json')
    cam_objs = sorted(bpy.context.selected_objects, key=lambda obj: obj.name)
    cinematic_splines_data = io_cybr_create_cinematic_splines_data(cam_objs)
    with output_file_path.open('w', encoding='UTF-8') as writefile:
        output_data = json.dumps(cinematic_splines_data, indent=2)
        writefile.write(output_data)


# Rename textures in a folder
fp = pathlib.Path(r'D:\Projects\Blender\ShadowWolf3dAvatar\textures')

for f in fp.iterdir():
        new_stem = f.stem.replace('AVTR', 'SW3D')
        new_stem = new_stem.replace('_Custom', '_')
        new_stem = new_stem.replace('_Main_', '_')
        new_stem = new_stem.replace('__', '_')
        if not f.with_stem(new_stem).exists():
                f.rename(f.with_stem(new_stem))



## QGIS

import pathlib
import re

from qgis.core import Qgis, QgsGraduatedSymbolRenderer, QgsProject, QgsSingleSymbolRenderer, QgsVectorFileWriter, QgsVectorLayer
from qgis.utils import iface


export_dir_path = pathlib.Path(QgsProject.instance().readPath('../07_Frentity/shapefiles'))
export_file_suffix = '.shp'

save_vector_options = QgsVectorFileWriter.SaveVectorOptions()
save_vector_options.driverName = 'ESRI Shapefile'
save_vector_options.fileEncoding = 'utf-8'
save_vector_options.includeZ = True
save_vector_options.onlySelectedFeatures = False
save_vector_options.saveMetadata = False
save_vector_options.skipAttributeCreation = True
save_vector_options.symbologyExport = False

lyrs = iface.layerTreeView().selectedLayers() or iface.mapCanvas().layers() or QgsProject.instance().mapLayers().values()

#
for lyr in lyrs:
    #
    if isinstance(lyr, QgsVectorLayer):
        pass
        #
        export_file_lyr = re.sub(r'\W+', '-', lyr.name()).strip('-')
        export_dir_lyr_path = export_dir_path.joinpath(lyr.name())
        export_dir_lyr_path.mkdir(exist_ok=True, parents=True)
        # lyr_uri_decoded = QgsProviderRegistry.instance().decodeUri(lyr.dataProvider().name(), lyr.publicSource())
        #
        if isinstance(lyr.renderer(), QgsSingleSymbolRenderer):
            save_vector_options.onlySelectedFeatures = False
            export_file_name = f'{export_file_lyr}{export_file_suffix}'
            export_file_path = export_dir_lyr_path.joinpath(export_file_name)
            lyr.removeSelection()
            lyr.selectAll()
            QgsVectorFileWriter.writeAsVectorFormatV3(
                lyr,
                export_file_path.as_posix(),
                QgsProject.instance().transformContext(),
                save_vector_options
            )
        #
        elif isinstance(lyr.renderer(), QgsGraduatedSymbolRenderer):

            cls_attr = lyr.renderer().legendClassificationAttribute()
            save_vector_options.onlySelectedFeatures = True
            #
            for i, r in enumerate(lyr.renderer().ranges()):
                lower_val_op = '<' if i > 0 else '<='
                expr = f'({r.lowerValue()}{lower_val_op}"{cls_attr}")and("{cls_attr}"<={r.upperValue()})'
                
                export_file_lbl = re.sub(r'\s+', '', r.label())
                export_file_name = f'{export_file_lyr}_{export_file_lbl}{export_file_suffix}'
                export_file_path = export_dir_lyr_path.joinpath(export_file_name)
                
                features = [feature for feature in lyr.getFeatures(expr)]
                feature_ids = [feature.id() for feature in lyr.getFeatures(expr)]
                #
                if len(feature_ids) > 0:
                    lyr.removeSelection()
                    lyr.selectByIds(feature_ids, Qgis.SelectBehavior.SetSelection)
                    QgsVectorFileWriter.writeAsVectorFormatV3(
                        lyr,
                        export_file_path.as_posix(),
                        QgsProject.instance().transformContext(),
                        save_vector_options
                    )




### RENAMER and TRANSFORM CLEANER

import mathutils
import re
import typing

import bpy

from mas_blender.mas_bpy._bpy_core import bpy_scn


def _apply_transforms(objs, loc=True, rot=True, scale=True, props=False, dup_data=False):
    """"""
    if not isinstance(objs, typing.Iterable):
        objs = [objs]

    bpy_scn.scn_select_items(items=objs)
    bpy.ops.object.transform_apply(
        location=loc,
        rotation=rot,
        scale=scale,
        properties=props,
        isolate_users=dup_data
    )
    bpy_scn.scn_select_items(items=[])


def _generate_name(prefix, descriptor, side=None, iterate_suffix=True, suffix_iterable=1):
    """"""
    new_name = f'{prefix}_{descriptor}_{side}_{suffix_iterable:03d}' if side else f'{prefix}_{descriptor}_{suffix_iterable:03d}'

    if iterate_suffix:
        while bpy.data.objects.get(new_name):
            suffix_iterable += 1
            new_name = f'{prefix}_{descriptor}_{suffix_iterable:03d}'

    return new_name



# Get Mesh Objects to edit.
obj_data = {
    'EMPTY': {
        'inst_objs': {},
        'objs': {},
        'prefix': 'NUL'
    },
    'MESH': {
        'inst_objs': {},
        'objs': {},
        'prefix': 'GEO'
    },
}

# default_loc_vec = mathutils.Vector((0.0, 0.0, 0.0))
# default_scale_vec = mathutils.Vector((1.0, 1.0, 1.0))
uv_map_name = 'UVMap'
re_name_pattern = re.compile(r'^(?P<prefix>[A-Z]{3,4})?_?(?P<descriptor>[A-Za-z1-9]+)_?(?P<side>[L|R])?_?(?P<suffix>\d{3,5})?$')

active_col = bpy.context.view_layer.active_layer_collection

for obj_type, obj_type_data in obj_data.items():
    objs_of_type = bpy_scn.scn_get_objects_of_type(obj_type, active_col.name)
    obj_type_data['objs'] = dict(zip(objs_of_type, [{} for i in range(len(objs_of_type))]))
    obj_type_data['inst_objs'] = bpy_scn.scn_get_instance_objects(list(obj_type_data['objs']))

    # Rename Objects.
    for obj in obj_type_data['objs']:

        #
        re_name_match = re_name_pattern.match(obj.name)

        #
        if re_name_match:
            re_name_dict = re_name_match.groupdict()
            generated_name = _generate_name(
                prefix=re_name_dict['prefix'] or obj_type_data['prefix'],
                descriptor=re_name_dict['descriptor'],
                side=re_name_dict['side'],
                suffix_iterable=int(re_name_dict['suffix']) if re_name_dict['suffix'] else 1
            )

        # Rename based on descriptor
        else:
            descriptor = obj.name.split('_')[0].title()
            generated_name = _generate_name(obj_type_data['prefix'], descriptor)
        
        if obj.name != generated_name:
            obj.name = generated_name

    # Apply Object transform data
    for obj in obj_type_data['objs']:

        #
        if obj.data:
            #
            if obj.data.name not in obj_type_data['inst_objs']:
                _apply_transforms(obj)

        else:
            _apply_transforms(obj)

    # Edit Object data
    for obj in obj_type_data['objs']:

        #
        if obj.data:

            if obj.data.name in obj_type_data['inst_objs']:
                re_name_match = re_name_pattern.match(obj.name)
                re_name_dict = re_name_match.groupdict()
                obj_type_data['inst_objs'].pop(obj.data.name)
                obj.data.name = _generate_name(
                    prefix=re_name_dict['prefix'] or obj_type_data['prefix'],
                    descriptor=re_name_dict['descriptor'],
                    side=re_name_dict['side'],
                    iterate_suffix=False
                )

            #
            elif obj.data.users == 1:
                obj.data.name = obj.name

            # Clean up UV maps.
            if obj.data.uv_layers:
                obj.data.uv_layers.active.name = uv_map_name
                for uv_lyr in obj.data.uv_layers:
                    if not uv_lyr.active:
                        bpy.ops.mesh.uv_texture_remove(uv_layer_index=uv_lyr.index)
            
            # Delete custom properpties
            bpy_scn.scn_remove_custom_properties(obj)




# Lemons

import bpy
import rigify

# Set armatures.
src_arm = bpy.data.armatures['Armature_Unity']
trgt_arm = rigify.utils.rig.get_rigify_target_rig(src_arm)

# Custom shape adjustments.
trgt_arm.pose.bones['butt'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['butt'].custom_shape_scale_xyz = (1.0, 1.0, 1.0)
trgt_arm.pose.bones['butt'].custom_shape_translation = (0.0, 0.15, 0.0)
trgt_arm.pose.bones['chest'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['chest'].custom_shape_scale_xyz = (1.0, 1.0, 1.0)
trgt_arm.pose.bones['chest'].custom_shape_rotation_euler = (0.0, -1.5708, 0.0)
trgt_arm.pose.bones['eye.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['eye.L'].custom_shape_scale_xyz = (0.8, 0.5, 0.8)
trgt_arm.pose.bones['eye.L'].custom_shape_translation = (0.0, 0.25, 0.0)
trgt_arm.pose.bones['eye.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['eye.R'].custom_shape_scale_xyz = (-0.8, 0.5, 0.8)
trgt_arm.pose.bones['eye.R'].custom_shape_translation = (0.0, 0.25, 0.0)
trgt_arm.pose.bones['foot_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_fk.L'].custom_shape_scale_xyz = (1.5, 1.0, 1.5)
trgt_arm.pose.bones['foot_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_fk.R'].custom_shape_scale_xyz = (-1.5, 1.0, 1.5)
trgt_arm.pose.bones['foot_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_heel_ik.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_heel_ik.L'].custom_shape_scale_xyz = (2.0, 2.0, 2.0)
trgt_arm.pose.bones['foot_heel_ik.L'].custom_shape_translation = (0.0, 0.01, 0.0)
trgt_arm.pose.bones['foot_heel_ik.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_heel_ik.R'].custom_shape_scale_xyz = (-2.0, 2.0, 2.0)
trgt_arm.pose.bones['foot_heel_ik.R'].custom_shape_translation = (0.0, 0.01, 0.0)
trgt_arm.pose.bones['foot_ik.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_ik.L'].custom_shape_scale_xyz = (1.5, 1.5, 1.0)
trgt_arm.pose.bones['foot_ik.L'].custom_shape_translation = (0.0, 0.02, 0.0)
trgt_arm.pose.bones['foot_ik.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_ik.R'].custom_shape_scale_xyz = (-1.5, 1.5, 1.0)
trgt_arm.pose.bones['foot_ik.R'].custom_shape_translation = (0.0, 0.02, 0.0)
trgt_arm.pose.bones['foot_spin_ik.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_spin_ik.L'].custom_shape_scale_xyz = (2.0, 2.0, 1.0)
trgt_arm.pose.bones['foot_spin_ik.L'].custom_shape_translation = (0.0, 0.0, 0.01)
trgt_arm.pose.bones['foot_spin_ik.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['foot_spin_ik.R'].custom_shape_scale_xyz = (-2.0, 2.0, 1.0)
trgt_arm.pose.bones['foot_spin_ik.R'].custom_shape_translation = (0.0, 0.0, 0.01)
trgt_arm.pose.bones['hand_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_fk.L'].custom_shape_scale_xyz = (2.5, 2.5, 2.5)
trgt_arm.pose.bones['hand_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_fk.R'].custom_shape_scale_xyz = (-2.5, 2.5, 2.5)
trgt_arm.pose.bones['hand_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_ik.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_ik.L'].custom_shape_scale_xyz = (1.0, 2.5, 2.5)
trgt_arm.pose.bones['hand_ik.L'].custom_shape_translation = (0.0, 0.0, 0.0125)
trgt_arm.pose.bones['hand_ik.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hand_ik.R'].custom_shape_scale_xyz = (-1.0, 2.5, 2.5)
trgt_arm.pose.bones['hand_ik.R'].custom_shape_translation = (0.0, 0.0, 0.0125)
trgt_arm.pose.bones['head'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['head'].custom_shape_scale_xyz = (1.25, 1.0, 1.5)
trgt_arm.pose.bones['head'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['hips'].custom_shape_rotation_euler = (0.0, -1.5708, 0.0)
trgt_arm.pose.bones['hips'].custom_shape_scale_xyz = (2.0, 1.0, 1.0)
trgt_arm.pose.bones['hips'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_arm_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_arm_fk.L'].custom_shape_scale_xyz = (2.0, 1.0, 2.0)
trgt_arm.pose.bones['lower_arm_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_arm_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_arm_fk.R'].custom_shape_scale_xyz = (-2.0, 1.0, 2.0)
trgt_arm.pose.bones['lower_arm_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_leg_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_leg_fk.L'].custom_shape_scale_xyz = (4.0, 1.0, 4.0,)
trgt_arm.pose.bones['lower_leg_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_leg_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['lower_leg_fk.R'].custom_shape_scale_xyz = (-4.0, 1.0, 4.0,)
trgt_arm.pose.bones['lower_leg_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['neck'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['neck'].custom_shape_scale_xyz = (12.0, 1.0, 12.0)
trgt_arm.pose.bones['neck'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['nose'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['nose'].custom_shape_scale_xyz = (0.5, 0.25, 0.25)
trgt_arm.pose.bones['nose'].custom_shape_translation = (0.005, 0.25, 0.0)
trgt_arm.pose.bones['shoulder.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['shoulder.L'].custom_shape_scale_xyz = (5.0, 10.0, 5.0)
trgt_arm.pose.bones['shoulder.L'].custom_shape_translation = (0.0, -0.1, -0.05)
trgt_arm.pose.bones['shoulder.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['shoulder.R'].custom_shape_scale_xyz = (-5.0, 10.0, 5.0)
trgt_arm.pose.bones['shoulder.R'].custom_shape_translation = (0.0, -0.1, -0.05)
trgt_arm.pose.bones['toes_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['toes_fk.L'].custom_shape_scale_xyz = (2.0, 2.0, 2.0)
trgt_arm.pose.bones['toes_fk.L'].custom_shape_translation = (0.0, 0.02, 0.0)
trgt_arm.pose.bones['toes_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['toes_fk.R'].custom_shape_scale_xyz = (-2.0, 2.0, 2.0)
trgt_arm.pose.bones['toes_fk.R'].custom_shape_translation = (0.0, 0.02, 0.0)
trgt_arm.pose.bones['toes_ik.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['toes_ik.L'].custom_shape_scale_xyz = (5.0, 1.0, 2.5)
trgt_arm.pose.bones['toes_ik.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['toes_ik.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['toes_ik.R'].custom_shape_scale_xyz = (-5.0, 1.0, 2.5)
trgt_arm.pose.bones['toes_ik.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['torso'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['torso'].custom_shape_scale_xyz = (1.5, 1.5, 0.6)
trgt_arm.pose.bones['torso'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['tummy'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['tummy'].custom_shape_scale_xyz = (1.0, 1.0, 1.0)
trgt_arm.pose.bones['tummy'].custom_shape_translation = (0.0, 0.15, 0.0)
trgt_arm.pose.bones['upper_arm_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_fk.L'].custom_shape_scale_xyz = (2.0, 1.0, 2.0)
trgt_arm.pose.bones['upper_arm_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_fk.R'].custom_shape_scale_xyz = (-2.0, 1.0, 2.0)
trgt_arm.pose.bones['upper_arm_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_parent.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_parent.L'].custom_shape_scale_xyz = (2.5, 2.5, 2.5)
trgt_arm.pose.bones['upper_arm_parent.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_parent.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_arm_parent.R'].custom_shape_scale_xyz = (-2.5, 2.5, 2.5)
trgt_arm.pose.bones['upper_arm_parent.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_fk.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_fk.L'].custom_shape_scale_xyz = (4.0, 1.0, 4.0,)
trgt_arm.pose.bones['upper_leg_fk.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_fk.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_fk.R'].custom_shape_scale_xyz = (-4.0, 1.0, 4.0,)
trgt_arm.pose.bones['upper_leg_fk.R'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_parent.L'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_parent.L'].custom_shape_scale_xyz = (5.0, 5.0, 5.0)
trgt_arm.pose.bones['upper_leg_parent.L'].custom_shape_translation = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_parent.R'].custom_shape_rotation_euler = (0.0, 0.0, 0.0)
trgt_arm.pose.bones['upper_leg_parent.R'].custom_shape_scale_xyz = (-5.0, 5.0, 5.0)
trgt_arm.pose.bones['upper_leg_parent.R'].custom_shape_translation = (0.0, 0.0, 0.0)

# Set arms to FK.
trgt_arm.pose.bones['upper_arm_parent.L']['IK_FK'] = 1.0
trgt_arm.pose.bones['upper_arm_parent.R']['IK_FK'] = 1.0