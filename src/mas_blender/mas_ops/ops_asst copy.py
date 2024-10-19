#!$BLENDER_PATH/python/bin python

"""
MAS Blender - OPS - Asset

"""

import os
import re

import bpy

from mas_blender.mas_bpy import bpy_ani
from mas_blender.mas_bpy import bpy_io
from mas_blender.mas_qt import qt_ui


COLLECTION_DATA = {
    'CHAR': {
        'blend_file_path': '{assets_dir}}/CHAR/published/{proj_name}_CHAR_Base.blend',
        'bones': {
            'back_attach.001': [{}, {},],
            'bubble.001.L': [{}, {},],
            'bubble.001.R': [{}, {},],
            'bubble.002.R': [{}, {},],
            'butt_attach.001': [{}, {},],
            'chest': [{}, {},],
            'chest_attach.001': [{}, {},],
            'chest_attach.001.L': [{}, {},],
            'chest_attach.001.R': [{}, {},],
            'ear_attach.001.L': [{}, {},],
            'ear_attach.001.R': [{}, {},],
            'eye.001.L': [{}, {},],
            'eye.001.R': [{}, {},],
            'eye.002.L': [{}, {},],
            'eye.002.R': [{}, {},],
            'eye.003.L': [{}, {},],
            'eye.003.R': [{}, {},],
            'eye.004.L': [{}, {},],
            'eye.004.R': [{}, {},],
            'eyebrow.001.L': [{}, {},],
            'eyebrow.001.R': [{}, {},],
            'face.001': [{}, {},],
            'face_attach.001': [{}, {},],
            'finger_index.001.L': [{}, {},],
            'finger_index.001.L.001': [{}, {},],
            'finger_index.001.R': [{}, {},],
            'finger_index.001.R.001': [{}, {},],
            'finger_index.001_master.L': [{}, {},],
            'finger_index.001_master.R': [{}, {},],
            'finger_index.002.L': [{}, {},],
            'finger_index.002.R': [{}, {},],
            'finger_index.003.L': [{}, {},],
            'finger_index.003.R': [{}, {},],
            'finger_middle.001.L': [{}, {},],
            'finger_middle.001.L.001': [{}, {},],
            'finger_middle.001.R': [{}, {},],
            'finger_middle.001.R.001': [{}, {},],
            'finger_middle.001_master.L': [{}, {},],
            'finger_middle.001_master.R': [{}, {},],
            'finger_middle.002.L': [{}, {},],
            'finger_middle.002.R': [{}, {},],
            'finger_middle.003.L': [{}, {},],
            'finger_middle.003.R': [{}, {},],
            'finger_pinky.001.L': [{}, {},],
            'finger_pinky.001.L.001': [{}, {},],
            'finger_pinky.001.R': [{}, {},],
            'finger_pinky.001.R.001': [{}, {},],
            'finger_pinky.001_master.L': [{}, {},],
            'finger_pinky.001_master.R': [{}, {},],
            'finger_pinky.002.L': [{}, {},],
            'finger_pinky.002.R': [{}, {},],
            'finger_pinky.003.L': [{}, {},],
            'finger_pinky.003.R': [{}, {},],
            'finger_thumb.001.L': [{}, {},],
            'finger_thumb.001.R': [{}, {},],
            'finger_thumb.002.L': [{}, {},],
            'finger_thumb.002.R': [{}, {},],
            'foot.001_heel_ik.L': [{}, {},],
            'foot.001_heel_ik.R': [{}, {},],
            'foot.001_ik.L': [{}, {},],
            'foot.001_ik.R': [{}, {},],
            'foot.001_spin_ik.L': [{}, {},],
            'foot.001_spin_ik.R': [{}, {},],
            'foot.001_tweak.L': [{}, {},],
            'foot.001_tweak.R': [{}, {},],
            'hand.001.L': [{}, {},],
            'hand.001.R': [{}, {},],
            'hand_attach.L': [{}, {},],
            'hand_attach.R': [{}, {},],
            'head': [{}, {},],
            'head.002': [{}, {},],
            'head.003': [{}, {},],
            'head.004': [{}, {},],
            'head.005': [{}, {},],
            'head.006': [{}, {},],
            'head.007': [{}, {},],
            'head.008': [{}, {},],
            'head.009': [{}, {},],
            'hips': [{}, {},],
            'legs_offset.001': [{}, {},],
            'mouth.001': [{}, {},],
            'mouth.001.L': [{}, {},],
            'mouth.001.R': [{}, {},],
            'mouth.002': [{}, {},],
            'mouth.002.L': [{}, {},],
            'mouth.002.R': [{}, {},],
            'neck': [{}, {},],
            'palm_thumb.001.L': [{}, {},],
            'palm_thumb.001.L.001': [{}, {},],
            'palm_thumb.001.R': [{}, {},],
            'palm_thumb.001.R.001': [{}, {},],
            'palm_thumb.001_master.L': [{}, {},],
            'palm_thumb.001_master.R': [{}, {},],
            'root': [{}, {},],
            'shin.001_tweak.L': [{}, {},],
            'shin.001_tweak.L.001': [{}, {},],
            'shin.001_tweak.L.002': [{}, {},],
            'shin.001_tweak.L.003': [{}, {},],
            'shin.001_tweak.L.004': [{}, {},],
            'shin.001_tweak.R': [{}, {},],
            'shin.001_tweak.R.001': [{}, {},],
            'shin.001_tweak.R.002': [{}, {},],
            'shin.001_tweak.R.003': [{}, {},],
            'shin.001_tweak.R.004': [{}, {},],
            'spine_fk.001': [{}, {},],
            'spine_fk.002': [{}, {},],
            'spine_fk.003': [{}, {},],
            'thigh.001_ik_target.L': [{}, {},],
            'thigh.001_ik_target.R': [{}, {},],
            'thigh.001_parent.L': [{}, {},],
            'thigh.001_parent.R': [{}, {},],
            'thigh.001_tweak.L': [{}, {},],
            'thigh.001_tweak.L.001': [{}, {},],
            'thigh.001_tweak.L.002': [{}, {},],
            'thigh.001_tweak.L.003': [{}, {},],
            'thigh.001_tweak.L.004': [{}, {},],
            'thigh.001_tweak.R': [{}, {},],
            'thigh.001_tweak.R.001': [{}, {},],
            'thigh.001_tweak.R.002': [{}, {},],
            'thigh.001_tweak.R.003': [{}, {},],
            'thigh.001_tweak.R.004': [{}, {},],
            'toe.001.L': [{}, {},],
            'toe.001.R': [{}, {},],
            'torso': [{}, {},],
            'tweak_head.002': [{}, {},],
            'tweak_head.003': [{}, {},],
            'tweak_head.004': [{}, {},],
            'tweak_head.005': [{}, {},],
            'tweak_head.006': [{}, {},],
            'tweak_head.007': [{}, {},],
            'tweak_head.008': [{}, {},],
            'tweak_head.009': [{}, {},],
            'tweak_head.010': [{}, {},],
            'tweak_neck.001': [{}, {},],
            'tweak_spine.001': [{}, {},],
            'tweak_spine.002': [{}, {},],
            'tweak_spine.003': [{}, {},],
            'tweak_spine.004': [{}, {},],
        },
        'collection': '{proj_name}_CHAR_Base',
        'output_node': 'FileOutput.002',
        'secondary': {
            'holdout': True,
            'indirect_only': False,
        },
        'textures_dir_path': '{textures_dir}/{proj_name}_CHAR_Base',
        'variant_bone': 'root',
        'variants': {
            '1A': {
                'output_node': 'FileOutput.002',
                'props': {
                    '_variant_': 1,
                    '_variant.clr_': 1,                    
                },
            },
            '2A': {
                'output_node': 'FileOutput.002',
                'props': {
                    '_variant_': 2,
                    '_variant.clr_': 1,                    
                },
            },
            '3A': {
                'output_node': 'FileOutput.002',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 1,                    
                },
            },
        },
        'view_layer': 'CHAR_Base_vlyr',
    },
    'LGHT': {
        'blend_file_path': '{assets_dir}}/LGHT/published/{proj_name}_LGHT_Base.blend',
        'bones': {
            'camera_b': [{}, {},],
            'root_camera_b': [{}, {},],
            'root_light_b': [{}, {},],
            'studio_2_fill_light_b': [{}, {},],
            'studio_2_fill_light_b.L': [{}, {},],
            'studio_2_key_light_b': [{}, {},],
            'studio_auto_fill_light_b': [{}, {},],
            'studio_auto_key_light_b': [{}, {},],
            'studio_fill_light_b.L': [{}, {},],
            'studio_fill_light_b.R': [{}, {},],
            'studio_key_light_b': [{}, {},],
            'studio_kick_light_b': [{}, {},],
            'studio_soft_fill_light_b.L': [{}, {},],
            'studio_soft_fill_light_b.R': [{}, {},],
            'studio_soft_key_light_b': [{}, {},],
            'sun_key_light_b': [{}, {},],
            'tracking_b': [{}, {},],
        },
        'collection': '{proj_name}_LGHT_Base',
        'output_node': 'FileOutput.003',
        'secondary': {
            'holdout': True,
            'indirect_only': True,
        },
        'textures_dir_path': '{textures_dir}/HDRI',
        'variant_bone': 'root_light_b',
        'variants': {},
        'view_layer': 'ViewLayer',
    },
    'PROP': {
        'blend_file_path': '{assets_dir}}/PROP/published/{proj_name}_PROP_Platform.blend',
        'bones': {
            'platform.001': [{}, {},],
        },
        'collection': '{proj_name}_PROP_Platform',
        'output_node': 'FileOutput.001',
        'secondary': {
            'holdout': False,
            'indirect_only': True,
        },
        'textures_dir_path': '{textures_dir}/{proj_name}_PROP_Platform',
        'variant_bone': 'platform.001',
        'variants': {
            '1A': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 1,
                    '_variant.clr_': 1,
                },
            },
            '2A': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 2,
                    '_variant.clr_': 1,
                },
            },
            '2B': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 2,
                    '_variant.clr_': 2,
                },
            },
            '2C': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 2,
                    '_variant.clr_': 3,
                },
            },
            '3A': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 1,
                },
            },
            '3B': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 2,
                },
            },
            '3C': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 3,
                },
            },
            '3D': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 4,
                },
            },
            '3E': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 5,
                },
            },
            '3F': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 6,
                },
            },
            '3G': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 7,
                },
            },
            '3H': {
                'output_node': 'FileOutput.001',
                'props': {
                    '_variant_': 3,
                    '_variant.clr_': 8,
                },
            },
        },
        'view_layer': 'PROP_Platform_vlyr',
    },
}


