#!$BLENDER_PATH/python/bin python

import getpass
import pathlib

from nft_blender.nft_bpy import nft_io
from nft_blender.nft_db import nft_sql


def proj_run():
    """TODO"""
    project_name = 'NFT_Project'
    project_code = 'NFT'
    project_path = pathlib.Path().resolve().as_posix()
    project_pipeline = {
        'assets': {
            'CHAR': 'characters',
            'LGHT': 'light rigs',
            'PROP': 'props',
        },
        'data': {
            'KSET': 'keying sets',
        },
        'edit': {},
        'models': {
            'FBX': 'fbx',
        },
        'scenes': {
            'ANIM': 'animation',
            'LAYT': 'layout',
            'RNDR': 'render'
        },
        'textures': {
            'HDRI': 'hdri',
            'UV': 'uvs',
        },
    }

    db_url = nft_sql.db_get_url('nft_blender', nft_io.io_get_temp_dir())
    db_engine = nft_sql.db_get_engine(db_url)
    nft_sql.db_create_table(db_engine)

    db_project = nft_sql.DB_Project(
        code=project_code,
        name=project_name,
        path=project_path,
        pipeline=project_pipeline,
    )
    db_user = nft_sql.DB_User(
        name=getpass.getuser(),
    )
    db_user.projects.append(db_project)

    nft_sql.db_upsert(db_engine, 'name', db_project, db_user)
