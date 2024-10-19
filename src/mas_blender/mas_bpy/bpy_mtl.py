#!$BLENDER_PATH/python/bin python

"""
MAS Blender - BPY - MTL

"""

import json
import pathlib
import re
import typing

import bpy

from mas_blender.mas_bpy._bpy_core import bpy_scn
from mas_blender.mas_py import py_util


# Load default data from config file.
bpy_mtl_config_file_path = pathlib.Path(__file__).parent.joinpath('bpy_mtl.config.json')
with bpy_mtl_config_file_path.open('r', encoding='UTF-8') as readfile:
    MTL_PBR_PREFS = json.load(readfile)


def mtl_assign_material(
    target_object: bpy.types.Object,
    material_name: str = '',
    set_as_active_material: bool = True
):
    """TODO"""
    mtl_to_assign = bpy.data.materials.get(material_name)
    if mtl_to_assign is None:
        return None

    try:
        if material_name not in target_object.data.materials:
            target_object.data.materials.append(mtl_to_assign)
        if set_as_active_material:
            target_object.material_slots[0].material = mtl_to_assign
            bpy.ops.object.material_slot_remove_unused()
        mtl_slot = target_object.material_slots.get(material_name)
        target_object.active_material_index = mtl_slot.slot_index

    except AttributeError:
        return None


def mtl_get_mtls_from_obj(
    obj: bpy.types.Object,
    active_mtl_only: bool = False,
    in_use_mtls_only: bool = False,
) -> list:
    """"""
    
    if active_mtl_only:
        return [obj.active_material]

    elif in_use_mtls_only:
        mtls = []
        for f in obj.data.polygons:
            f_mtl = obj.material_slots[f.material_index].material
            if f_mtl not in mtls:
                mtls.append(f_mtl)
        return mtls

    else:
        return [mtl_slot.material for mtl_slot in obj.material_slots]


def mtl_remove_unused_material_slots(
    obj: bpy.types.Object
) -> dict:
    """"""

    # 
    in_use_mtls = mtl_get_mtls_from_obj(
        obj=obj,
        in_use_mtls_only=True
    )

    #
    removed_mtl_slots = {}
    for mtl_slot in obj.material_slots:
        mtl = mtl_slot.material
        if mtl not in in_use_mtls:
            removed_mtl_slots[mtl_slot.slot_index] = mtl
            mtl_slot.material = None
    
    # 
    current_sl = bpy_scn.scn_select_items(
        items=[obj]
    )
    bpy.ops.object.material_slot_remove_unused()
    bpy_scn.scn_select_items(
        items=current_sl[0],
        active_obj=current_sl[1]
    )

    return removed_mtl_slots


# def mtl_resize_image_textures(
#     images: typing.Iterable[bpy.types.Image],
#     max_height: int = 2048,
#     max_width: int = 2048,
#     proportional: bool = True
# ) -> list:
#     """TODO depreciate"""
#     resized_images = []

#     for image in images:
#         if (image.size[0] > max_width) or (image.size[1] > max_height):

#             if proportional:
#                 scale_val = max(((image.size[0] / max_width), (image.size[1] / max_height)))
#                 scale_width = int(image.size[0] / scale_val)
#                 scale_height = int(image.size[1] / scale_val)

#             else:
#                 scale_width = int(image.size[0] / (image.size[0] / max_width))
#                 scale_height = int(image.size[1] / (image.size[1] / max_height))

#             image.scale(scale_width, scale_height)
#             resized_images.append(image)

#     return resized_images