def anim_import_keying_set():
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    os.system('cls')

    collection_data = list(COLLECTION_DATA.items())
    collection_names = [v['collection'] for _, v in collection_data if bpy.data.collections.get(v['collection'])]
    #
    collection_name = qt_ui.ui_get_item(
        title='Load Keying Set',
        label='Select asset to load Keying Set for',
        items=collection_names,
    )
    if not collection_name:
        return

    keying_set_names = bpy_ani.anim_get_keying_set_names_for_asset(
        asset_name=collection_name,
        exists_ok=True,
    )
    keying_set_name = qt_ui.ui_get_item(
        title='Select Keying Set',
        label='Select the Keying Set to import',
        items=keying_set_names,
    )

    if keying_set_name:

        bpy_ani.anim_load_keying_set_for_asset(
            asset_name=collection_name,
            keying_set_name=keying_set_name,
        )

        if qt_ui.ui_message_box(
            title='Set Keyframe',
            text='Set keyframe?',
            message_box_type='question',
        ):

            frame_number = qt_ui.ui_get_int(
                title='Set Keyframe',
                label='Set frame numnber',
                value=0,
                minValue=-bpy.context.window.scene.frame_start,
                maxValue=bpy.context.window.scene.frame_end,
                step=bpy.context.window.scene.frame_step,
            )

            if frame_number is not None:

                bpy.context.scene.frame_set(frame_number)
                bpy.ops.anim.keyframe_insert()

        collection = bpy.data.collections.get(collection_name)
        collection_armatures = [obj for obj in collection.all_objects if obj.type == 'ARMATURE']
        for collection_armature in collection_armatures:
            if not collection_armature.hide_render:

                if qt_ui.ui_message_box(
                    title='Add Modifier',
                    text=f'Add F-Curve Modifier to {collection_name} ({collection_armature.name})?',
                    message_box_type='question',
                ):
                    fcurves = collection_armature.animation_data.action.fcurves
                    for fcurve in fcurves:
                        if len(fcurve.modifiers) == 0:
                            fcurve.modifiers.new('CYCLES')


