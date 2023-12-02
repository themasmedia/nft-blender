#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - MDL

"""

import typing

import bpy

from nft_blender.nft_bpy._bpy_core import bpy_ctx, bpy_scn
from nft_blender.nft_py import py_util


def mdl_add_objects_as_shape_keys(
    trgt_obj: bpy.types.Object,
    src_objs: typing.Iterable[bpy.types.Object],
):
    """ takes an array of objects and adds them as shapekeys to the trgt_obj: bpy.types.Object object """

    bpy_scn.scn_select_items(items=src_objs + [trgt_obj])
    bpy.ops.object.join_shapes()


def mdl_apply_modifier(
    obj: bpy.types.Object,
    mdfr: bpy.types.Modifier,
):
    """ applies a specific modifier """

    bpy_scn.scn_select_items(items=[obj])
    bpy.ops.object.modifier_apply(modifier=mdfr.name)


def mdl_apply_modifiers_to_object(
    obj,
    mdfr_list: typing.Iterable[bpy.types.Modifier],
) -> bpy.types.Object:
    """"""

    if not mdl_has_shape_keys(obj):
        for mdfr in mdfr_list:
            mdl_apply_modifier(obj, mdfr)

        return obj
    
    # Get the Shape Key names.
    shp_key_names = []
    for block in obj.data.shape_keys.key_blocks:
        shp_key_names.append(block.name)

    # create receiving object that will contain all collapsed shapekeys
    obj_copy = bpy_scn.scn_copy_object(obj, times=1, offset=0)[0]
    # bake in the shapekey
    mdl_apply_shape_key(obj_copy, 0)
    # apply the selected modifiers
    for entry in mdfr_list:
        mdl_apply_modifier(obj_copy, entry)
    # get the number of shapekeys on the original mesh
    num_shapes = len(obj.data.shape_keys.key_blocks)

    # create a copy for each blendshape and transfer it to the obj_copy one after the other
    # start the loop at 1 so we skip the base shapekey
    for i in range(1, num_shapes):
        # copy of baseobject / blendshape donor
        blendshape = bpy_scn.scn_copy_object(obj, times=1, offset=0)[0]
        # bake shapekey
        mdl_apply_shape_key(blendshape, i)
        # # apply the selected modifiers
        for entry in mdfr_list:
            mdl_apply_modifier(blendshape, entry)

        # remove all the other modifiers
        # they are not needed the obj_copy object has them
        mdl_remove_modifiers(blendshape)

        # add the copy as a blendshape to the obj_copy
        mdl_add_objects_as_shape_keys(obj_copy, [blendshape])

        # restore the shapekey name
        obj_copy.data.shape_keys.key_blocks[i].name = shp_key_names[i]

        # delete the blendshape donor and its mesh datablock (save memory)
        mesh_data = blendshape.data
        bpy.data.objects.remove(blendshape)
        bpy.data.meshes.remove(mesh_data)

    # delete the original and its mesh data
    orig_name = obj.name
    orig_data = obj.data
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(orig_data)

    # rename the obj_copy
    obj_copy.name = orig_name

    return obj_copy
    
    
def mdl_apply_shape_key(
    obj: bpy.types.Object,
    shp_key_index: int,
):
    """ deletes all shapekeys except the one with the given index """
    shapekeys = obj.data.shape_keys.key_blocks

    # check for valid index
    if shp_key_index < 0 or shp_key_index > len(shapekeys):
        return

    # remove all other shapekeys
    for i in reversed(range(0, len(shapekeys))):
        if i != shp_key_index:
            obj.shape_key_remove(shapekeys[i])

    # remove the chosen one and bake it into the object
    obj.shape_key_remove(shapekeys[0])


def mdl_clear_shape_keys(
    obj: bpy.types.Object,
    vrm_armature: bpy.types.Armature = None,
) -> None:
    """
    Clears all Shapekeys for the given Object. Accounts for VRM Add-On bindings.
    """
    # If an Armature is given and the VRM Add-On is installed, clear bindings.
    if vrm_armature is not None and bpy_ctx.ctx_get_addon(addon_name='VRM_Addon_for_Blender-release'):

        # Assign the VRM Add-On Blendshaoe Proxy data to the shape_key_master variable.
        shape_key_master = py_util.util_get_attr_recur(
            vrm_armature, 'vrm_addon_extension.vrm0.blend_shape_master'
        )

        # Remove all Shape Keys bindings to the VRM Add-On Blendshaoe Proxy data.
        if shape_key_master is not None:
            for shape_key_grp in shape_key_master.blend_shape_groups:
                for bind in shape_key_grp.binds:
                    if bind.mesh.mesh_object_name == obj.name:
                        bind.index = ''
                        bind.mesh.mesh_object_name = ''

    # Clear all Shape Keys from the Mesh Object.
    if obj.data.shape_keys is not None:
        obj.shape_key_clear()


def mdl_get_inputs_from_modifiers(
    obj: bpy.types.Object,
    input_types: tuple = (bpy.types.bpy_struct,),
    mdfrs: typing.Iterable = (),
) -> dict:
    """"""
    inputs = {}
    mdfrs = mdfrs if mdfrs else obj.modifiers

    for mdfr in mdfrs:
        for prop_key, prop_val in mdfr.rna_type.properties.items():
            if isinstance(prop_val, bpy.types.PointerProperty) and prop_val.fixed_type.base is not None:
                input_src = getattr(mdfr, prop_key)
                if isinstance(input_src, input_types):
                    inputs[prop_key] = input_src
    
    return inputs


def mdl_has_shape_keys(obj: bpy.types.Object):
    """"""
    # Check that the Object is not an Empty.
    if obj.data is not None:
        # Check that it has Shape Keys.
        if obj.data.shape_keys is not None:
            return True
    
    return False


def mdl_join_objects(
    objects: typing.Iterable[bpy.types.Object],
    new_name: str = '',
) -> bpy.types.Object:
    """"""
    objects = [obj for obj in objects if obj.data]
    bpy_scn.scn_select_items(items=objects)
    bpy.ops.object.join()
    new_obj = bpy.context.active_object
    new_obj.name = new_name or bpy.context.active_object.name

    return new_obj


def mdl_remove_modifiers(
    obj: bpy.types.Object,
):
    """ removes all modifiers from the object """

    for i in reversed(range(0, len(obj.modifiers))):
        modifier = obj.modifiers[i]
        obj.modifiers.remove(modifier)


def mdl_set_modifier_display(
    modifier: bpy.types.Modifier,
    visibility: bool = True
) -> None:
    """TODO"""
    modifier.show_in_editmode = visibility
    modifier.show_on_cage = visibility
    modifier.show_render = visibility
    modifier.show_viewport = visibility
