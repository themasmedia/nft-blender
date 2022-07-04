#!$BLENDER_PATH/python/bin python

import pathlib
import tempfile

import bpy


def io_append_file(
    blend_file_path: pathlib.Path | str,
    inner_path: str,
    object_name: str,
    autoselect: bool = False,
    link: bool = False,
):
    """TODO"""
    bpy.ops.wm.append(
        filepath=pathlib.Path(blend_file_path, inner_path, object_name).as_posix(),
        directory=pathlib.Path(blend_file_path, inner_path).as_posix(),
        filename=object_name,
        autoselect=autoselect,
        link=link,
    )


def io_get_current_file_path() -> pathlib.Path:
    """TODO"""
    return pathlib.Path(bpy.data.filepath)


def io_get_temp_dir() -> pathlib.Path | None:
    """TODO"""
    return pathlib.Path(tempfile.gettempdir())


def io_save_as(
    file_path: pathlib.Path | str,
    check_existing: bool = False,
):
    """TODO"""
    bpy.ops.wm.save_as_mainfile(
        filepath=pathlib.Path(file_path).as_posix(),
        check_existing=check_existing,
    )