def mtl_search_replace_image_dir_paths(
    search_for: str = '',
    replace_with: str = '',
    collection: bpy.types.Collection = None,
) -> list:
    """
    Searches and replaces a substring in the file path for Image nodes.

    :param search_for: Substring to search for.
    :param replace_with: Substring to be used as a replacement.
    :param collection: If a Collection is given,
        only Image nodes for Materials applied to Mesh objects in the Collection are affected.
    :returns: A list of updated Image nodes.
    """
    updated_img_nodes = []

    if collection:
        img_nodes, mtl_list = [], []
        mesh_objs = (obj for obj in collection.all_objects if obj.type == 'MESH')
        for mesh_obj in mesh_objs:
            for mtl in mesh_obj.data.materials:
                if mtl not in mtl_list:
                    for grp in (n for n in mtl.node_tree.nodes if n.type == 'GROUP'):
                        for tex_img in (n for n in grp.node_tree.nodes if n.type == 'TEX_IMAGE'):
                            img_nodes.append(tex_img.image)
                    for tex_img in (n for n in mtl.node_tree.nodes if n.type == 'TEX_IMAGE'):
                        img_nodes.append(tex_img.image)
                mtl_list.append(mtl)

    else:
        img_nodes = bpy.data.images

    re_img_data_pattern = re.compile(
        fr'^.+_(?P<img_data_name>({"|".join(MTL_PBR_PREFS.keys())}))\.(?P<ext>\w+)$'
    )

    for img_node in img_nodes:

        repathed_fp = pathlib.Path(img_node.filepath.replace(search_for, replace_with))
        re_match = re_img_data_pattern.match(repathed_fp.as_posix())

        if re_match:

            img_suffix = re_match.group('img_data_name')
            colorspace_settings = MTL_PBR_PREFS.get(img_suffix)['colorspace_settings']

            repathed_fp_str = '//' + str(repathed_fp).lstrip('\\')
            img_node.filepath = repathed_fp_str
            img_node.colorspace_settings.name = colorspace_settings

            updated_img_nodes.append(img_node)

    return updated_img_nodes


def mtl_set_material_at_index(
    obj: bpy.types.Object,
    mtl_index: int = -1,
    mtl_name: str = '',
    replace_existing: bool = True,
    set_as_active_mtl: bool = True,
) -> bool:
    """
    Sets the active Material for the given Mesh objects.

    :param obj: The affected Object.
    :param mtl_index: The Material Slot index to affect.
    :param mtl_name: The name of the Material to set as the active Material.
    :param replace_existing: Replace the current Material set for the Material Slot.
    :param set_as_active_mtl: Set the affected Material Slot as active.

    :returns: True if the Material was assigned; otherwise False.
    """
    mtl = bpy.data.materials.get(mtl_name)
    if mtl is None:
        return False

    if py_util.util_get_attr_recur(obj, 'data.materials') is None:
        return False

    if mtl_index < 0:
        mtl_index = obj.active_material_index

    bpy_scn.scn_select_items(items=[obj])

    if (not replace_existing) or (len(obj.material_slots) == 0):
        bpy.ops.object.material_slot_add()
        for _ in range(len(obj.material_slots) - mtl_index - 1):
            bpy.ops.object.material_slot_move(direction='UP')
    
    obj.material_slots[mtl_index].material = mtl
    
    if set_as_active_mtl:
        obj.active_material_index = mtl_index

    return True


def mtl_set_material_data(
    mtl_name: str = '',
    mesh_objs: typing.Iterable = (),
) -> bool:
    """
    Sets the active Material for the given Mesh objects.

    :param mtl_name: The name of the Material to set as the active Material.
    :param mesh_objs: The Mesh objects to set.
    :returns: True if Material data was assigned to at least one Mesh; otherwise False.
    """
    mtl = bpy.data.materials.get(mtl_name)
    mtl_assigned = False

    if mtl:
        for mesh_obj in (obj for obj in mesh_objs if obj.type == 'MESH'):
            mesh_obj.active_material = mtl
        mtl_assigned = True

    return mtl_assigned


def mtl_set_material_properties(
    mtls: typing.Iterable[bpy.types.Material],
    props: dict,
) -> None:
    """"""
    for mtl in mtls:
        for prop_k, prop_v in props.items():
            py_util.util_set_attr_recur(mtl, prop_k, prop_v)


def mtl_swap_materials_at_indexes(
    obj: bpy.types.Object,
    index1: int = -1,
    index2: int = -1,
) -> bool:
    """"""
    total_mtl_slots = len(obj.material_slots)
    
    if total_mtl_slots < 2:
        return False
        
    if index1 < 0:
        index1 = obj.active_material_index
    
    if index2 < 0:
        index2 = index1

    index1_mtl = obj.material_slots[index1].material
    index2_mtl = obj.material_slots[index2].material
    
    for index, mtl in ((index1, index2_mtl), (index2, index1_mtl)):
        mtl_set_material_at_index(
            obj,
            mtl_index=index,
            mtl_name=mtl.name,
            set_as_active_mtl=False,
        )

    obj.active_material_index = index1

    return True
