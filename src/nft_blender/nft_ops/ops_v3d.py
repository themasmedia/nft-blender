#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Verge3D

"""

import copy
import json
import pathlib
import typing

import bpy

from nft_blender.nft_bpy._bpy_core import bpy_scn
from nft_blender.nft_py import py_util


# Load default data from config file.
ops_v3d_config_file_path = pathlib.Path(__file__).parent.joinpath('ops_v3d.config.json')
with ops_v3d_config_file_path.open('r', encoding='UTF-8') as readfile:
    V3D_CONFIG_DATA = json.load(readfile)


def v3d_add_custom_props(
    objs: typing.Iterable[bpy.types.Object] = (),
    remove_extra: bool = True,
    update_existing: bool = True,
) -> None:
    """TODO"""
    
    for obj in objs:

        obj_prop_data = copy.copy(V3D_CONFIG_DATA['object'])
        obj_data = py_util.util_get_attr_recur(obj, 'data')
        if obj_data is None:
            obj_prop_data.update(copy.copy(V3D_CONFIG_DATA['annotation']))
        bpy_scn.scn_edit_custom_props(obj, obj_prop_data, remove_extra, update_existing)
        
        obj_mtls = py_util.util_get_attr_recur(obj, 'data.materials')
        if obj_mtls is not None:
            mtl_prop_data = copy.copy(V3D_CONFIG_DATA['material'])
            for mtl in obj_mtls:
                bpy_scn.scn_edit_custom_props(mtl, mtl_prop_data, remove_extra, update_existing)
