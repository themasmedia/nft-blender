#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS (Operators)

.. code-block:: python

    # Import NFT Blender - OPS
    from nft_blender.nft_ops import ops_proj

"""

# for ANIM update
# nft_scripts.script_update_asset()
# nft_scripts.script_import_keying_set()

# for RNDR setup
# nft_scripts.script_append_anim_for_render()

# for RNDR
# nft_scripts.script_update_render_template()

# for batch RNDR
# nft_scripts.script_batch_render()

import pathlib
import typing

import sqlalchemy

from nft_blender.nft_db import db_sql


class OpsSessionDataMeta(type):
    """
    Metaclass for OpsSessionData class.
    """
    def __init__(cls, *args, **kwargs):
        """
        Constructor method.
        """
        cls._db_engine = sqlalchemy.engine.base.Engine(None, None, '')
        cls._project = db_sql.DBProject(
            code='',
            name='',
            path=pathlib.Path(),
            pipeline={},
        )

    @property
    def db_engine(cls) -> sqlalchemy.engine.base.Engine:
        """
        Persistent Database Engine property for the Blender session.
        """
        return cls._db_engine

    @db_engine.setter
    def db_engine(cls, db_engine: sqlalchemy.engine.base.Engine):
        """
        Persistent Database Engine setter for the Blender session.
        """
        cls._db_engine = db_engine

    @property
    def project(cls) -> db_sql.DBProject:
        """
        Persistent Database Project property for the Blender session.
        """
        return cls._project

    @project.setter
    def project(cls, project: db_sql.DBProject):
        """
        Persistent Database Project setter for the Blender session.
        """
        cls._project = project


class OpsSessionData(dict, metaclass=OpsSessionDataMeta):
    """
    Global class with persistent class properties available for the duration of the Blender session.
    """
    @classmethod
    def proj_io_pipeline_to_paths(
        cls,
        root_dir_path: typing.Union[pathlib.Path, str],
        project_pipeline: dict,
    ) -> list[pathlib.Path]:
        """
        Creates a list of Paths for all folders in a project.

        :param root_dir_path: The root path of the project.
        :param project_pipeline: Project pipeline heirarchy data.
        :returns: A list of Paths for each folder in the pipeline data.
        """
        root_dir_path = pathlib.Path(root_dir_path)
        project_dir_paths = [root_dir_path]

        for key, val in project_pipeline.items():
            sub_dir_path = root_dir_path.joinpath(key)
            project_dir_paths.extend(cls.proj_io_pipeline_to_paths(sub_dir_path, val))

        return project_dir_paths
