#!$BLENDER_PATH/python/bin python

"""
NFT Blender - UE - I/O

"""

import copy
import json
import os
import pathlib
import re
import typing

from PySide6 import QtCore, QtWidgets
# from __feature__ import snake_case, true_property

import bpy

from nft_blender.nft_bpy import bpy_ani, bpy_ctx, bpy_io, bpy_mdl, bpy_mtl, bpy_scn
from nft_blender.nft_qt import qt_ui
from nft_blender.nft_ops import OpsSessionData


# Load default data from config file.
ops_io_config_file_path = pathlib.Path(__file__).parent.joinpath('ops_io.config.json')
with ops_io_config_file_path.open('r', encoding='UTF-8') as readfile:
    IO_CONFIG_DATA = json.load(readfile)

# rigify_armature_obj = bpy_ani.ani_rigify_for_ue(
#     active_bone_layer_ids=(3, 4, 8, 11, 13, 14, 15, 16, 17, 18,)
# )
# bpy_ani.ani_reset_fcurve_modifiers(rigify_armature_obj)


class IOExportDialogUI(qt_ui.UIDialogBase):
    """
    Dialog Box UI for importing/exporting Object(s) for use in other platforms.
    """
    _UI_FILE_NAME = 'qt_io_export_dialog.ui'
    _UI_WINDOW_TITLE = 'NFT Blender - Export Tools'

    def __init__(
        self,
        parent: QtCore.QObject = None,
    ) -> None:
        """
        Constructor method.

        :param parent: Parent object (Application, UI Widget, etc.).
        """
        self._project = OpsSessionData.project
        self._project_path = OpsSessionData.project_path
        self._project_paths = OpsSessionData.proj_pipeline_paths(
            project_pipeline=self._project.pipeline
        )

        super().__init__(modality=False, parent=parent)


    def _set_up_ui(self) -> None:
        """"""
        # Create additional QObjects
        self._ui.io_export_data_btngrp = QtWidgets.QButtonGroup()
        self._ui.io_export_data_btngrp.setExclusive(True)

        self._ui.io_export_mdfr_type_btngrp = QtWidgets.QButtonGroup()
        self._ui.io_export_mdfr_type_btngrp.setExclusive(False)

        self._ui.io_export_platform_btngrp = QtWidgets.QButtonGroup()
        self._ui.io_export_platform_btngrp.setExclusive(True)
        self._ui.io_export_platform_btngrp.buttonClicked[QtWidgets.QAbstractButton] \
            .connect(self.ui_update)

        # Make connections
        self._ui.io_export_data_file_pshbtn.clicked.connect(self.ui_update_io_export_data_file)
        self._ui.io_export_export_pshbtn.clicked.connect(self.io_export)
        self._ui.io_export_reset_pshbtn.clicked.connect(self.ui_update)
        self._ui.io_export_mdfr_type_select_pshbtn.clicked \
            .connect(lambda: self.ui_update_io_export_mdfr(True))
        self._ui.io_export_mdfr_type_deselect_pshbtn.clicked \
            .connect(lambda: self.ui_update_io_export_mdfr(False))

        self.ui_init()

    def io_export(self):
        """TODO"""
        export_dir_path = self._ui.io_proj_export_dir_lnedit.text()
        export_platform_name = self._ui.io_export_platform_btngrp.checkedButton().text()
        export_platform_data = IO_CONFIG_DATA['export']['platforms'][export_platform_name]
        export_file_format = export_platform_data['format']
        export_settings = export_platform_data['settings']
        for type_k, type_v in export_platform_data['convert'].items():
            # export_settings[type_k] = vars(__builtins__)[type_k](export_settings[type_v])
            export_settings[type_k] = dict(__builtins__)[type_v](export_settings[type_k])

        if self._ui.io_export_data_btngrp.checkedId() == 1:
            export_data_file_path_str = self._ui.io_export_data_file_label.text()
            export_data_file_path = pathlib.Path(export_data_file_path_str)
            with pathlib.Path(export_data_file_path).open('r', encoding='UTF-8') as r_file:
                export_data = json.load(r_file)

        else:
            if self._ui.io_export_data_btngrp.checkedId() == 2:
                export_mesh_name = bpy.context.collection.name
                objs = bpy.context.collection.all_objects
            elif self._ui.io_export_data_btngrp.checkedId() == 3:
                export_mesh_name = re.sub(r'\W', '_', bpy_io.io_get_current_file_path().stem)
                objs = bpy.context.selected_objects

            export_data = {
                export_mesh_name: {
                    'meshes': [obj.name for obj in objs if isinstance(obj.data, bpy.types.Mesh)],
                    'overrides': {},
                },
            }

        export_mesh_names = sum(
            [export_data['meshes'] for export_data in export_data.values()],
            list()
        )

        mdfrs_as_shape_keys = self._ui.io_export_mdfr_grpbox.isChecked()
        mdfr_start_frame = self._ui.io_export_mdfr_start_frame_spbox.value()
        mdfr_end_frame = self._ui.io_export_mdfr_end_frame_spbox.value()
        mdfr_frame_step = self._ui.io_export_mdfr_frame_step_spbox.value()
        mdfr_frame_range = (mdfr_start_frame, mdfr_end_frame, mdfr_frame_step)
        mdfr_name_prefix = self._ui.io_export_mdfr_name_lnedit.text()
        mdfr_names = [
            btn.text() for btn in self._ui.io_export_mdfr_type_btngrp.buttons() if btn.isChecked()
        ]
        mdfr_types = tuple(getattr(bpy.types, mdfr_name) for mdfr_name in mdfr_names)

        #
        b3d_exporter = IOExporter(
            root_export_dir_path=export_dir_path
        )
        b3d_exporter.bake_ue2rigify_rig_to_source()
        # b3d_exporter.render_preview_images(
        #     preview_image_data=preview_image_data
        # )
        #
        if mdfrs_as_shape_keys:
            b3d_exporter.prepare_shape_keys_from_modifiers(
                modifier_types=mdfr_types,
                keep_as_separate=False,
                mesh_object_names=export_mesh_names,
                shape_key_name_prefix=mdfr_name_prefix,
                modifier_frame_range=mdfr_frame_range
            )
        b3d_exporter.apply_modifiers(
            mesh_object_names=export_mesh_names
        )
        if mdfrs_as_shape_keys:
            b3d_exporter.apply_shape_keys_from_modifiers(
                move_shape_keys_to_top=True
            )
        #
        b3d_exporter.export_objects(
            mesh_data=export_data,
            export_file_format=export_file_format,
            **export_settings
        )

        #
        qt_ui.ui_message_box(
            title='Export Complete',
            text=f'{export_platform_name} export completed successfully.',
            message_box_type='information'
        )
        self.done(0)

    def ui_init(self) -> None:
        """
        Initializes the UI.
        """
        export_data_names = ('Export Data File', 'Active Collection', 'Selected Object(s)')
        for i, export_data_name in enumerate(export_data_names, 1):
            export_data_radbtn = QtWidgets.QRadioButton(export_data_name)
            self._ui.io_export_data_frame.layout().addWidget(export_data_radbtn)
            self._ui.io_export_data_btngrp.addButton(export_data_radbtn, i)
            self._ui.io_export_data_btngrp.setId(export_data_radbtn, i)
        self._ui.io_export_data_btngrp.button(1).setChecked(True)

        for i, mdfr_name in enumerate(IO_CONFIG_DATA['export']['modifier_types'], 1):
            mdfr_type_chbox = QtWidgets.QCheckBox(mdfr_name)
            mdfr_type_chbox.setChecked(True)
            self._ui.io_export_mdfr_type_widget.layout().addWidget(mdfr_type_chbox)
            self._ui.io_export_mdfr_type_btngrp.addButton(mdfr_type_chbox)
            self._ui.io_export_mdfr_type_btngrp.setId(mdfr_type_chbox, i)

        for i, platform_name in enumerate(IO_CONFIG_DATA['export']['platforms'], 1):
            platform_radbtn = QtWidgets.QRadioButton(platform_name)
            self._ui.io_export_platform_grpbox.layout().addWidget(platform_radbtn)
            self._ui.io_export_platform_btngrp.addButton(platform_radbtn)
            self._ui.io_export_platform_btngrp.setId(platform_radbtn, i)
        self._ui.io_export_platform_btngrp.button(1).setChecked(True)

        self._ui.io_proj_name_lnedit.setText(self._project.name)
        self._ui.io_proj_export_dir_lnedit.setText(
            self._project_paths.get('models', self._project_path).as_posix()
        )

        try:
            armature_msg = \
                'Control mode for ue2rigify detected.' + \
                f'Source Rig will be exported: {bpy.context.scene.ue2rigify.source_rig.name}'
        except AttributeError:
            armature_msg = 'Armature objects modifying exported Mesh Object(s) will be exported.'
        self._ui.io_export_armature_detect.setText(armature_msg)

        #
        proj_data_dir_path = self._project_paths.get('data/addons/nft_blender')
        export_platform = self._ui.io_export_platform_btngrp.checkedButton().text()
        export_file_pattern = re.sub(r'\s', '*', export_platform.lower())
        for export_json_file_path in proj_data_dir_path.glob(f'*{export_file_pattern}.json'):
            self._ui.io_export_data_file_label.setText(export_json_file_path.as_posix())
            break

        self.ui_update()

    def ui_update(self) -> None:
        """
        Updates the UI section(s) based on the widget sender
        (or all sections if called by the script).
        """
        if self.sender() == self._ui.io_export_reset_pshbtn:
            self._ui.io_export_data_btngrp.button(1).setChecked(True)
            self._ui.io_export_data_file_label.setText('')
            self._ui.io_export_mdfr_end_frame_spbox.setValue(0)
            self._ui.io_export_mdfr_frame_step_spbox.setValue(1)
            self._ui.io_export_mdfr_name_lnedit.setText('')
            self._ui.io_export_mdfr_start_frame_spbox.setValue(0)

        use_export_data_file = self._ui.io_export_data_btngrp.checkedId() == 1
        self._ui.io_export_data_file_pshbtn.setEnabled(use_export_data_file)
        self._ui.io_export_data_file_label.setEnabled(use_export_data_file)

        export_platform_name = self._ui.io_export_platform_btngrp.checkedButton().text()
        export_file_format = IO_CONFIG_DATA['export']['platforms'][export_platform_name]['format']
        self._ui.io_export_format_label.setText(export_file_format)
        self._ui.io_export_export_pshbtn.setEnabled(
            pathlib.Path(self._ui.io_export_data_file_label.text()).exists()
        )

        if self.sender() is None:

            export_file_path = pathlib.Path(self._ui.io_export_data_file_label.text())
            export_config_file_path = export_file_path.with_suffix('.config.json')
            if export_config_file_path.is_file():
                with export_config_file_path.open('r', encoding='UTF-8') as r_file:
                    export_config_data = json.load(r_file)

                for config_k, widget_func in {
                    'mdfr_end_frame': self._ui.io_export_mdfr_end_frame_spbox.setValue,
                    'mdfr_frame_step': self._ui.io_export_mdfr_frame_step_spbox.setValue,
                    'mdfr_name': self._ui.io_export_mdfr_name_lnedit.setText,
                    'mdfr_start_frame': self._ui.io_export_mdfr_start_frame_spbox.setValue
                }.items():
                    if config_k in export_config_data:
                        widget_func(export_config_data[config_k])

    def ui_update_io_export_data_file(self) -> None:
        """TODO"""
        export_file_path = qt_ui.ui_get_file(
            caption='Select export data file',
            dir_str=self._project_paths.get('data', self._project_path).as_posix(),
            filter_str='JSON Files (*.json)'
        )
        if export_file_path is not None:
            self._ui.io_export_data_file_label.setText(export_file_path.as_posix())

        self.ui_update()

    def ui_update_io_export_mdfr(self, *args):
        """TODO"""
        for mdfr_chbox in self._ui.io_export_mdfr_type_btngrp.buttons():
            mdfr_chbox.setChecked(args[0])


