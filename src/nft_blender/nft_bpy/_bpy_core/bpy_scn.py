#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - SCN

"""

import typing

import bpy
import idprop


def scn_copy_object(
    obj: bpy.types.Object,
    cols: typing.Iterable[bpy.types.Collection] = (),
    times: int = 1,
    offset: float = 0.0
) -> typing.Union[typing.List[bpy.types.Object], bpy.types.Object]:
    """"""

    copied_objs = []
    for i in range(times):
        copy_obj = obj.copy()
        copy_obj.data = obj.data.copy()
        copy_obj.name = f'{obj.name}_{i + 1:04d}'
        copy_obj.location.x += offset * (i + 1)

        #
        cols = cols or obj.users_collection
        for usr_col in cols:
            usr_col.objects.link(copy_obj)
        copied_objs.append(copy_obj)

    return copied_objs if len(copied_objs) > 1 else copied_objs[0]


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
    name: str = '',
    instance: bool = False
) -> bpy.types.Object:
    """TODO"""
    scn_select_items(items=[obj])
    bpy.ops.object.duplicate(linked=False)
    dup_obj = bpy.context.object

    if name:
        dup_obj.name = name

    if instance:
        dup_obj.data = obj.data

    scn_select_items(items=[dup_obj])

    return dup_obj


def scn_edit_custom_props(
    target,
    prop_data: dict = {},
    remove_extra: bool = True,
    update_existing: bool = True,
) -> None:
    """TODO"""
    if remove_extra:
        target_keys = list(target.keys())
        extra_keys = (
            k for k in target_keys if k not in prop_data and \
            not isinstance(target[k], idprop.types.IDPropertyGroup)
        )
        for extra_k in extra_keys:
            target.pop(extra_k)

    for prop_k, prop_v in prop_data.items():
        if prop_k not in target:
            target[prop_k] = prop_v['default']

        target.id_properties_ensure()  # Make sure the manager is updated
        prop_manager = target.id_properties_ui(prop_k)

        if update_existing:
            prop_manager.update(**prop_v)


def scn_get_instance_objects(
    objs: typing.Iterable[bpy.types.Object] = ()
) -> dict:
    """
    Gets all instanced Curve and Mesh Objects in a given an array of Objects (defaults to all Objects in the active view layer).
    """
    obj_data_types = (bpy.types.Curve, bpy.types.Mesh)
    objs = objs or (obj for obj in bpy.context.view_layer.objects if isinstance(obj.data, obj_data_types))
    inst_objs = {}

    for obj in objs:
        scn_select_items(items=[obj])
        bpy.ops.object.select_linked(type='OBDATA')
        if len(bpy.context.selected_objects) > 1 and obj.data.name not in inst_objs:
            inst_objs[obj.data.name] = sorted(bpy.context.selected_objects, key=lambda obj: (len(scn_get_hierarchy(obj)), obj.name))
        scn_select_items(items=[])

    return inst_objs


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


def scn_get_hierarchy(
    obj: bpy.types.Object
) -> typing.Tuple[bpy.types.Object]:
    """
    Generates a key that represents the object's hierarchy position.
    The key is a tuple of parent names, starting from the root parent.
    """
    if obj.parent is None:
        return (obj,)

    #
    else:
        parent_key = scn_get_hierarchy(obj.parent)
        return parent_key + (obj,)


def scn_get_objects_of_type(
    obj_type: str,
    col_name: str = '',
) -> list:
    """
    Gets a list of allo objects of a specific data type in the current Blender Ccene.

    :param obj_type: Name of the data type (i.e. "ARMATURE").
    :returns: A list of objects.
    """
    col = bpy.data.collections.get(col_name)
    objs = col.all_objects if col is not None else bpy.data.objects
    objs_of_type = [obj for obj in objs if obj.type == obj_type]

    return sorted(objs_of_type, key=lambda obj: (len(scn_get_hierarchy(obj)), obj.name))


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


def scn_get_view_layer_collections(
    view_lyr: bpy.types.ViewLayer,
    recursive = True,
):
    """TODO transition into this function from scn_get_child_layer_collections"""
    def _get_children(root_lyr_col):
        """"""
        lyr_cols = []
        for lyr_col in root_lyr_col.children:
            lyr_cols.append(lyr_col)
            if recursive:
                lyr_cols.extend(_get_children(lyr_col))
        return lyr_cols
    
    view_lyr_cols = _get_children(view_lyr.layer_collection)

    return view_lyr_cols


def scn_link_objects_to_collection(
    col: bpy.types.Collection,
    objs: typing.Iterable[bpy.types.Object],
    exclusive: bool = False,
) -> None:
    """
    Links the given Object(s) to the given Collection.
    """
    # Iterate through the Objects
    for obj in objs:

        # Link the Object to the given Collection.
        if obj.name not in col.objects:
            col.objects.link(obj)

        # If exclusive, unlink the Object from other Collections, if necessary.
        if exclusive:
            usr_cols = [usr_col for usr_col in obj.users_collection if usr_col != col]
            for usr_col in usr_cols:
                if obj.name in usr_col.objects:
                    usr_col.objects.unlink(obj)


def scn_select_items(
    items: typing.Iterable = (),
    active_obj: bpy.types.Object = None,
    mode: str = 'OBJECT'
) -> typing.Tuple[list, bpy.types.Object]:
    """TODO Last item in items will be set as the active item."""
    _active_obj = bpy.context.active_object
    _selected_objs = bpy.context.selected_objects

    if bpy.context.mode != mode:
        bpy.ops.object.mode_set(mode=mode)
    bpy.ops.object.select_all(action='DESELECT')

    for item in items:
        if isinstance(item, bpy.types.bpy_struct):
            scn_set_all_hidden(item, False)
            item.select_set(True)
            if mode == 'OBJECT':
                bpy.context.view_layer.objects.active = item
    
    if active_obj and mode == 'OBJECT':
        bpy.context.view_layer.objects.active = active_obj
    
    return (_selected_objs, _active_obj)


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
