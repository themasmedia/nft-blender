#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Verge3D

"""

import json
import pathlib
import typing

import bpy

from nft_blender.nft_bpy._bpy_core import bpy_ctx, bpy_obj, bpy_scn
from nft_blender.nft_bpy import bpy_mdl
from nft_blender.nft_py import py_util


# Load default data from config file.
ops_v3d_config_file_path = pathlib.Path(__file__).parent.joinpath('ops_v3d.config.json')
with ops_v3d_config_file_path.open('r', encoding='UTF-8') as readfile:
    V3D_CONFIG_DATA = json.load(readfile)


def v3d_edit_custom_props(
    objs: typing.Iterable[bpy.types.Object] = (),
    remove_extra: bool = True,
    update_existing: bool = True,
) -> None:
    """TODO"""
    
    # Iterate through the object(s), and edit custom properties based the Object's data
    for obj in objs:
        obj_data = py_util.util_get_attr_recur(obj, 'data')
        # Renderable Objects.
        if isinstance(obj_data, (bpy.types.Curve, bpy.types.Mesh)):
            obj_prop_data = py_util.util_copy(V3D_CONFIG_DATA['object'])
        # Locators used for annotations and camera aiming/positioning.
        elif obj_data is None:
            obj_prop_data = py_util.util_copy(V3D_CONFIG_DATA['annotation'])
        # Edit custom properties for the Object.
        bpy_scn.scn_edit_custom_props(obj, obj_prop_data, remove_extra, update_existing)
        # Edit custom properties for the Object's Material(s).
        obj_mtls = py_util.util_get_attr_recur(obj, 'data.materials')
        if obj_mtls is not None:
            mtl_prop_data = py_util.util_copy(V3D_CONFIG_DATA['material'])
            for mtl in obj_mtls:
                bpy_scn.scn_edit_custom_props(mtl, mtl_prop_data, remove_extra, update_existing)


def v3d_import_shapefile(
    shapefile_path = pathlib.Path | str,
    elevation_source: str = 'GEOM',
    extrusion_axis: str = 'Z',
    field_elevaction_name: str = '',
    field_extrude_name: str = '',
    field_object_name: str = '',
    object_elevation_name: str = '',
    scaler: float = 1.0,
    separate_objects: bool = False,
    shape_crs: str = ''
) -> bpy.types.Object:
    """"""
    shapefile_path = pathlib.Path(shapefile_path)

    bgis_prefs = bpy_ctx.ctx_get_addon('BlenderGIS-228').preferences
    predef_crs_json = json.loads(bgis_prefs['predefCrsJson'])[0]
    shp_crs = shape_crs or predef_crs_json[bgis_prefs['predefCrs']]

    bpy.ops.importgis.shapefile(
        'INVOKE_DEFAULT',
        filepath=shapefile_path.as_posix(),
        elevSource=elevation_source,
        extrusionAxis=extrusion_axis,
        fieldElevName=field_elevaction_name,
        fieldExtrudeName=field_extrude_name,
        fieldObjName=field_object_name,
        objElevName=object_elevation_name,
        separateObjects=separate_objects,
        shpCRS=shp_crs,
    )

    shp_obj = bpy.context.active_object
    bpy_scn.scn_select_items()

    bpy_mdl.mdl_set_origin(shp_obj)
    shp_obj.scale *= scaler
    bpy_obj.obj_apply_transforms(shp_obj)

    return shp_obj