class IOExporter(object):
    """
    TODO
    """

    def __init__(
        self,
        root_export_dir_path: typing.Union[pathlib.Path, str]
    ):
        """TODO"""
        root_export_dir_path = pathlib.Path(root_export_dir_path)
        self.export_dir_path = root_export_dir_path.joinpath(bpy_io.io_get_current_file_path().stem)
        self.export_dir_path.mkdir(parents=True, exist_ok=True)
        #
        # Save as a separate file in the temp directory for the session.
        current_file_name = bpy_io.io_get_current_file_path().name
        temp_dir_path = bpy_io.io_get_temp_dir(context='session')
        save_file_path = temp_dir_path.joinpath(current_file_name)
        bpy_io.io_save_as(
            file_path=save_file_path,
            check_existing=False
        )
        #
        self.armature_obj = None
        self.control_rig = None
        self.shape_key_meshes = {}
        self.shape_key_modifier_types = set()

        ue2rigify_loaded = all((
            bpy_ctx.ctx_get_addon('rigify'),
            bpy_ctx.ctx_get_addon('ue2rigify')
        ))
        if ue2rigify_loaded:
            import ue2rigify
            ue2rigify_extras_col = bpy.data.collections.get(
                ue2rigify.constants.Collections.EXTRAS_COLLECTION_NAME
            )
            self.armature_obj = bpy.context.scene.ue2rigify.source_rig
            if ue2rigify_extras_col:
                self.control_rig = ue2rigify_extras_col.objects.get(
                    ue2rigify.constants.Rigify.CONTROL_RIG_NAME
                )

    def apply_modifiers(
        self,
        mesh_object_names: list = typing.Iterable[str]
    ):
        """
        TODO
        A mesh object cannot be exported from Blender with Shape Keys if any modifiers are active.
        Sadly, most modifiers cannot be applied to a mesh object if it has any shape keys.
        apply_modifiers() work-around:
        1. Creates temporary mesh object duplicate(s) for each shape key on a mesh object.
        2. Removes all shape keys from source mesh object so that modifiers can be applied.
        3. Creates a new shape key from each temporary mesh duplicate.
        """
        # Iterate through each mesh object
        for mesh_obj_name in mesh_object_names:
            orig_mesh_obj = bpy.data.objects.get(mesh_obj_name)
            if orig_mesh_obj is not None:

                bpy_scn.scn_set_all_hidden(orig_mesh_obj, False)
                dup_mesh_objs = {}

                if orig_mesh_obj.data.shape_keys:
                    # Clear drivers and/or keyframes driving shape keys and set their values to 0
                    shape_key_data_name = orig_mesh_obj.active_shape_key.id_data.name
                    anim_data = bpy.data.shape_keys[shape_key_data_name].animation_data
                    if anim_data:
                        action_fcrvs = anim_data.action.fcurves if anim_data.action else []
                        for _ in action_fcrvs:
                            action_fcrvs.remove(action_fcrvs[0])
                        driver_fcrvs = anim_data.drivers
                        for _ in driver_fcrvs:
                            driver_fcrvs.remove(driver_fcrvs[0])
                    orig_shape_keys = orig_mesh_obj.data.shape_keys.key_blocks
                    for shape_key in orig_shape_keys:
                        shape_key.value = 0

                    # Create mesh object duplicate(s) for each shape key on the mesh object.
                    for shape_key in orig_shape_keys[1:]:
                        bpy_scn.scn_select_items(items=[orig_mesh_obj])
                        shape_key.value = 1
                        bpy.ops.object.duplicate(linked=False)
                        dup_mesh_obj = bpy.context.object
                        dup_mesh_objs[shape_key.name] = dup_mesh_obj
                        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                        for dup_mod in dup_mesh_obj.modifiers:
                            if not isinstance(dup_mod, bpy.types.ArmatureModifier):
                                if isinstance(dup_mod, tuple(self.shape_key_modifier_types)):
                                    bpy.ops.object.modifier_remove(modifier=dup_mod.name)
                                else:
                                    bpy.ops.object.modifier_apply(modifier=dup_mod.name)
                        shape_key.value = 0

                bpy_scn.scn_select_items(items=[orig_mesh_obj])
                orig_mesh_obj.shape_key_clear()
                for mod in orig_mesh_obj.modifiers:
                    if not isinstance(mod, bpy.types.ArmatureModifier):
                        if isinstance(mod, tuple(self.shape_key_modifier_types)):
                            bpy.ops.object.modifier_remove(modifier=mod.name)
                        else:
                            bpy.ops.object.modifier_apply(modifier=mod.name)

                for shape_key_name, dup_mesh_obj in dup_mesh_objs.items():
                    bpy_scn.scn_select_items(items=[dup_mesh_obj, orig_mesh_obj])
                    bpy.ops.object.join_shapes()
                    shape_key_index = len(orig_mesh_obj.data.shape_keys.key_blocks) - 1
                    orig_mesh_obj.active_shape_key_index = shape_key_index
                    orig_mesh_obj.active_shape_key.name = shape_key_name
                    bpy_scn.scn_select_items(items=[dup_mesh_obj])
                    bpy.ops.object.delete(use_global=False)
                    bpy.context.view_layer.objects.active = orig_mesh_obj
                orig_mesh_obj.active_shape_key_index = 0

    def apply_shape_keys_from_modifiers(
        self,
        move_shape_keys_to_top: bool = False,
    ):
        """TODO"""
        for orig_mesh_obj, shape_key_meshes in self.shape_key_meshes.items():
            for i, (shape_key_name, shape_key_mesh) in enumerate(shape_key_meshes.items(), 1):
                bpy_scn.scn_select_items(items=[shape_key_mesh, orig_mesh_obj])
                bpy.ops.object.join_shapes()
                bpy_scn.scn_select_items(items=[orig_mesh_obj])
                shape_key_index = len(orig_mesh_obj.data.shape_keys.key_blocks) - 1
                orig_mesh_obj.active_shape_key_index = shape_key_index
                orig_mesh_obj.active_shape_key.name = shape_key_name
                if move_shape_keys_to_top:
                    bpy.ops.object.shape_key_move(type='TOP')
                    while orig_mesh_obj.active_shape_key_index < i:
                        bpy.ops.object.shape_key_move(type='DOWN')

                bpy_scn.scn_select_items(items=[shape_key_mesh])
                bpy.ops.object.delete(use_global=False)
            orig_mesh_obj.active_shape_key_index = 0

    def bake_ue2rigify_rig_to_source(self):
        """
        Note that ue2rigify will only bake actions present in the rig's NLA editor.
        Make sure to stash (or push down) all actions and
        set their frame range to include them before baking.
        """
        if self.control_rig is not None:

            # Create NLA strips for each action
            anim_data = self.control_rig.animation_data
            if anim_data is not None:
                bpy_scn.scn_select_items(items=[self.control_rig])
                bpy_ani.ani_reset_armature_transforms(self.control_rig)
                for nla_track in anim_data.nla_tracks:
                    anim_data.nla_tracks.remove(nla_track)

                for action in reversed(bpy.data.actions):
                    nla_track = anim_data.nla_tracks.new()
                    nla_track.lock = True
                    nla_track.mute = True
                    nla_track.name = action.name
                    nla_track.select = False

                    nla_strip = nla_track.strips.new(
                        name=action.name,
                        start=int(action.frame_range[0]),
                        action=action
                    )
                    nla_strip.action_frame_end = int(action.frame_range[1])
                    nla_strip.action_frame_start = int(action.frame_range[0])
                    nla_strip.select = False

                    bpy_scn.scn_select_items(items=[self.control_rig])
                    bpy_ani.ani_reset_armature_transforms(self.control_rig)

            # ue2rigify bake rig to source
            bpy.ops.ue2rigify.bake_from_rig_to_rig()

        # Clear current action and reset armature transforms
        bpy_scn.scn_select_items(items=[self.armature_obj])
        bpy_ani.ani_reset_armature_transforms(armature_obj=self.armature_obj)

    def export_objects(
        self,
        mesh_data: dict,
        export_file_format: str = 'fbx',
        **export_settings
    ):
        """
        onCyber requirements:
            - Url for testing "Spaces": https://oncyber.io/uploader
            - Must be glTF Binary file format (*.glb).
            - Preformance must support >60fps across devices.
              Add ?stats=true to the end of your destination URL to get a sense for FPS.
              Use https://gltf.report/ to get an in-browser performance report.
            - Upload url: http://oncyber.io/uploader.
              Uploaded spaces url: https://oncyber.io/destinations.
            - Reference model: https://docs.oncyber.io/architects/starter-models
              Note:
              - All mesh is parented to specifically named Empty objects for functionality.
              - Do not apply location/rotation transforms to objects.
              - "Placeholder" objects must be named "placeholder_001,*_002,...etc".
                Placeholders must contain at least one face and are created at the object's pivot.
              - The usage of animation Actions in the NLE for certain objects.
              - Reflective meshes are named with the suffix "_pbr".
                Materials applied to these objects must only be applied to objects with this suffix.
              - Portal doors must be named and parented to the display Empty.
                The object must be named "Portal_Door_001".
                In the NLE, the tracks must be namned "Portal_Open_001" and "Portal_Close_001".
              - Lighting must be "baked" into textures.
              - 1024x1024 textures with a maximum file size ~40mb is recommended

        UE5 requirements:
            -TODO
        """
        export_dir_path = self.export_dir_path.joinpath(export_file_format)
        export_dir_path.mkdir(parents=True, exist_ok=True)
        export_function = getattr(bpy.ops.export_scene, export_file_format)
        export_file_suffix = IO_CONFIG_DATA['export']['file_formats'][export_file_format]

        bpy_scn.scn_select_items(items=[self.armature_obj])
        bpy_ani.ani_reset_armature_transforms(armature_obj=self.armature_obj)

        for mesh_name, mesh_export_data in mesh_data.items():

            export_file_path = export_dir_path.joinpath(mesh_name).with_suffix(export_file_suffix)
            export_objs = [self.armature_obj] if self.armature_obj is not None else []

            for mesh_obj_name in mesh_export_data['meshes']:
                mesh_obj = bpy.data.objects.get(mesh_obj_name)
                if mesh_obj is not None:
                    export_objs.extend([
                        mdfr.object for mdfr in mesh_obj.modifiers if isinstance(
                            mdfr, bpy.types.ArmatureModifier
                        )
                    ])
                    export_objs.append(mesh_obj)

            export_objs = list(set(export_objs))
            bpy_scn.scn_select_items(items=export_objs)

            export_settings_copy = copy.deepcopy(export_settings)
            for override_k, override_v in mesh_export_data['overrides'].items():
                export_settings_copy[override_k] = override_v

            export_function(
                filepath=export_file_path.as_posix(),
                **export_settings_copy
            )

    def prepare_shape_keys_from_modifiers(
        self,
        modifier_types: typing.Tuple[bpy.types.Modifier] = (bpy.types.Modifier,),
        keep_as_separate: bool = True,
        mesh_object_names: list = typing.Iterable[str],
        shape_key_name_prefix: str = '',
        modifier_frame_range: typing.Iterable[int] = (1, 2, 1)
    ):
        """
        Run this, then run apply_shape_keys_from_modifiers() after apply_modifiers().
        """
        def _add_shape_key_mesh(
            orig_mesh_obj: bpy.types.Object,
            shape_key_name: str,
            shape_key_mesh_obj: bpy.types.Object
        ):
            """TODO"""
            if orig_mesh_obj not in self.shape_key_meshes:
                self.shape_key_meshes[orig_mesh_obj] = {}
            self.shape_key_meshes[orig_mesh_obj][shape_key_name] = shape_key_mesh_obj

        #
        for i in range(*modifier_frame_range):

            if len(range(*modifier_frame_range)) > 1:
                shape_key_name = f'{shape_key_name_prefix}_{i:02d}'
            else:
                shape_key_name = shape_key_name_prefix

            for mesh_object_name in mesh_object_names:
                orig_mesh_obj = bpy.data.objects.get(mesh_object_name)
                if orig_mesh_obj is not None:

                    #
                    if not any(
                        (isinstance(mod, modifier_types) for mod in orig_mesh_obj.modifiers)
                    ):
                        continue

                    # Force driver updates
                    bpy.context.scene.frame_set(i)
                    anim_data = orig_mesh_obj.animation_data
                    if anim_data:
                        for fcrv in orig_mesh_obj.animation_data.drivers:
                            fcrv.driver.expression = fcrv.driver.expression
                            fcrv.update()

                    # If a separate shape key is needed for each modifier of the given type(s),
                    # create a duplicate mesh for each modifier.
                    if keep_as_separate:
                        for j, mod in enumerate(orig_mesh_obj.modifiers):
                            if isinstance(mod, modifier_types):
                                dup_mesh_name = \
                                    f'{shape_key_name}_{j:03d}' if shape_key_name else mod.name
                                bpy_scn.scn_select_items(items=[orig_mesh_obj])
                                dup_mesh_obj = bpy_scn.scn_duplicate_object(
                                    obj=orig_mesh_obj,
                                    name=dup_mesh_name
                                )
                                if dup_mesh_obj.data.shape_keys:
                                    bpy.ops.object.shape_key_clear()
                                    bpy.ops.object.shape_key_remove(all=True, apply_mix=False)
                                _add_shape_key_mesh(
                                    orig_mesh_obj=orig_mesh_obj,
                                    shape_key_name=dup_mesh_name,
                                    shape_key_mesh_obj=dup_mesh_obj
                                )

                                for dup_mod in dup_mesh_obj.modifiers:
                                    if isinstance(dup_mod, modifier_types):
                                        if dup_mod.name == mod.name:
                                            bpy_mdl.mdl_set_modifier_display(
                                                modifier=dup_mod, visibility=True
                                            )
                                        else:
                                            bpy.ops.object.modifier_remove(modifier=dup_mod.name)
                                    try:
                                        bpy.ops.object.modifier_apply(modifier=dup_mod.name)
                                    except RuntimeError as r_e:
                                        print(r_e)

                    # If a single shape key is needed for all the deformer(s),
                    # create a single duplicate mesh from all modifiers of the given type(s).
                    else:
                        bpy_scn.scn_select_items(items=[orig_mesh_obj])
                        dup_mesh_obj = bpy_scn.scn_duplicate_object(
                            obj=orig_mesh_obj,
                            name=shape_key_name
                        )
                        if dup_mesh_obj.data.shape_keys:
                            bpy.ops.object.shape_key_clear()
                            bpy.ops.object.shape_key_remove(all=True, apply_mix=False)
                        _add_shape_key_mesh(
                            orig_mesh_obj=orig_mesh_obj,
                            shape_key_name=shape_key_name,
                            shape_key_mesh_obj=dup_mesh_obj
                        )

                        for dup_mod in dup_mesh_obj.modifiers:
                            if isinstance(dup_mod, modifier_types):
                                bpy_mdl.mdl_set_modifier_display(modifier=dup_mod, visibility=True)
                            try:
                                bpy.ops.object.modifier_apply(modifier=dup_mod.name)
                            except RuntimeError as r_e:
                                print(r_e)

            self.shape_key_modifier_types = self.shape_key_modifier_types.union(modifier_types)

        bpy.context.scene.frame_set(modifier_frame_range[0])

    def render_preview_images(
        self,
        preview_image_data: dict,
        export_file_format: str = 'png',
    ):
        """TODO"""
        EXPORT_FILE_FORMAT_DATA = {
            'png': {
                'func': bpy.ops.render.opengl,
                'subdir': 'images',
                'suffix': '.png',
            }
        }
        active_cam = bpy.context.scene.camera
        light_objs = bpy_scn.scn_get_objects_of_type('LIGHT')

        export_function = getattr(bpy.ops.render.opengl, export_file_format)
        export_file_suffix = EXPORT_FILE_FORMAT_DATA[export_file_format]['suffix']
        export_subdir_name = EXPORT_FILE_FORMAT_DATA[export_file_format]['subdir']
        export_dir_path = self.export_dir_path.joinpath(export_subdir_name)
        export_dir_path.mkdir(parents=True, exist_ok=True)

        for export_file_name, data in preview_image_data.items():
            objects_to_render = [active_cam]
            objects_to_render.extend(light_objs)

            for mesh_name, mesh_data in data['meshes'].items():
                mesh_obj = bpy.data.objects.get(mesh_name)
                if mesh_obj is not None:
                    bpy_scn.scn_set_all_hidden(mesh_obj, False)
                    objects_to_render.append(mesh_obj)

                    for mdfr_k, mdfr_v in mesh_data['Modifiers'].items():
                        for input_k, input_v in mdfr_v.items():
                            mesh_obj.modifiers[mdfr_k][input_k] = input_v

                    for shape_k, shape_v in mesh_data['ShapeKeys'].items():
                        # break inputs, if any
                        shape_key_data_name = mesh_obj.active_shape_key.id_data.name
                        anim_data = bpy.data.shape_keys[shape_key_data_name].animation_data
                        if anim_data:
                            action_fcrvs = anim_data.action.fcurves if anim_data.action else []
                            for _ in action_fcrvs:
                                action_fcrvs.remove(action_fcrvs[0])
                            driver_fcrvs = anim_data.drivers
                            for _ in driver_fcrvs:
                                driver_fcrvs.remove(driver_fcrvs[0])
                        shape_keys = mesh_obj.data.shape_keys.key_blocks
                        shape_keys[shape_k].value = shape_v

            render_viewport_image(
                output_path=export_dir_path.joinpath(f'{export_file_name}{export_file_suffix}'),
                objects_to_render=objects_to_render,
                render_cam=active_cam
            )


