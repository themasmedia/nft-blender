#!$BLENDER_PATH/python/bin python

"""NFT Blender - Add-On

Add-on Object can be accessed within Blender via nft_blender.nft_bpy.bpy_ctx.ctx_get_addon().
"""

bl_info = {
    'author': 'masangri.eth',
    'blender': (3, 0, 0),
    'category': 'User Interface',
    'description': 'A growing set of tools for Blender that utilize the full scope of Python 3',
    'doc_url': 'https://masangri.github.io/nft-blender/',
    'location': 'NFT Blender (menu bar)',
    'name': 'NFT Blender',
    'version': (0, 0, 1),
}

import os

import bpy

from nft_blender.nft_ops import ops_asst, ops_proj, ops_rndr


import importlib

for module in (ops_asst, ops_proj, ops_rndr):
    importlib.reload(module)


# OPERATORS

class NFTOperatorPROJ01(bpy.types.Operator):
    """
    Operator for nft_ops.ops_proj.proj_launch_dialog_ui().
    """
    bl_idname = 'nft.proj_launch_dialog_ui'
    bl_label = 'Launch NFT Project Manager'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_proj.proj_launch_dialog_ui()

        return {'FINISHED'}


class NFTOperatorPRE01(bpy.types.Operator):
    """
    Operator for nft_ops.ops_asst.asst_set_material_data().
    """
    bl_idname = 'nft.asst_set_material_data'
    bl_label = 'Set Material Data for Selected Meshes'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_asst.asst_set_material_data()

        return {'FINISHED'}


class NFTOperatorPOST01(bpy.types.Operator):
    """
    Operator for nft_ops.ops_rndr.rndr_batch_render().
    """
    bl_idname = 'nft.rndr_batch_render'
    bl_label = 'Select and Render Blender File(s) Locally.'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_rndr.rndr_batch_render()

        return {'FINISHED'}


# MENUS

class NFT_MT_SubmenuPRE(bpy.types.Menu):
    """
    Pre-production sub-menu.
    """
    bl_label = 'Pre-Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.asst_set_material_data')


class NFT_MT_SubmenuPROD(bpy.types.Menu):
    """
    Production sub-menu.
    """
    bl_label = 'Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""


class NFT_MT_SubmenuPOST(bpy.types.Menu):
    """
    Post-production sub-menu.
    """
    bl_label = 'Post-Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.rndr_batch_render')


class NFT_MT_Menu(bpy.types.Menu):
    """
    NFT Blender Menu.
    """
    bl_label = 'NFT Blender'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.proj_launch_dialog_ui')
        layout.menu('NFT_MT_SubmenuPRE')
        layout.menu('NFT_MT_SubmenuPROD')
        layout.menu('NFT_MT_SubmenuPOST')

    def menu_draw(
        self,
        context: bpy.types.Context,
    ):
        """Menu draw method override."""
        self.layout.menu('NFT_MT_Menu')


classes = (
    NFTOperatorPROJ01,
    NFTOperatorPRE01,
    NFTOperatorPOST01,
    NFT_MT_SubmenuPRE,
    NFT_MT_SubmenuPROD,
    NFT_MT_SubmenuPOST,
    NFT_MT_Menu,
)


# REGISTER ADD-ON

def register():
    """
    Register all NFT Blender menu and operator classes.
    """
    os.system('cls')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(NFT_MT_Menu.menu_draw)


def unregister():
    """
    Unregister all NFT Blender menu and operator classes.
    """
    os.system('cls')
    bpy.types.TOPBAR_MT_editor_menus.remove(NFT_MT_Menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
