#!$BLENDER_PATH/python/bin python

import getpass
import os
import pathlib
import typing

from PySide6 import QtCore, QtGui, QtWidgets
# from __feature__ import snake_case, true_property
import sqlalchemy

from nft_blender.nft_bpy import nft_io, nft_ui
from nft_blender.nft_db import nft_sql

import importlib
importlib.reload(nft_io)
importlib.reload(nft_sql)
importlib.reload(nft_ui)


PROJ_CONFIG_DATA = nft_io.io_load_json_file(
    pathlib.Path(__file__).parent.joinpath('nft_blender_proj.config.json')
)

PROJ_DEFAULT_DB = {
    'SQLite': {
        'name': 'nft_blender',
        'path': nft_io.io_get_temp_dir(),
    }
}

PROJ_DEFAULT_PIPELINE = {
    'assets': {
        'CHAR': {
            'published': {},
            'versions': {},
        },
        'LGHT': {
            'published': {},
            'versions': {},
        },
        'PROP': {
            'published': {},
            'versions': {},
        },
    },
    'data': {
        'KSET': {},
    },
    'edit': {},
    'models': {
        'FBX': {},
    },
    'scenes': {
        'ANIM': {
            'published': {},
            'versions': {},
        },
        'LAYT': {
            'published': {},
            'versions': {},
        },
        'RNDR': {
            'published': {},
            'versions': {},
        },
    },
    'textures': {
        'HDRI': {},
        'UV': {},
    },
}

PROJ_NAME_LIST = ['NFT_Project']


