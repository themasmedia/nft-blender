#!$BLENDER_PATH/python/bin python

import getpass
import json
import pathlib
import tempfile
import typing

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


def io_get_blender_app_path() -> pathlib.Path:
    """TODO"""
    return pathlib.Path(bpy.app.binary_path)


def io_get_current_file_path() -> pathlib.Path:
    """TODO"""
    return pathlib.Path(bpy.data.filepath)


def io_get_temp_dir() -> pathlib.Path | None:
    """TODO"""
    return pathlib.Path(tempfile.gettempdir()).resolve()


def io_get_user() -> str:
    """TODO"""
    return getpass.getuser()


def io_load_json_file(file_path: pathlib.Path | str) -> dict:
    """TODO"""
    with pathlib.Path(file_path).open('r', encoding='UTF-8') as readfile:
        json_data = json.load(readfile)

    return json_data


def io_make_dirs(*dir_paths: typing.Iterable[pathlib.Path | str]):
    """TODO"""
    for dir_path in dir_paths:
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def io_save_as(
    file_path: pathlib.Path | str,
    check_existing: bool = False,
):
    """TODO"""
    bpy.ops.wm.save_as_mainfile(
        filepath=pathlib.Path(file_path).as_posix(),
        check_existing=check_existing,
    )