def render_viewport_image(
    output_path: typing.Union[pathlib.Path, str],
    objects_to_render: typing.Iterable,
    render_cam: bpy.types.Camera,
    color_depth: str = '8',
    color_mode: str = 'RGBA',
    compression: int = 100,
    file_format: str = 'PNG',
    resolution_percentage: int = 100,
    viewport_shading_type: str = 'MATERIAL'
):
    """TODO"""
    #Create temporary preview image render scene
    scn = bpy_scn.scn_create_and_link_new_scene(
        objects_to_link=objects_to_render
    )
    scn.camera = render_cam

    screen_spaces = []
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    screen_spaces.append(space)
    for space in screen_spaces:
        space.overlay.show_axis_x = False
        space.overlay.show_axis_y = False
        space.overlay.show_axis_z = False
        space.overlay.show_cursor = False
        space.overlay.show_extras = False
        space.overlay.show_floor = False
        space.overlay.show_outline_selected = False
        space.region_3d.view_perspective = 'CAMERA'
        space.shading.type = viewport_shading_type

    #
    scn.render.image_settings.file_format = file_format
    scn.render.image_settings.color_mode = color_mode
    scn.render.image_settings.color_depth = color_depth
    scn.render.image_settings.compression = compression
    scn.render.resolution_percentage = resolution_percentage

    scn.render.filepath = pathlib.Path(output_path).as_posix()

    bpy.ops.render.opengl(
        animation=False,
        render_keyed_only=False,
        sequencer=False,
        write_still=True,
        view_context=True
    )

    bpy.ops.scene.delete()


def io_launch_export_dialog_ui() -> None:
    """
    Launches the IO Export Dialog Box UI.
    """
    os.system('cls')

    qt_ui.ui_launch_dialog(IOExportDialogUI)
