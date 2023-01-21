#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - SCN

"""

import typing

import bpy


def scn_create_and_link_new_scene(
    scene_name: str = '',
    scene_type: str = 'EMPTY',
    objects_to_link: typing.Sequence = ()
) -> bpy.types.Scene:
    """TODO"""
    # Create new scene
    bpy.ops.scene.new(type=scene_type)
    scn = bpy.context.scene
    scn.name = scene_name

    for obj in objects_to_link:
        scn.collection.objects.link(obj)

    return scn


def scn_duplicate_object(
    obj: bpy.types.Object,
    name:str = ''
) -> bpy.types.Object:
    """TODO"""
    scn_select_items(items=[obj])
    bpy.ops.object.duplicate(linked=False)
    dup_obj = bpy.context.object
    if name:
        dup_obj.name = name
    scn_select_items(items=[dup_obj])

    return dup_obj


def scn_get_child_layer_collections(
    root_layer_collection: bpy.types.Collection,
    recursive: bool = False,
) -> list:
    """
    Gets a list of child Collections in the given Collection.

    :param root_layer_collection: The top-level Collection to get child Collection(s) from.
    :param recursive: If True, recursively add child Collections for all Collections.
    :returns: A list of Collections.
    """
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
    type_filter: typing.Sequence = (),
) -> list:
    """
    Gets a list of selected objects in the current Blender Ccene.

    :param type_filter: A sequence of Blender object types.
        Selected objects that do not have types that match those given are omitted.
    :returns: A list of selected objects.
    """
    bpy.ops.object.mode_set(mode='OBJECT')
    sl_objs = bpy.context.selected_objects

    if type_filter:
        sl_objs = [sl_obj for sl_obj in sl_objs if sl_obj.type in type_filter]

    return sl_objs


def scn_get_objects_of_type(
    obj_type: str,
) -> list:
    """
    Gets a list of allo objects of a specific data type in the current Blender Ccene.

    :param obj_type: Name of the data type (i.e. "ARMATURE").
    :returns: A list of objects.
    """
    return [obj for obj in bpy.data.objects if obj.type == obj_type]


def scn_select_items(
    mode: str = 'OBJECT',
    items: list = typing.Iterable
) -> None:
    """TODO"""
    if bpy.context.mode != mode:
        bpy.ops.object.mode_set(mode=mode)
    bpy.ops.object.select_all(action='DESELECT')
    for item in items:
        if isinstance(item, bpy.types.bpy_struct):
            scn_set_all_hidden(item, False)
            item.select_set(True)
            if mode == 'OBJECT':
                bpy.context.view_layer.objects.active = item


def scn_set_all_hidden(
    obj: bpy.types.Object,
    state: bool
) -> None:
    """
    TODO
    """
    obj.hide_viewport = state
    obj.hide_render = state
    obj.hide_set(state)


def scn_set_frame_range(
    frame_start: int = 1,
    frame_end: int = 250,
    frame_step: int = 1,
    frames_per_second: int = 24,
) -> None:
    """
    Sets the start and end frame for the current Scene (for both the timeline and for rendering).

    :param frame_start: The start frame.
    :param frame_end: The end frame.
    :param frame_step: The increment at which to evaluate each frame.
    :param frames_per_second: The number of frames to evaluate per second.
    """
    bpy.context.scene.frame_start = frame_start or bpy.context.scene.frame_start
    bpy.context.scene.frame_end = frame_end or bpy.context.scene.frame_end
    bpy.context.scene.frame_step = frame_step or bpy.context.scene.frame_step
    bpy.context.scene.render.fps = frames_per_second or bpy.context.scene.render.fps

    bpy.context.scene.frame_preview_start = frame_start or bpy.context.scene.frame_start
    bpy.context.scene.frame_preview_end = frame_end or bpy.context.scene.frame_end
    bpy.context.scene.frame_set(frame_start or bpy.context.scene.frame_start)
