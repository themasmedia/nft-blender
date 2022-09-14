#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Asset

"""

import os
import typing

import bpy

from nft_blender.nft_bpy import bpy_mtl
from nft_blender.nft_bpy import bpy_scn
from nft_blender.nft_qt import qt_ui

# from nft_blender.nft_ops import OpsSessionData

import importlib

importlib.reload(bpy_mtl)
importlib.reload(bpy_scn)
importlib.reload(qt_ui)


def asst_set_material_data(mesh_objs: typing.Iterable = ()) -> bool:
    """
    Assigns a Material to specified Mesh object(s) and sets it as the active Material.

    :param mesh_objs: Mesh objects to assign the material to.
        If no objects are given, the selected objects in the scene are used.
    :returns: True if Material data was assigned to at least one Mesh; otherwise False.
    """
    if not mesh_objs:
        mesh_objs = bpy_scn.scn_get_selected_objects(['MESH'])

    mesh_objs = (obj for obj in bpy.data.objects if obj.type == 'MESH')

    if mesh_objs:
        mtl_name = qt_ui.ui_get_item(
            title='Select Material',
            label='Select the Material to assign to the Mesh objects',
            items=[mtl.name for mtl in bpy.data.materials if not mtl.is_grease_pencil],
        )
        return bpy_mtl.mtl_set_material_data(mtl_name, mesh_objs)

    return False


def asst_swap_armature(*modified_objs) -> bool:
    """
    Swaps the Armature modifying a given group of Objects with a new one.

    :param modified_objs: Objects with Armature Modifiers to change.
        If no objects are given, the selected objects in the scene are used.
    :returns: True upon successful modification.
    """
    os.system('cls')

    armature_objs = bpy_scn.scn_get_objects_of_type('ARMATURE')

    armature_obj = qt_ui.ui_get_item(
        title='Select Armature',
        label='Select which armature object will be modify the selected object(s):',
        items=armature_objs,
    )
    if not armature_obj:
        return False

    if not modified_objs:
        modified_objs = bpy_scn.scn_get_selected_objects(['MESH'])

    for modified_obj in modified_objs:

        if isinstance(armature_obj, bpy.types.Object):
            modified_obj.parent = armature_obj
            modified_obj.matrix_parent_inverse = armature_obj.matrix_world.inverted()

        obj_driven_modifiers = [mod for mod in modified_obj.modifiers if mod.type == 'ARMATURE']
        for mod in obj_driven_modifiers:
            mod.object = armature_obj

    return True
