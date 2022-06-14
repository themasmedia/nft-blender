#!$BLENDER_PATH/python/bin python

import pathlib

import bpy


KEYING_SET_ROOT_PATH = pathlib.Path('') # TODO


def anim_get_existing_keying_set_names() -> list:
    """"""
    existing_keying_sets = bpy.context.scene.keying_sets_all
    existing_keying_set_names = [ks.bl_idname for ks in existing_keying_sets]

    return existing_keying_set_names


def anim_get_keying_set_names_for_asset(
    asset_name: str,
    exists_ok: bool = False,
) -> list:
    """"""
    keying_set_dir_path = KEYING_SET_ROOT_PATH.joinpath(asset_name)

    if keying_set_dir_path.is_dir():

        keying_set_names = [ks_path.stem for ks_path in keying_set_dir_path.glob('*.py')]

        if not exists_ok:

            existing_keying_set_names = anim_get_existing_keying_set_names()

            keying_set_names = [
                ks for ks in keying_set_names if ks not in existing_keying_set_names
            ]

        keying_set_names.sort()

        return keying_set_names
    
    return []


def anim_load_keying_set_for_asset(
    asset_name: str,
    keying_set_name: str,
) -> bool:
    """"""
    existing_keying_set_names = anim_get_existing_keying_set_names()

    if keying_set_name in existing_keying_set_names:

        return False

    keying_set_file_path = KEYING_SET_ROOT_PATH.joinpath(asset_name, keying_set_name).with_suffix('.py')

    if keying_set_file_path.is_file():
        with keying_set_file_path.open('r') as ks_rf:
            exec(ks_rf.read())
        bpy.ops.anim.keying_set_active_set(type=keying_set_name)

    return True