def asst_append_or_update_collection() -> bool:
    """
    Updates the scene by appending a collection from another Asset file,
    or by appending from a newer version of the Asset file,
    applying animation data from the old version in the scene,
    and purging the old version from the scene. 

    :returns: True on success.
    """
    os.system('cls')

    collection_data = list(COLLECTION_DATA.items())
    collection_name = None
    operation = qt_ui.ui_get_item(
        title='Select Operation',
        label='Update existing asset collection or append new asset to scene?',
        items=['Update', 'Append']
    )

    if operation == 'Append':

        asset_file_path = qt_ui.ui_get_file(
            caption='Select File',
            dir='{assets_dir}}',
            filter='Blend Files (*.blend)'
        )
        if asset_file_path:
            collection_names = [v['collection'] for _, v in collection_data]
            if asset_file_path.stem in collection_names:
                collection_name = asset_file_path.stem

    if operation == 'Update':

        collection_names = [v['collection'] for _, v in collection_data if bpy.data.collections.get(v['collection'])]
        #
        collection_name = qt_ui.ui_get_item(
            title='Update Asset',
            label='Select asset to update',
            items=collection_names,
        )
    
    if not collection_name:
        return

    update_index = collection_names.index(collection_name)
    blend_file_path = collection_data[update_index][-1]['blend_file_path']
    asset_bone_data = collection_data[update_index][-1]['bones']
    inner_path = 'Collection'

    #
    old_char_collection = bpy.data.collections.get(collection_name)

    #
    if old_char_collection:

        collection_armatures = [obj for obj in old_char_collection.all_objects if obj.type == 'ARMATURE']
        for collection_armature in collection_armatures:
            if not collection_armature.hide_render:
                for bone_name in asset_bone_data:
                    asset_bone = collection_armature.pose.bones[bone_name]
                    asset_bone_data[bone_name][0]['location'] = asset_bone.location
                    asset_bone_data[bone_name][0]['rotation_euler'] = asset_bone.rotation_euler
                    asset_bone_data[bone_name][0]['rotation_quaternion'] = asset_bone.rotation_quaternion
                    asset_bone_data[bone_name][0]['scale'] = asset_bone.scale
                    for prop_name, prop_value in asset_bone.items():
                        asset_bone_data[bone_name][1][prop_name] = prop_value

        #
        for child_collection in old_char_collection.children_recursive:
            bpy.data.collections.remove(child_collection)
        bpy.data.collections.remove(old_char_collection)

        #
        # for scene_type_collection in (bpy.data.images, bpy.data.materials, bpy.data.meshes, bpy.data.textures):
        for scene_type_collection in (bpy.data.images,):
            for data_block in scene_type_collection:
                if data_block.users == 0:
                    #
                    if collection_name in data_block.filepath:
                        scene_type_collection.remove(data_block, do_unlink=True)

    bpy_io.io_append_file(blend_file_path, inner_path, collection_name)

    #
    new_char_collection = bpy.data.collections.get(collection_name)

    #
    if operation == 'Update':

        collection_armatures = [obj for obj in new_char_collection.all_objects if obj.type == 'ARMATURE']
        for collection_armature in collection_armatures:
            if not collection_armature.hide_render:

                # TODO hard-coded fix
                if re.match(r'^rig\..+', collection_armature.name):
                    collection_armature.name = 'rig'
                
                for bone_name in asset_bone_data:
                    asset_bone = collection_armature.pose.bones[bone_name]

                    asset_bone.location = asset_bone_data[bone_name][0]['location']
                    asset_bone.rotation_euler = asset_bone_data[bone_name][0]['rotation_euler']
                    asset_bone.rotation_quaternion = asset_bone_data[bone_name][0]['rotation_quaternion']
                    asset_bone.scale  = asset_bone_data[bone_name][0]['scale']
                    for prop_name, prop_value in asset_bone_data[bone_name][1].items():
                        asset_bone[prop_name] = prop_value

        bpy.ops.outliner.orphans_purge(do_recursive=True)
