#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Project

"""

import json
import os
import pathlib
import typing

from PySide6 import QtCore, QtGui, QtWidgets
# from __feature__ import snake_case, true_property
import sqlalchemy

from nft_blender.nft_bpy import bpy_io
from nft_blender.nft_db import db_sql
from nft_blender.nft_qt import qt_ui

import importlib

importlib.reload(bpy_io)
importlib.reload(db_sql)
importlib.reload(qt_ui)


# Load default data from config file.
ops_proj_config_file_path = pathlib.Path(__file__).parent.joinpath('ops_proj.config.json')
with ops_proj_config_file_path.open('r', encoding='UTF-8') as readfile:
    PROJ_CONFIG_DATA = json.load(readfile)

PROJ_DEFAULT_DB = {
    'SQLite': {
        'name': __package__.split('.', maxsplit=-1)[0],
        'path': bpy_io.io_get_temp_dir(),
    }
}


class ProjDialogUI(qt_ui.UIDialogBase):
    """
    Dialog Box UI for creating and tracking high-level database data, such as projects and users.
    """
    _UI_FILE_NAME = 'ui_proj_dialog.ui'
    _UI_WINDOW_TITLE = 'NFT Blender - Project Manager'

    def __init__(self, parent: QtWidgets.QApplication = None):
        """
        Constructor method.

        :param TODO:
        :returns: TODO
        """
        self._db_engine = None

        super().__init__(modality=False, parent=parent)


    def _set_up_ui(self):
        """
        TODO

        :param TODO:
        :returns: TODO
        """

        # Create additional QObjects

        self._ui.proj_create_btngrp = QtWidgets.QButtonGroup()
        self._ui.proj_create_btngrp.addButton(self._ui.proj_create_reset_pshbtn)
        self._ui.proj_create_btngrp.addButton(self._ui.proj_create_create_pshbtn)
        self._ui.proj_create_pipe_btngrp = QtWidgets.QButtonGroup()
        self._ui.proj_create_pipe_btngrp.addButton(self._ui.proj_create_pipe_add_child_pshbtn)
        self._ui.proj_create_pipe_btngrp.addButton(self._ui.proj_create_pipe_add_item_pshbtn)
        self._ui.proj_create_pipe_btngrp.addButton(self._ui.proj_create_pipe_del_item_pshbtn)
        self._ui.proj_create_code_lnedit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'\w{0,4}'))
        )
        self._ui.proj_create_name_lnedit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'\w+'))
        )
        self._ui.proj_create_pipe_trmodl = UITreeModelProjCreate(['Project Structure:'])
        self._ui.proj_create_pipe_trview.setModel(self._ui.proj_create_pipe_trmodl)

        self._ui.proj_db_btngrp = QtWidgets.QButtonGroup()
        self._ui.proj_db_btngrp.addButton(self._ui.proj_db_url_custom_radbtn)
        self._ui.proj_db_btngrp.addButton(self._ui.proj_db_url_default_radbtn)
        self._ui.proj_db_btngrp.setExclusive(True)
        self._ui.proj_db_btngrp.button(-3).setChecked(True)

        self._ui.proj_nav_trmodl = UITreeModelProjNav()
        self._ui.proj_nav_trview.setModel(self._ui.proj_nav_trmodl)

        # Set up connections
        self._ui.proj_create_btngrp.buttonClicked[QtWidgets.QAbstractButton] \
            .connect(self.ui_update_proj_create)
        self._ui.proj_create_pipe_btngrp.buttonClicked[QtWidgets.QAbstractButton] \
            .connect(self.ui_update_proj_create)
        self._ui.proj_create_code_lnedit.textEdited[str].connect(self.ui_update_proj_create)
        self._ui.proj_create_dir_pshbtn.clicked.connect(self.ui_update_proj_create)
        self._ui.proj_create_tmplt_pshbtn.clicked.connect(self.ui_update_proj_create)

        self._ui.proj_db_btngrp.buttonClicked[QtWidgets.QAbstractButton] \
            .connect(self.ui_update_proj_db)
        self._ui.proj_db_connect_pshbtn.clicked.connect(self.ui_update_proj_db)
        self._ui.proj_db_dbms_combox.currentIndexChanged[int].connect(self.ui_update_proj_db)
        self._ui.proj_db_del_pshbtn.clicked.connect(self.ui_update_proj_db)
        self._ui.proj_db_del_rows_combox.currentIndexChanged[int].connect(self.ui_update_proj_db)
        self._ui.proj_db_del_table_combox.currentIndexChanged[int].connect(self.ui_update_proj_db)

        self._ui.proj_nav_combox.currentIndexChanged[int].connect(self.ui_update_proj_nav)
        self._ui.proj_nav_trview.activated[QtCore.QModelIndex].connect(self.ui_update_proj_nav)

        self._ui.proj_toolbox.currentChanged[int].connect(self.ui_update)

        self.ui_init()

    def query_db_proj_data(
            self,
            project_name: str = '',
        ) -> db_sql.DBProject:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        db_project = db_sql.DBProject(
            code='',
            name='',
            path=pathlib.Path(),
            pipeline={},
        )

        if self.set_db_connection():

            db_col_name = 'name'
            db_projects = db_sql.db_query_basic(
                self._db_engine,
                db_sql.DBProject,
                limit=1,
                columns=(db_col_name,),
                filters=((db_col_name, project_name),)
            )

            if db_projects:
                db_project = db_sql.DBProject(
                    code=db_projects[0].code,
                    name=db_projects[0].name,
                    path=pathlib.Path(db_projects[0].path).resolve().as_posix(),
                    pipeline=db_projects[0].pipeline,
                )

        return db_project

    def set_db_connection(
        self,
        db_url: str = '',
        force_reset: bool = False,
        force_update: bool = True,
    ) -> bool:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if force_reset or self._db_engine is None:
            self._db_engine = db_sql.db_get_engine(db_url)
            # Assign DB engine to instance variable

        db_connected = db_sql.db_test_connection(self._db_engine)

        if db_connected and force_update:
            # Create default FB metadata table(s)
            db_sql.db_create_table(self._db_engine)

            # Create DBUser entry in DB if necessary.
            proj_db_update_user(
                db_engine=self._db_engine,
                name=self._ui.proj_db_user_lnedit.text(),
            )

        return db_connected

    def ui_update(self, *args):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if self.sender() == self._ui.proj_toolbox:

            proj_widget = self._ui.proj_toolbox.widget(args[0])

            if proj_widget == self._ui.proj_db_widget:
                self.ui_update_proj_db()

            elif proj_widget == self._ui.proj_create_widget:
                proj_widget.setEnabled(self.set_db_connection(force_update=False))
                self.ui_update_proj_create()

            elif proj_widget == self._ui.proj_nav_widget:
                proj_widget.setEnabled(self.set_db_connection(force_update=False))
                self.ui_update_proj_nav()

        else:
            self.ui_update_proj_db()
            self.ui_update_proj_create()
            self.ui_update_proj_nav()


    def ui_update_proj_create(self, *args):
        """TODO Select newly created index for self._ui.proj_create_pipe_btngrp"""
        if self.sender() == self._ui.proj_create_dir_pshbtn:
            proj_dir = qt_ui.ui_get_directory(
                caption='Select Location to Create Project',
                dir_str=pathlib.Path.home().as_posix(),
                parent=self,
            )
            if proj_dir is not None:
                self._ui.proj_create_dir_label.setText(proj_dir.as_posix())

        elif self.sender() == self._ui.proj_create_code_lnedit:
            self._ui.proj_create_code_lnedit.setText(args[0].upper())

        elif self.sender() == self._ui.proj_create_btngrp:

            if args[0] == self._ui.proj_create_create_pshbtn:
                project_code = self._ui.proj_create_code_lnedit.text()
                project_name = self._ui.proj_create_name_lnedit.text()
                project_root_path = pathlib.Path(self._ui.proj_create_dir_label.text())
                project_path = project_root_path.joinpath(project_name).as_posix()
                project_pipeline = self._ui.proj_create_pipe_trview.model().modelData()

                if not qt_ui.ui_message_box(
                    title='Create/Update Project',
                    text=f'Create/update DBProject entry with:\n' \
                        f'project code: "{project_code}", ' \
                        f'project name: "{project_name}"?',
                    message_box_type='question',
                    parent=self,
                ):
                    return

                # Create/update DBProject entry in DB.
                proj_db_update_project(
                    db_engine=self._db_engine,
                    code=project_code,
                    name=project_name,
                    path=project_path,
                    pipeline=project_pipeline,
                )

                # Create/update the project directory structure.
                if qt_ui.ui_message_box(
                    title='Create/Update Directory Structure?',
                    text=f'Project directory structure will be created at {project_path}.\n' \
                         'No folders or files will be overwritten or removed in the process.',
                    message_box_type='question',
                    parent=self,
                ):
                    proj_paths = proj_io_pipeline_to_paths(project_path, project_pipeline)
                    bpy_io.io_make_dirs(*proj_paths)
                    qt_ui.ui_message_box(
                        title='Folders Created/Updated',
                        text=f'Project directory structure created/updated in {project_path}.',
                        message_box_type='information',
                        parent=self,
                    )
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(project_path))

            self._ui.proj_create_dir_label.clear()
            self._ui.proj_create_code_lnedit.clear()
            self._ui.proj_create_name_lnedit.clear()
            self._ui.proj_create_pipe_trmodl.clear()
            self._ui.proj_create_pipe_trview.setHeaderHidden(True)

        elif self.sender() == self._ui.proj_create_pipe_btngrp:

            index = self._ui.proj_create_pipe_trview.selectionModel().currentIndex()

            if args[0] == self._ui.proj_create_pipe_add_child_pshbtn:
                new_rows = ['new_child']
                self._ui.proj_create_pipe_trmodl.insertRows(-1, new_rows, index)

            elif args[0] == self._ui.proj_create_pipe_add_item_pshbtn:
                new_rows = ['new_item']
                self._ui.proj_create_pipe_trmodl.insertRows(index.row(), new_rows, index.parent())

            elif args[0] == self._ui.proj_create_pipe_del_item_pshbtn:
                self._ui.proj_create_pipe_trmodl.removeRows(index.row(), 1, index.parent())

        elif self.sender() == self._ui.proj_create_tmplt_pshbtn:
            tmplt_name = self._ui.proj_create_tmplt_combox.currentText()
            tmplt_data = PROJ_CONFIG_DATA['pipelines'][tmplt_name]

            self._ui.proj_create_pipe_trmodl.clear()
            self._ui.proj_create_pipe_trmodl.setModelData(tmplt_data)
            self._ui.proj_create_pipe_trview.setHeaderHidden(False)


    def ui_update_proj_db(self, *args):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if self.sender() in (self._ui.proj_db_btngrp, self._ui.proj_db_dbms_combox):

            checked_btn = self._ui.proj_db_btngrp.checkedButton()

            if checked_btn == self._ui.proj_db_url_custom_radbtn:
                self._ui.proj_db_url_lnedit.setEnabled(True)

            else:
                self._ui.proj_db_url_lnedit.setEnabled(False)

                dbms_name = self._ui.proj_db_dbms_combox.currentText()
                dbms_data = PROJ_DEFAULT_DB.get(dbms_name)
                if dbms_data:
                    db_default_url = db_sql.db_get_url(
                        db_name=dbms_data['name'],
                        db_root_path=dbms_data['path'].as_posix(),
                        dbms_name=dbms_name,
                    )
                    self._ui.proj_db_url_lnedit.setText(db_default_url)

        elif self.sender() == self._ui.proj_db_connect_pshbtn:

            if self.set_db_connection(self._ui.proj_db_url_lnedit.text()):
                lbl_css = 'color: white; background-color: green'
                lbl_txt = 'Connected'

                # Populate with DB Model Classes.
                self._ui.proj_db_del_table_combox.clear()
                self._ui.proj_db_del_table_combox.addItem('', None)

                for db_model in db_sql.DBModels:
                    self._ui.proj_db_del_table_combox.addItem(db_model.__tablename__, db_model)

            else:
                lbl_css = 'color: white; background-color: red'
                lbl_txt = 'Not Connected'

            self._ui.proj_db_status_lnedit.setStyleSheet(lbl_css)
            self._ui.proj_db_status_lnedit.setText(lbl_txt)

        elif self.sender() == self._ui.proj_db_del_pshbtn:
            db_cls = self._ui.proj_db_del_table_combox.currentData()
            db_row = self._ui.proj_db_del_rows_combox.currentData()

            if qt_ui.ui_message_box(
                title='Confirm Deletion',
                text=f'This will delete {db_cls.name}: {db_row.name} from the database. Continue?',
                message_box_type='question',
                parent=self,
            ):
                proj_db_delete_row(
                    db_engine=self._db_engine,
                    db_cls=db_cls,
                    db_row_id=db_row.id,
                )
                db_row_index = self._ui.proj_db_del_rows_combox.currentIndex()
                self._ui.proj_db_del_rows_combox.removeItem(db_row_index)
                self._ui.proj_db_del_table_combox.setCurrentIndex(0)

        elif self.sender() == self._ui.proj_db_del_table_combox:
            # Populate with rows for the DB Model.
            db_cls = self._ui.proj_db_del_table_combox.currentData()
            self._ui.proj_db_del_rows_combox.clear()
            self._ui.proj_db_del_rows_combox.addItem('', None)

            if db_cls is not None:
                for db_row in db_sql.db_query_basic(self._db_engine, db_cls):
                    self._ui.proj_db_del_rows_combox.addItem(db_row.name, db_row)

        elif self.sender() == self._ui.proj_db_del_rows_combox:
            self._ui.proj_db_del_pshbtn.setEnabled(args[0] > 0)

        elif self.sender() == self._ui.proj_toolbox:
            self._ui.proj_db_del_table_combox.setCurrentIndex(0)

        self._ui.proj_db_del_grpbox.setEnabled(self.set_db_connection(force_update=False))

    def ui_update_proj_nav(self, *args):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if self.sender() == self._ui.proj_nav_combox:
            db_proj_data = self.query_db_proj_data(self._ui.proj_nav_combox.itemText(args[0]))
            self._ui.proj_nav_trmodl = UITreeModelProjNav(
                ['Project Structure:', 'Directory Path']
            )
            self._ui.proj_nav_trmodl.setModelData(db_proj_data.pipeline, root_url=db_proj_data.path)
            self._ui.proj_nav_trview.setModel(self._ui.proj_nav_trmodl)
            self._ui.proj_nav_trview.setHeaderHidden(not db_proj_data.pipeline)
            self._ui.proj_nav_trview.header().setSectionResizeMode(
                QtWidgets.QHeaderView.ResizeToContents
            )

        elif self.sender() == self._ui.proj_nav_trview:
            parent_index = self._ui.proj_nav_trview.model().parent(args[0])
            last_col_index = self._ui.proj_nav_trview.model().index(args[0].row(), 1, parent_index)
            last_col_data = self._ui.proj_nav_trview.model().data(last_col_index)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(last_col_data))

        elif self.sender() == self._ui.proj_toolbox:
            proj_names = ['']
            current_proj_name = self._ui.proj_nav_combox.currentText()

            if db_sql.db_test_connection(self._db_engine):
                proj_entries = db_sql.db_query_basic(self._db_engine, db_sql.DBProject)
                proj_names.extend((proj_entry.name for proj_entry in proj_entries))

            self._ui.proj_nav_combox.clear()
            self._ui.proj_nav_combox.addItems(proj_names)
            proj_name_index = self._ui.proj_nav_combox.findText(current_proj_name)
            self._ui.proj_nav_combox.setCurrentIndex(proj_name_index)

    def ui_init(self):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        self._ui.proj_db_dbms_combox.clear()
        self._ui.proj_db_dbms_combox.addItems(PROJ_CONFIG_DATA['databases'])
        self._ui.proj_db_status_lnedit.setStyleSheet('color: white; background-color: red')
        self._ui.proj_db_status_lnedit.setText('Not Connected')
        self._ui.proj_db_url_lnedit.setEnabled(False)
        self._ui.proj_db_user_lnedit.setText(bpy_io.io_get_user())

        self._ui.proj_create_tmplt_combox.clear()
        self._ui.proj_create_tmplt_combox.addItems(PROJ_CONFIG_DATA['pipelines'])

        self.ui_update()


class UITreeModelProjCreate(qt_ui.UITreeModel):
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    def data(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        role: int = QtCore.Qt.DisplayRole,
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if index.isValid() and (role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole)):
            return index.internalPointer().data(index.column())

        return None

    def flags(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        value: object | type[None] = None,
        role: int = QtCore.Qt.EditRole,
    ) -> bool:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if any((role != QtCore.Qt.EditRole, not index.isValid(), not value)):
            return False

        index.internalPointer().setData(index.column(), value)
        self.dataChanged.emit(index, index)

        return True


class UITreeModelProjNav(qt_ui.UITreeModel):
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    def setModelData(
        self,
        data: typing.Iterable,
        parent_item: 'UITreeModelProjNav' = None,
        root_url: pathlib.Path | str = '.',
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        parent_item = parent_item if parent_item else self._root_item

        if isinstance(data, typing.Mapping):
            for key, val in sorted(data.items()):
                data_items = (key, pathlib.Path(root_url).joinpath(key).as_posix())
                tree_item = self.MODEL_ITEM_TYPE(data_items, parent_item)
                parent_item.insertChildren([tree_item])
                self.setModelData(val, tree_item, root_url=data_items[1])

        elif isinstance(data, typing.Sequence):
            tree_item = self.MODEL_ITEM_TYPE(data, parent_item)
            parent_item.insertChildren([tree_item])


def proj_db_delete_row(
    db_engine: sqlalchemy.engine.base.Engine,
    db_cls: sqlalchemy.Table,
    db_row_id: int,
):
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    db_sql.db_delete_rows(db_engine, db_cls, (('id', db_row_id),))


def proj_db_update_project(
    db_engine: sqlalchemy.engine.base.Engine,
    code: str,
    name: str,
    path: pathlib.Path | str,
    pipeline: dict,
) -> bool:
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    column_name_filter = 'code'
    db_entry = db_sql.DBProject(
        code=code,
        name=name,
        path=pathlib.Path(path).resolve().as_posix(),
        pipeline=pipeline,
    )

    db_entry_results = db_sql.db_upsert(
        db_engine=db_engine,
        db_entries=[db_entry],
        column_name_filter=column_name_filter,
    )

    return db_entry_results[0]


def proj_db_update_user(
    db_engine: sqlalchemy.engine.base.Engine,
    name: str,
):
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    db_user = db_sql.DBUser(name=name)
    db_results = db_sql.db_upsert(
        db_engine=db_engine,
        db_entries=[db_user],
        column_name_filter='name',
    )

    return db_results[0]


def proj_io_pipeline_to_paths(
    root_dir_path: pathlib.Path | str,
    project_pipeline: dict,
) -> list[pathlib.Path]:
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    root_dir_path = pathlib.Path(root_dir_path)
    project_dir_paths = [root_dir_path]

    for key, val in project_pipeline.items():
        sub_dir_path = root_dir_path.joinpath(key)
        # project_dir_paths.append(sub_dir_path)
        project_dir_paths.extend(proj_io_pipeline_to_paths(sub_dir_path, val))

    return project_dir_paths


def proj_launch_dialog_ui():
    """
    TODO

    :param TODO:
    :returns: TODO
    """
    os.system('cls')

    qt_ui.ui_launch_dialog(ProjDialogUI)
