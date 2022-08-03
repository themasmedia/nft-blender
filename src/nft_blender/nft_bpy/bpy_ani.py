#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - ANI

"""

import pathlib
import typing

import bpy


class AniKeyingSetHelper(object):
    """
    Helper object for managing Blender Keying Sets for assets in a project.
    """
    def __init__(self, ks_dir_path: typing.Union[pathlib.Path, str]) -> None:
        """
        Constructor method.

        :param ks_dir_path: Path to the Keying Set directory.
        """
        self._ks_root_dir_path = pathlib.Path(ks_dir_path)

    def get_existing_keying_set_names(self) -> list:
        """
        Gets a list of all Keying Set names in the current Scene.

        :returns: A list of Keying Set names.
        """
        existing_keying_sets = bpy.context.scene.keying_sets_all
        existing_keying_set_names = [ks.bl_idname for ks in existing_keying_sets]

        return existing_keying_set_names

    def get_keying_set_names_for_asset(
        self,
        asset_name: str,
        exists_ok: bool = False,
    ) -> list:
        """
        Gets the Keying Set name(s) for the given asset in the current project.

        :param asset_name: The name of the asset.
        :param exists_ok: If False,
            only return Keying Set names that do not exist yet in current Scene (default: False).
        :returns: A list of Keying Set names.
        """
        keying_set_dir_path = self._ks_root_dir_path.joinpath(asset_name)

        if keying_set_dir_path.is_dir():

            keying_set_names = [ks_path.stem for ks_path in keying_set_dir_path.glob('*.py')]

            if not exists_ok:

                existing_keying_set_names = self.get_existing_keying_set_names()

                keying_set_names = [
                    ks for ks in keying_set_names if ks not in existing_keying_set_names
                ]

            keying_set_names.sort()

            return keying_set_names

        return []

    def load_keying_sets_for_asset(
        self,
        asset_name: str,
        ks_name: str,
    ) -> bool:
        """
        Creates a new Keying Set in the current scene from the given asset and Keying Set name.

        :param asset_name: The name of the asset.
        :param ks_name: The name of the Keying Set to load.
        :returns: Success result of creating the new Keying Set.
        """
        existing_ks_names = self.get_existing_keying_set_names()

        if ks_name in existing_ks_names:

            return False

        ks_file_path = self._ks_root_dir_path.joinpath(
            asset_name, ks_name
        ).with_suffix('.py')

        if ks_file_path.is_file():
            # bpy.utils.execfile(ks_file_path.as_posix())
            with ks_file_path.open('r', encoding='utf-8') as ks_rf:
                exec(ks_rf.read())
            bpy.ops.anim.keying_set_active_set(type=ks_name)

            return True

        return False
