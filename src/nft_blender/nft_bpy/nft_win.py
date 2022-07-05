#!$BLENDER_PATH/python/bin python

import bpy


def win_set_workspace(
    workspace_name: str,
):
    """TODO"""
    workspace = bpy.data.workspaces.get(workspace_name) or bpy.context.window.workspace
    bpy.context.window.workspace = workspace
