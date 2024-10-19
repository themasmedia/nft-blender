#

import bpy
import os
import re


def run(
        *pose_bones
    ):
    """"""
    pose_bone_xforms = {}
    
    for pose_bone in pose_bones:

        mirror_match = re.search(r'(\.|_)(L|R)', pose_bone.name)

        if not mirror_match:
            continue

        else:
            repl_str = f'{mirror_match.group(1)}{"L" if mirror_match.group(2) == "R" else "R"}'
            trgt_pose_bone_name = re.sub(r'(\.|_)(L|R)', repl_str, pose_bone.name)
            trgt_pose_bone = pose_bone.id_data.pose.bones.get(trgt_pose_bone_name)

            pose_bone_xforms[trgt_pose_bone] = {
                'location': [pose_bone.location.x * -1, pose_bone.location.y, pose_bone.location.z],
                'rotation_euler': [
                    pose_bone.rotation_euler.x, pose_bone.rotation_euler.y * -1, pose_bone.rotation_euler.z * -1
                ],
                'rotation_mode': pose_bone.rotation_mode,
                'rotation_quaternion': [
                    pose_bone.rotation_quaternion.w, pose_bone.rotation_quaternion.x,
                    pose_bone.rotation_quaternion.y * -1, pose_bone.rotation_quaternion.z * -1
                ],
                'scale': pose_bone.scale
            }

    for trgt_pose_bone, xform_data in pose_bone_xforms.items():

        trgt_pose_bone.location = xform_data['location']
        trgt_pose_bone.rotation_mode = xform_data['rotation_mode']
        if xform_data['rotation_mode'] == 'EULER':
            trgt_pose_bone.rotation_euler = xform_data['rotation_euler']
        elif xform_data['rotation_mode'] == 'QUATERNION':
            trgt_pose_bone.rotation_quaternion = xform_data['rotation_quaternion']
        trgt_pose_bone.scale = xform_data['scale']


    return True
        

if __name__ == '__main__':

    os.system('cls')
    
    if bpy.context.active_object.type == 'ARMATURE':
        
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones = bpy.context.selected_pose_bones
    
        run(*pose_bones)
