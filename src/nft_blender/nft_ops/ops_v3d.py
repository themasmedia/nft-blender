#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Verge3D

"""

import json
import pathlib
import typing

import bpy
import idprop

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
        targets = []
        obj_data = py_util.util_get_attr_recur(obj, 'data')
        obj_mtls = py_util.util_get_attr_recur(obj, 'data.materials')
        
        if obj_data is None:
            target_prop_data = V3D_CONFIG_DATA['annotation']
            targets.append(obj)
        
        elif obj_mtls is not None:
            target_prop_data = V3D_CONFIG_DATA['material']
            targets.extend(list(obj_mtls))
            
        for target in targets:

            if remove_extra:
                extra_keys = (
                    k for k in target.keys() if k not in target_prop_data and \
                    not isinstance(target[k], idprop.types.IDPropertyGroup)
                )
                for extra_k in extra_keys:
                    target.pop(extra_k)

            for prop_k, prop_v in target_prop_data.items():
                if prop_k not in target:
                    target[prop_k] = prop_v['default']

                target.id_properties_ensure()  # Make sure the manager is updated
                prop_manager = target.id_properties_ui(prop_k)

                if update_existing:
                    prop_manager.update(**prop_v)

