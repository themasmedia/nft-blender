#!$BLENDER_PATH/python/bin python

import json
import os
import pathlib


def user_get_json_data_file_path(
    root_dir_path: pathlib.Path | str,
) -> pathlib.Path:
    """"""
    root_dir_path = pathlib.Path(root_dir_path)
    json_data_file_path = root_dir_path.joinpath(f'nft_blender_data_{os.getlogin()}.json')

    return json_data_file_path


def user_get_json_data(
    json_data_file_path: pathlib.Path | str,
) -> dict:
    """"""
    json_data = {}
    if json_data_file_path.exists():
        with json_data_file_path.open('r') as json_data_file:
            json_data = json.loads(json_data_file.read())
    
    return json_data


def user_set_json_data(
    json_data_file_path: pathlib.Path | str,
    **kwargs,
) -> pathlib.Path:
    """"""
    json_data = user_get_json_data(json_data_file_path)

    with json_data_file_path.open('w+') as json_data_file:

        json_data.setdefault('username', os.getlogin())

        for k, v in kwargs.items():
            json_data[k] = v

        json_data_file.write(json.dumps(json_data, indent=2))

    return json_data_file_path
