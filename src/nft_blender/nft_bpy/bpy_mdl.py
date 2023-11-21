#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - MDL

"""

import typing

import bpy


def mdl_get_inputs_from_modifiers(
    obj: bpy.types.Object,
    input_types: typing.Iterable = (bpy.types.bpy_struct),
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


def mdl_set_modifier_display(
    modifier: bpy.types.Modifier,
    visibility: bool = True
) -> None:
    """TODO"""
    modifier.show_in_editmode = visibility
    modifier.show_on_cage = visibility
    modifier.show_render = visibility
    modifier.show_viewport = visibility