class UIDialogProj(nft_ui.UIDialogBase):
    """TODO"""
    _UI_FILE_NAME = 'ui_proj_dialog.ui'
    _UI_WINDOW_TITLE = 'NFT Blender - Project Manager'

    def __init__(self, parent: QtWidgets.QApplication = None):
        """TODO"""
        self._db_engine = None

        super().__init__(parent)


    def _set_up_connections(self):
        """TODO"""

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
        self._ui.proj_db_dbms_combox.currentIndexChanged[int].connect(self.ui_update_proj_db)
        self._ui.proj_db_connect_pshbtn.clicked.connect(self.ui_update_proj_db)

        self._ui.proj_nav_combox.currentIndexChanged[int].connect(self.ui_update_proj_nav)
        self._ui.proj_nav_trview.activated[QtCore.QModelIndex].connect(self.ui_update_proj_nav)

        self._ui.proj_toolbox.currentChanged[int].connect(self.ui_update)

        self.ui_init()

    def query_db_proj_data(
            self,
            project_name: str = '',
        ) -> nft_sql.DB_Project:
        """TODO - currently for testing UI only. Use db query"""

        if project_name in PROJ_NAME_LIST:
            project_name = 'NFT_Project'
            project_code = 'NFT'
            project_path = pathlib.Path('D:/Projects/NFT Droplets/NFTears').resolve().as_posix()
            project_pipeline = PROJ_DEFAULT_PIPELINE

            db_project = nft_sql.DB_Project(
                code=project_code,
                name=project_name,
                path=project_path,
                pipeline=project_pipeline,
            )

        else:
            db_project = nft_sql.DB_Project(
                code='',
                name='',
                path=pathlib.Path(),
                pipeline={},
            )

        return db_project

    def ui_update(self, *args):
        """TODO"""
        if self.sender() == self._ui.proj_toolbox:

            if self._ui.proj_toolbox.widget(args[0]) == self._ui.proj_db_widget:
                self.ui_update_proj_db()

            elif self._ui.proj_toolbox.widget(args[0]) == self._ui.proj_create_widget:
                self.ui_update_proj_create()

            elif self._ui.proj_toolbox.widget(args[0]) == self._ui.proj_nav_widget:
                self.ui_update_proj_nav()

        else:
            self.ui_update_proj_db()
            self.ui_update_proj_create()
            self.ui_update_proj_nav()


    def ui_update_proj_create(self, *args):
        """TODO Select newly created index for self._ui.proj_create_pipe_btngrp"""
        if self.sender() == self._ui.proj_create_dir_pshbtn:
            proj_dir = nft_ui.ui_get_directory(
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
                project_name = self._ui.proj_create_name_lnedit.text()
                project_code = self._ui.proj_create_code_lnedit.text()
                project_path = pathlib.Path(self._ui.proj_create_dir_label.text()).as_posix()
                project_pipeline = self._ui.proj_create_pipe_trview.model().modelData()

                print(project_name, project_code, project_path, project_pipeline)

                # db_project = nft_sql.DB_Project(
                #     code=project_code,
                #     name=project_name,
                #     path=project_path,
                #     pipeline=project_pipeline,
                # )

            elif args[0] == self._ui.proj_create_reset_pshbtn:
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
        """TODO"""
        if self.sender() in (self._ui.proj_db_btngrp, self._ui.proj_db_dbms_combox):

            checked_btn = self._ui.proj_db_btngrp.checkedButton()

            if checked_btn == self._ui.proj_db_url_custom_radbtn:
                self._ui.proj_db_url_lnedit.setEnabled(True)

            else:
                self._ui.proj_db_url_lnedit.setEnabled(False)

                dbms_name = self._ui.proj_db_dbms_combox.currentText()
                dbms_data = PROJ_DEFAULT_DB.get(dbms_name)
                if dbms_data:
                    db_default_url = nft_sql.db_get_url(
                        db_name=dbms_data['name'],
                        root_dir_path=dbms_data['path'],
                        dbms_name=dbms_name,
                    )
                    self._ui.proj_db_url_lnedit.setText(db_default_url)

        elif self.sender() == self._ui.proj_db_connect_pshbtn:
            db_url = self._ui.proj_db_url_lnedit.text()
            db_engine = nft_sql.db_get_engine(db_url)
            db_connected = nft_sql.db_test_connection(db_engine)

            if db_connected:
                # Create default FB metadata table(s)
                nft_sql.db_create_table(db_engine)
                # Assign DB engine to instance variable
                self._db_engine = db_engine
                lbl_css = 'color: white; background-color: green'
                lbl_txt = 'Connected'

                #TODO create user in db
                proj_db_create_user(self._db_engine)

            else:
                self._db_engine = None
                lbl_css = 'color: white; background-color: red'
                lbl_txt = 'Not Connected'

            self._ui.proj_db_status_lnedit.setStyleSheet(lbl_css)
            self._ui.proj_db_status_lnedit.setText(lbl_txt)


    def ui_update_proj_nav(self, *args):
        """TODO"""
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
            proj_name_list = ['']
            if nft_sql.db_test_connection(self._db_engine):
                #TODO Query project names and extend list
                proj_name_list.extend(PROJ_NAME_LIST)
            self._ui.proj_nav_combox.clear()
            self._ui.proj_nav_combox.addItems(proj_name_list)


    def ui_init(self):
        """TODO"""
        self._ui.proj_db_dbms_combox.clear()
        self._ui.proj_db_dbms_combox.addItems(PROJ_CONFIG_DATA['databases'])
        self._ui.proj_db_status_lnedit.setStyleSheet('color: white; background-color: red')
        self._ui.proj_db_status_lnedit.setText('Not Connected')
        self._ui.proj_db_url_lnedit.setEnabled(False)
        self._ui.proj_db_user_lnedit.setText(nft_io.io_get_user())

        self._ui.proj_create_tmplt_combox.clear()
        self._ui.proj_create_tmplt_combox.addItems(PROJ_CONFIG_DATA['pipelines'])

        self.ui_update()


class UITreeModelProjCreate(nft_ui.UITreeModel):
    """TODO"""
    def data(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        role: int = QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if index.isValid() and (role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole)):
            return index.internalPointer().data(index.column())

        return None

    def flags(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        value: object | type[None] = None,
        role: int = QtCore.Qt.EditRole,
    ) -> bool:
        """TODO"""
        if any((role != QtCore.Qt.EditRole, not index.isValid(), not value)):
            return False

        index.internalPointer().setData(index.column(), value)
        self.dataChanged.emit(index, index)

        return True


class UITreeModelProjNav(nft_ui.UITreeModel):
    """TODO"""
    def setModelData(
        self,
        data: typing.Iterable,
        parent_item: 'UITreeModelProjNav' = None,
        root_url: pathlib.Path | str = '.',
    ):
        """TODO"""
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


def proj_db_create_user(
    db_engine: sqlalchemy.engine.base.Engine
):
    """"""
    db_user = nft_sql.DB_User(
        name=getpass.getuser(),
    )
    nft_sql.db_upsert(
        db_engine=db_engine,
        column_name_filter='name',
        db_entries=db_user,
    )


def proj_launch_dialog():
    """TODO"""
    os.system('cls')

    nft_ui.ui_launch_dialog(UIDialogProj)


def proj_run():
    """TODO"""
    project_name = 'NFT_Project'
    project_code = 'NFT'
    project_path = pathlib.Path().resolve().as_posix()
    project_pipeline = PROJ_DEFAULT_PIPELINE

    db_url = nft_sql.db_get_url('nft_blender', nft_io.io_get_temp_dir())
    db_engine = nft_sql.db_get_engine(db_url)
    nft_sql.db_create_table(db_engine)



    nft_sql.db_upsert(db_engine, 'name', db_project, db_user)
