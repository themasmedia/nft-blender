#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - IO

"""

import getpass
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
) -> None:
    """
    Appends data from another Blender Scene file into the current Scene.

    :param blend_file_path: The path to the Blender Scene file (.blend).
    :param inner_path: The Blender type of the data.
    :param object_name: The name of the data object to append.
    :param autoselect: Select the appended objects after appended (default: False).
    :param link: If True, link the data to the Scene instead of appending it (default: False).
    """
    bpy.ops.wm.append(
        filepath=pathlib.Path(blend_file_path, inner_path, object_name).as_posix(),
        directory=pathlib.Path(blend_file_path, inner_path).as_posix(),
        filename=object_name,
        autoselect=autoselect,
        link=link,
    )


def io_get_blender_app_path() -> pathlib.Path:
    """
    Gets the installation path to the Blender application running.

    :returns: The installation path.
    """
    return pathlib.Path(bpy.app.binary_path)


def io_get_current_file_path() -> pathlib.Path:
    """
    Gets the file path to the current Blender Scene.

    :returns: The Blender Scene path.
    """
    return pathlib.Path(bpy.data.filepath)


def io_get_temp_dir() -> pathlib.Path | None:
    """
    Gets the systems default path for temporary files and folders.

    :returns: The default temp path.
    """
    return pathlib.Path(tempfile.gettempdir()).resolve() or None


def io_get_user() -> str:
    """
    Gets the user name of the current user.

    :returns: The user name.
    """
    return getpass.getuser()


def io_make_dirs(*dir_paths: typing.Iterable[pathlib.Path | str]) -> None:
    r"""
    Creates directories for all directory paths given.

    :param \*dir_paths: One or more directory paths to create.
    """
    for dir_path in dir_paths:
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def io_save_as(
    file_path: pathlib.Path | str,
    check_existing: bool = False,
) -> None:
    """
    Saves the current Scene to disk at a given location.

    :param file_path: File path location to save to.
    :param check_existing: Prompt the user if the file already exists (default: False).
    """
    bpy.ops.wm.save_as_mainfile(
        filepath=pathlib.Path(file_path).as_posix(),
        check_existing=check_existing,
    )
