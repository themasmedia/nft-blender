#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Render

"""

import pathlib
import typing

import bpy

from nft_blender.nft_bpy._bpy_core import bpy_scn
from nft_blender.nft_qt import qt_os, qt_ui

# from nft_blender.nft_ops import OpsSessionData


# class IOExporter(object):
#     """
#     TODO: refactor
#     """

#     def __init__(
#         self,
#         root_export_dir_path: typing.Union[pathlib.Path, str]
#     ):
#         """TODO"""

#     def render_preview_images(
#         self,
#         preview_image_data: dict,
#         export_file_format: str = 'png',
#     ):
#         """TODO"""
#         EXPORT_FILE_FORMAT_DATA = {
#             'png': {
#                 'func': bpy.ops.render.opengl,
#                 'subdir': 'images',
#                 'suffix': '.png',
#             }
#         }
#         active_cam = bpy.context.scene.camera
#         light_objs = bpy_scn.scn_get_objects_of_type('LIGHT')

#         export_function = getattr(bpy.ops.render.opengl, export_file_format)
#         export_file_suffix = EXPORT_FILE_FORMAT_DATA[export_file_format]['suffix']
#         export_subdir_name = EXPORT_FILE_FORMAT_DATA[export_file_format]['subdir']
#         export_dir_path = self.export_dir_path.joinpath(export_subdir_name)
#         export_dir_path.mkdir(parents=True, exist_ok=True)

#         for export_file_name, export_data in preview_image_data.items():
#             objects_to_render = [active_cam]
#             objects_to_render.extend(light_objs)

#             for obj_name, obj_data in export_data['objects'].items():
#                 obj = bpy.data.objects.get(obj_name)
#                 if obj is not None:
#                     bpy_scn.scn_set_all_hidden(obj, False)
#                     objects_to_render.append(obj)

#                     for mdfr_k, mdfr_v in obj_data['Modifiers'].items():
#                         for input_k, input_v in mdfr_v.items():
#                             obj.modifiers[mdfr_k][input_k] = input_v

#                     for shape_k, shape_v in obj_data['ShapeKeys'].items():
#                         # break inputs, if any
#                         shape_key_data_name = obj.active_shape_key.id_data.name
#                         anim_data = bpy.data.shape_keys[shape_key_data_name].animation_data
#                         if anim_data:
#                             action_fcrvs = anim_data.action.fcurves if anim_data.action else []
#                             for _ in action_fcrvs:
#                                 action_fcrvs.remove(action_fcrvs[0])
#                             driver_fcrvs = anim_data.drivers
#                             for _ in driver_fcrvs:
#                                 driver_fcrvs.remove(driver_fcrvs[0])
#                         shape_keys = obj.data.shape_keys.key_blocks
#                         shape_keys[shape_k].value = shape_v

#             self.render_viewport_image(
#                 output_path=export_dir_path.joinpath(f'{export_file_name}{export_file_suffix}'),
#                 objects_to_render=objects_to_render,
#                 render_cam=active_cam
#             )


#     def render_viewport_image(
#         self,
#         output_path: typing.Union[pathlib.Path, str],
#         objects_to_render: typing.Iterable,
#         render_cam: bpy.types.Camera,
#         color_depth: str = '8',
#         color_mode: str = 'RGBA',
#         compression: int = 100,
#         file_format: str = 'PNG',
#         resolution_percentage: int = 100,
#         viewport_shading_type: str = 'MATERIAL'
#     ):
#         """TODO"""
#         #Create temporary preview image render scene
#         scn = bpy_scn.scn_create_and_link_new_scene(
#             objects_to_link=objects_to_render
#         )
#         scn.camera = render_cam

#         screen_spaces = []
#         for area in bpy.context.screen.areas:
#             if area.type == 'VIEW_3D':
#                 for space in area.spaces:
#                     if space.type == 'VIEW_3D':
#                         screen_spaces.append(space)
#         for space in screen_spaces:
#             space.overlay.show_axis_x = False
#             space.overlay.show_axis_y = False
#             space.overlay.show_axis_z = False
#             space.overlay.show_cursor = False
#             space.overlay.show_extras = False
#             space.overlay.show_floor = False
#             space.overlay.show_outline_selected = False
#             space.region_3d.view_perspective = 'CAMERA'
#             space.shading.type = viewport_shading_type

#         #
#         scn.render.image_settings.file_format = file_format
#         scn.render.image_settings.color_mode = color_mode
#         scn.render.image_settings.color_depth = color_depth
#         scn.render.image_settings.compression = compression
#         scn.render.resolution_percentage = resolution_percentage

