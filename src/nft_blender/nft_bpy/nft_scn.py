#!$BLENDER_PATH/python/bin python

import bpy


def scn_get_child_layer_collections(
    root_layer_collection,
    recursive: bool = False,
) -> list:
    """TODO"""
    child_layer_collections = []

    for child_layer_collection in root_layer_collection.children:
        child_layer_collections.append(child_layer_collection)
        if recursive:
            child_layer_collections.extend(
                scn_get_child_layer_collections(
                    child_layer_collection,
                    recursive=recursive,
                )
            )

    return child_layer_collections


def scn_get_selected_objects(
    type_filter: list = []
) -> list:
    """TODO"""
    bpy.ops.object.mode_set(mode='OBJECT')
    sl_objs = bpy.context.selected_objects

    if type_filter:
        [sl_obj for sl_obj in sl_objs if sl_obj.type in type_filter]

    return sl_objs


def scn_set_frame_range(
    frame_start: int = 1,
    frame_end: int = 250,
    frame_step: int = 1,
    frames_per_second: int = 24,
):
    """TODO"""
    bpy.context.scene.frame_start = frame_start or bpy.context.scene.frame_start
    bpy.context.scene.frame_end = frame_end or bpy.context.scene.frame_end
    bpy.context.scene.frame_step = frame_step or bpy.context.scene.frame_step
    bpy.context.scene.render.fps = frames_per_second or bpy.context.scene.render.fps

    bpy.context.scene.frame_preview_start = frame_start or bpy.context.scene.frame_start
    bpy.context.scene.frame_preview_end = frame_end or bpy.context.scene.frame_end
    bpy.context.scene.frame_set(frame_start or bpy.context.scene.frame_start)
