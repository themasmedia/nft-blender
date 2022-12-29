#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - MDL

"""

import bpy


def mdl_set_modifier_display(
    modifier: bpy.types.Modifier,
    visibility: bool = True
) -> None:
    """TODO"""
    modifier.show_in_editmode = visibility
    modifier.show_on_cage = visibility
    modifier.show_render = visibility
    modifier.show_viewport = visibility
