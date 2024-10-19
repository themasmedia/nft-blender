#

import bpy
import os
import re


def run(
        armature,
        *mesh_objs
    ):
    """"""
    mesh_objs = (mesh_obj for mesh_obj in mesh_objs if mesh_obj.type == 'MESH')

    for mesh_obj in mesh_objs:
        shape_keys = mesh_obj.data.shape_keys.key_blocks if mesh_obj.data.shape_keys is not None else {}

        for shape_key_name, shape_key in shape_keys.items():
            
            # Skip base shape
            index = mesh_obj.data.shape_keys.key_blocks.find(shape_key_name)
            if index < 1:
                continue

            shape_key_driver = shape_key.id_data.animation_data.drivers[index-1].driver
            shape_key_driver.variables[0].targets[0].id = armature

        print(f'Reconnected shape keys for: {mesh_obj}')
    
    return True


if __name__ == '__main__':

    # Select all mesh objects to drive, then armature with one pose bone selected.
    os.system('cls')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    armature = bpy.context.scene.objects.get('rig')
    mesh_objs =  bpy.context.selected_objects

    run(armature, *mesh_objs)
