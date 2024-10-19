#!$BLENDER_PATH/python/bin python

"""MAS Blender - Add-On

Add-on Object can be accessed within Blender via nft_blender.nft_bpy.bpy_ctx.ctx_get_addon().
"""

bl_info = {
    'author': '[m a s]',
    'blender': (4, 0, 0),
    'category': 'User Interface',
    'description': 'A growing set of tools for Blender that utilize the full scope of Python 3',
    'doc_url': 'https://themasmedia.github.io/mas-blender/',
    'location': 'MAS Blender (menu bar)',
    'name': 'MAS Blender',
    'version': (0, 0, 1),
}

import os

import bpy

from nft_blender.nft_ops import ops_asst, ops_io, ops_proj, ops_rndr


import importlib

for module in (ops_asst, ops_io, ops_proj, ops_rndr):
    importlib.reload(module)


# OPERATORS

# PROJ

class MASOperatorProjectLaunchDialogUi(bpy.types.Operator):
    """
    Operator for nft_ops.ops_proj.proj_launch_dialog_ui().
    """
    bl_idname = 'mas.proj_launch_dialog_ui'
    bl_label = 'Launch NFT Project Manager'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_proj.proj_launch_dialog_ui()

        return {'FINISHED'}


# PRE

class MASOperatorAssetSetMaterialData(bpy.types.Operator):
    """
    Operator for nft_ops.ops_asst.asst_set_material_data().
    """
    bl_idname = 'mas.asst_set_material_data'
    bl_label = 'Set Material Data for Selected Meshes'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_asst.asst_set_material_data()

        return {'FINISHED'}


# PROD


# POST

class MASOperatorIoLaunchExportDialogUi(bpy.types.Operator):
    """
    Operator for ops_io.io_launch_export_dialog_ui().
    """
    bl_idname = 'mas.io_launch_export_dialog_ui'
    bl_label = 'Launch Export Dialog'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_io.io_launch_export_dialog_ui()

        return {'FINISHED'}


class MASOperatorRenderBatchRender(bpy.types.Operator):
    """
    Operator for nft_ops.ops_rndr.rndr_batch_render().
    """
    bl_idname = 'mas.rndr_batch_render'
    bl_label = 'Select and Render Blender File(s) Locally'

    def invoke(
        self,
        context: bpy.types.Context,
        event: bpy.types.Event,
    ):
        """Invoke method override."""
        ops_rndr.rndr_batch_render()

        return {'FINISHED'}


# MENUS

class MAS_MT_SubmenuPRE(bpy.types.Menu):
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
        layout.operator('mas.asst_set_material_data')


class MAS_MT_SubmenuPROD(bpy.types.Menu):
    """
    Production sub-menu.
    """
    bl_label = 'Production'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""


class MAS_MT_SubmenuPOST(bpy.types.Menu):
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
        layout.operator('mas.io_launch_export_dialog_ui')
        layout.operator('mas.rndr_batch_render')


class MAS_MT_Menu(bpy.types.Menu):
    """
    MAS Blender Menu.
    """
    bl_label = 'MAS Blender'

    def draw(
        self,
        context: bpy.types.Context,
    ):
        """Draw method override."""
        layout = self.layout
        layout.operator('mas.proj_launch_dialog_ui')
        layout.menu('MAS_MT_SubmenuPRE')
        layout.menu('MAS_MT_SubmenuPROD')
        layout.menu('MAS_MT_SubmenuPOST')

    def menu_draw(
        self,
        context: bpy.types.Context,
    ):
        """Menu draw method override."""
        self.layout.menu('MAS_MT_Menu')


classes = (
    MASOperatorProjectLaunchDialogUi,
    MASOperatorAssetSetMaterialData,
    MASOperatorIoLaunchExportDialogUi,
    MASOperatorRenderBatchRender,
    MAS_MT_SubmenuPRE,
    MAS_MT_SubmenuPROD,
    MAS_MT_SubmenuPOST,
    MAS_MT_Menu,
)


# REGISTER ADD-ON

def register():
    """
    Register all MAS Blender menu and operator classes.
    """
    os.system('cls')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(MAS_MT_Menu.menu_draw)


def unregister():
    """
    Unregister all MAS Blender menu and operator classes.
    """
    os.system('cls')
    bpy.types.TOPBAR_MT_editor_menus.remove(MAS_MT_Menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
