#

import bpy
import os
import re


def run(
        driver_obj,
        *mesh_objs
    ):
    """"""
    mesh_objs = (mesh_obj for mesh_obj in mesh_objs if mesh_obj.type == 'MESH')
    rna_ui = driver_obj.get('_RNA_UI', {})
    
    for mesh_obj in mesh_objs:
        shape_keys = mesh_obj.data.shape_keys.key_blocks if mesh_obj.data.shape_keys is not None else {}
        anim_data_fcurves = mesh_obj.data.shape_keys.animation_data.drivers if mesh_obj.data.shape_keys.animation_data else []
        driver_names = [anim_data_fcurve.driver.name for anim_data_fcurve in anim_data_fcurves]

        for shape_key_name, shape_key in shape_keys.items():
            
            # Skip base shape
            if mesh_obj.data.shape_keys.key_blocks.find(shape_key_name) < 1:
                continue

            # Add custom property to driver
            driver_obj[shape_key_name] = 0.0
            rna_ui.update({
                shape_key_name: {
                    'max':1.0,
                    'min':0.0,
                    'soft_max':1.0,
                    'soft_min':0.0
                }
            })

            # Add driver to shape key value
            shape_key_driver = shape_key.driver_add('value')
            shape_key_driver.driver.type = 'SCRIPTED'
            shape_key_driver.driver.expression = shape_key_name

            variable = shape_key_driver.driver.variables.new()
            variable.name = shape_key_name
            target = variable.targets[0]
            target.id_type = "OBJECT"
            target.id = driver_obj.id_data
            target.data_path = f'pose.bones["{driver_obj.name}"]["{shape_key_name}"]'

            shape_key_driver.driver.expression = shape_key_name

    driver_obj['_RNA_UI'] = rna_ui

    bpy.ops.object.select_all(action='DESELECT')
    
    armature_obj = driver_obj.id_data
    armature_obj.select_set(True)
    armature_obj.data.bones.active = driver_obj.bone
    bpy.ops.object.mode_set(mode='POSE')

    return True
        

if __name__ == '__main__':

    # Select all mesh objects to drive, then armature with one pose bone selected.
    os.system('cls')
    
    if bpy.context.active_object.type == 'ARMATURE':
        
        bpy.ops.object.mode_set(mode='POSE')
        driver_obj = bpy.context.active_pose_bone
        
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh_objs = bpy.context.selected_objects
    
        run(driver_obj, *mesh_objs)
