#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Asset

"""

import typing

import bpy

from nft_blender.nft_bpy import bpy_mtl
from nft_blender.nft_bpy import bpy_scn
from nft_blender.nft_qt import qt_ui

# import importlib

# importlib.reload(bpy_mtl)
# importlib.reload(bpy_scn)
# importlib.reload(qt_ui)


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
