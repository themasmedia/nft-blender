#!$BLENDER_PATH/python/bin python

"""
MAS Blender - PY -  PATH

"""

import pathlib
import typing


def paths_get_contents(
    dir_path: str | pathlib.Path,
    dirs: bool = True,
    files: bool = True,
    recursive: bool = False,
    suffix_filter: typing.Iterable[str] = None
) -> list:
    """
    Returns a list of Path objects for directories and/or files in the given directory.

    Args:
        dir_path (Path): The directory to search.
        dirs (bool, optional): If True, includes directory paths in the output list. Defaults to True.
        files (bool, optional): If True, includes file paths in the output list. Defaults to True.
        recursive (bool, optional): If True, includes all subdirectories recursively. Defaults to False.
        suffix_filter (Tuple[str], optional): A tuple of file suffixes to filter files by. Defaults to None.

    Returns:
        list: A list of Path objects for the requested directories and/or files.
    """
    dir_path = pathlib.Path(dir_path)
    paths = []

    if recursive:
        for path in dir_path.rglob('*'):
            if path.is_dir() and dirs:
                paths.append(path)
            elif path.is_file() and files and (suffix_filter is None or path.suffix in suffix_filter):
                paths.append(path)

    else:
        for path in dir_path.iterdir():
            if path.is_dir() and dirs:
                paths.append(path)
            elif path.is_file() and files and (suffix_filter is None or path.suffix in suffix_filter):
                paths.append(path)

    return paths
