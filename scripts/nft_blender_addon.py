#!$BLENDER_PATH/python/bin python

"""NFT Blender - Add-On

Add-on Object can be accessed with ctx_get_addon() function in nft_blender.nft_bpy.bpy_ctx.
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

import bpy

from nft_blender.nft_ops import ops_asst, ops_proj, ops_rndr


import importlib

for module in (ops_asst, ops_proj, ops_rndr):
    importlib.reload(module)


# PREFERENCES

class NFTAddonPrefs(bpy.types.AddonPreferences):
    """"""
    bl_idname = __name__

    db_connected: bpy.props.BoolProperty(
        default=False,
        name='Database connection status',
    )

    proj_code: bpy.props.StringProperty(
        default='',
        name='Short-hand code for the current project',
    )

    proj_name: bpy.props.StringProperty(
        default='',
        name='Name of the current project',
    )

    proj_path: bpy.props.StringProperty(
        default='',
        name='Root file path for the current project',
        subtype='DIR_PATH',
    )

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.label(text='This is a preferences view for our add-on')
        layout.prop(self, 'db_connected')
        layout.prop(self, 'proj_code')
        layout.prop(self, 'proj_name')
        layout.prop(self, 'proj_path')


# OPERATORS

class NFTOperatorPROJ01(bpy.types.Operator):
    """TODO"""
    bl_idname = 'nft.proj_launch_dialog_ui'
    bl_label = 'NFT Project Manager'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_proj.proj_launch_dialog_ui()

        return {'FINISHED'}


class NFTOperatorPRE01(bpy.types.Operator):
    """TODO"""
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
    """TODO"""
    bl_idname = 'nft.rndr_batch_render'
    bl_label = 'NFT Project Manager'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_rndr.rndr_batch_render()

        return {'FINISHED'}


# MENUS

class NFTSubmenuPRE(bpy.types.Menu):
    """TODO"""
    bl_label = 'Pre-Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.asst_set_material_data')


class NFTSubmenuPROD(bpy.types.Menu):
    """TODO"""
    bl_label = 'Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
    #     layout = self.layout
    #     layout.operator(f'nft.')


class NFTSubmenuPOST(bpy.types.Menu):
    """TODO"""
    bl_label = 'Post-Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.rndr_batch_render')


class NFTMenu(bpy.types.Menu):
    """TODO"""
    bl_label = 'NFT Blender'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('nft.proj_launch_dialog_ui')
        layout.menu('NFTSubmenuPRE')
        layout.menu('NFTSubmenuPROD')
        layout.menu('NFTSubmenuPOST')

    def menu_draw(
        self,
        context: bpy.types.Context,
    ):
        """Menu draw method override."""
        self.layout.menu('NFTMenu')


classes = (
    NFTAddonPrefs,
    NFTOperatorPROJ01,
    NFTOperatorPRE01,
    NFTOperatorPOST01,
    NFTSubmenuPRE,
    NFTSubmenuPROD,
    NFTSubmenuPOST,
    NFTMenu,
)


# REGISTER ADD-ON

def register():
    """Register all NFT Blender menu and operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(NFTMenu.menu_draw)


def unregister():
    """Unregister all NFT Blender menu and operator classes."""
    bpy.types.TOPBAR_MT_editor_menus.remove(NFTMenu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
