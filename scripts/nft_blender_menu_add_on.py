#!$BLENDER_PATH/python/bin python


bl_info = {
    'author': 'masangri.eth',
    'blender': (3, 0, 0),
    'category': 'User Interface',
    'description': 'A growing set of tools for Blender that utilize the full scope of Python 3',
    'doc_url': '',
    'location': 'NFT Blender (menu bar)',
    'name': 'NFT Blender Menu Add-On',
    'version': (0, 0, 1),
}

import bpy

from nft_blender.operators import operator_asset, operator_proj, operator_rndr


# import importlib

# for module in (operator_asset, operator_proj, operator_rndr):
#     importlib.reload(module)


class NFTBlenderOperatorPROJ01(bpy.types.Operator):
    """TODO"""
    bl_idname = 'nft.proj_ui_launch_dialog'
    bl_label = 'NFT Project Manager'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        operator_proj.proj_ui_launch_dialog()

        return {'FINISHED'}


class NFTBlenderSubmenuPREPROD(bpy.types.Menu):
    """TODO"""
    bl_label = 'Pre-Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
    #     layout = self.layout
    #     layout.operator(f'nft.example')


class NFTBlenderSubmenuPROD(bpy.types.Menu):
    """TODO"""
    bl_label = 'Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
    #     layout = self.layout
    #     layout.operator(f'nft.')


class NFTBlenderMenu(bpy.types.Menu):
    """TODO"""
    bl_label = 'NFT Blender'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.proj_ui_launch_dialog')
        layout.menu('NFTBlenderSubmenuPREPROD')
        layout.menu('NFTBlenderSubmenuPROD')

    def menu_draw(
        self,
        context: bpy.types.Context,
    ):
        """Menu draw method override."""
        self.layout.menu('NFTBlenderMenu')


classes = (
    NFTBlenderOperatorPROJ01,
    NFTBlenderSubmenuPREPROD,
    NFTBlenderSubmenuPROD,
    NFTBlenderMenu,
)


def register():
    """Register all NFT Blender menu and operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(NFTBlenderMenu.menu_draw)


def unregister():
    """Unregister all NFT Blender menu and operator classes."""
    bpy.types.TOPBAR_MT_editor_menus.remove(NFTBlenderMenu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
