#!$BLENDER_PATH/python/bin python

"""
MAS Blender - BPY - CTX

"""

import bpy


def ctx_get_addon(addon_name: str = '') -> bpy.types.Addon:
    """
    Gets the Addon object with the given add-on name (by default, the MAS Blender add-on is used).
    The add-on must be installed and enabled.
    Useful for accessing persistent variables for the Blender session via Addon.preferences.

    :returns: The matching Addon object.
    """
    if not addon_name:
        addon_name = __package__.split('.', maxsplit=-1)[0] + '_addon'

    return bpy.context.preferences.addons.get(addon_name)


def ctx_set_workspace(
    workspace_name: str = '',
) -> None:
    """
    Sets the workspace in the current window in Blender.

    :param workspace_name: Name of the Blender workspace.
    """
    workspace = bpy.data.workspaces.get(workspace_name) or bpy.context.window.workspace
    bpy.context.window.workspace = workspace