#         scn.render.filepath = pathlib.Path(output_path).as_posix()

#         bpy.ops.render.opengl(
#             animation=False,
#             render_keyed_only=False,
#             sequencer=False,
#             write_still=True,
#             view_context=True
#         )

#         bpy.ops.scene.delete()


def rndr_render_cameras(
    camera_objs: typing.Iterable[bpy.types.Object],
    fps: typing.Union[float, int, None] = None,
    fps_base: typing.Union[float, int, None] = None,
    frame_start: typing.Union[int, None] = None,
    frame_end: typing.Union[int, None] = None,
    frame_step: typing.Union[int, None] = None,
    opengl: bool = True,
    render: bool = True
) -> None:
    """
    TODO
    cam_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'CAMERA']
    rndr_render_cameras(camera_objs=cam_objs)
    """

    scn = bpy.context.scene
    scn.render.use_file_extension = False

    #
    orig_fps = scn.render.fps
    orig_fps_base = scn.render.fps_base
    orig_frame_start = scn.frame_start
    orig_frame_end = scn.frame_end
    orig_frame_step = scn.frame_step
    orig_output_cam = scn.camera

    scn.frame_start = frame_start if isinstance(frame_start, (float, int)) else orig_frame_start
    scn.frame_end = frame_end if isinstance(frame_end, (float, int)) else orig_frame_end
    scn.frame_step = frame_step if isinstance(frame_step, (float, int)) else orig_frame_step
    scn.render.fps = fps if isinstance(fps, (float, int)) else orig_fps
    scn.render.fps_base = fps_base if isinstance(fps_base, (float, int)) else orig_fps_base

    orig_output_path = pathlib.Path(scn.render.filepath)
    output_dir_path = orig_output_path.parent
    output_file_stem = orig_output_path.stem
    output_file_suffix = orig_output_path.suffix

    #
    screen_spaces = []
    if opengl:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        screen_spaces.append(space)
    for space in screen_spaces:
        space.shading.type = 'MATERIAL'

    #Iterate and render from each camera
    for cam_obj in camera_objs:

        #Set active camera
        scn.camera = cam_obj

        #Switch to camera view for the active camera
        for space in screen_spaces:
            space.region_3d.view_perspective = 'CAMERA'

        #Set the output filename from camera name
        cam_output_filename = f'{output_file_stem}-{cam_obj.name}{output_file_suffix}'
        cam_output_dir_path = output_dir_path.joinpath(pathlib.Path(bpy.data.filepath).stem)
        cam_output_dir_path.mkdir(parents=True, exist_ok=True)

        #Set start frame, end frame based on camera keyframes, if override is not given
        cam_anim_data = cam_obj.animation_data
        if cam_anim_data is not None:
            fcrvs = cam_anim_data.action.fcurves if cam_anim_data.action else []
            if not isinstance(frame_start, (float, int)):
                scn.frame_start = int(min([fcrv.range()[0] for fcrv in fcrvs]))
            if not isinstance(frame_end, (float, int)):
                scn.frame_end = int(max([fcrv.range()[1] for fcrv in fcrvs]))

        if opengl:
            cam_output_path = cam_output_dir_path.joinpath('viewport', cam_output_filename)
            scn.render.filepath = cam_output_path.as_posix()
            bpy.ops.render.opengl(
                animation=True,
                render_keyed_only=False,
                sequencer=False,
                write_still=False,
                view_context=True
            )

        if render:
            subdir_name = bpy.context.scene.render.engine.split('_')[-1].lower()
            cam_output_path = cam_output_dir_path.joinpath(subdir_name, cam_output_filename)
            scn.render.filepath = cam_output_path.as_posix()
            bpy.ops.render.render(
                animation=True,
                write_still=False,
                use_viewport=True,
                # layer='',
                scene=scn.name
            )

    # Reset
    scn.frame_start = orig_frame_start
    scn.frame_end = orig_frame_end
    scn.camera = orig_output_cam
    scn.render.filepath = orig_output_path.as_posix()


def rndr_batch_render() -> None:
    """
    Renders the selected Blender file(s) in a detached local process (not meant for production).
    """
    batch_render_dir_path = qt_ui.ui_get_directory(
        caption='Select directory with files to batch render',
    )
    if batch_render_dir_path.is_dir():
        batch_render_file_paths = [f.as_posix() for f in batch_render_dir_path.glob('*.blend')]

        ui_blender_process = qt_os.OSBlenderProcess(blend_files=batch_render_file_paths)
        ui_blender_process.startDetached()
