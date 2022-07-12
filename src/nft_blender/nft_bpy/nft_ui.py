#!$BLENDER_PATH/python/bin python

import pathlib
import sys
import typing

from PySide6 import QtCore, QtGui, QtUiTools, QtWidgets
# from __feature__ import snake_case, true_property


class UIDialogBase(QtWidgets.QDialog):
    """TODO"""
    _UI_FILE_NAME = ''
    _UI_WINDOW_TITLE = ''

    def __init__(
        self,
        parent: QtWidgets.QApplication = None,
    ):
        """TODO"""
        super().__init__(parent=parent)
        self._set_up_ui()
        self._set_up_connections()

    def _set_up_connections(self):
        """TODO"""
        raise NotImplementedError

    def _set_up_ui(self):
        """TODO"""
        self._ui = QtUiTools.QUiLoader().load(self._ui_file_path.as_posix())
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self._ui)
        self.setLayout(self._layout)

        self.setWindowTitle(self._ui_window_title)

    @classmethod
    @property
    def _ui_file_path(cls) -> pathlib.Path:
        """TODO"""
        ui_dir_path = pathlib.Path(__file__).parent.parent
        ui_file_path = ui_dir_path.joinpath('ui', cls._UI_FILE_NAME)
        assert ui_file_path.exists() and ui_file_path.suffix == '.ui'
        return ui_file_path

    @classmethod
    @property
    def _ui_window_title(cls) -> str:
        """TODO"""
        assert len(cls._UI_WINDOW_TITLE) > 0
        return cls._UI_WINDOW_TITLE


class UIBlenderProcess(QtCore.QProcess):
    """TODO"""

    def __init__(
        self,
        blender_app_path = pathlib.Path | str,
        blend_files: typing.Iterable[str] = (),
        parent: QtWidgets.QApplication = None,
    ):
        """TODO"""
        super().__init__(parent=parent)

        # Set app
        self.setProgram(blender_app_path.as_posix())

        # Set arguments
        args = ['-b']
        for blend_file in blend_files:
            args.append(blend_file)
            args.append('-a')
        self.setArguments(args)


class UIChecklistDialog(QtWidgets.QDialog):
    """PySide2 Checklist Dialog Widget"""

    def __init__(
        self,
        title: str = '',
        text: str = '',
        items: typing.Iterable[str] = (),
        parent: QtWidgets.QApplication = None,
    ):
        """TODO"""
        super().__init__(parent=parent)

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(False)
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.layout.addRow(QtWidgets.QLabel(text))

        for item in items:
            chbox = QtWidgets.QCheckBox()
            chbox.setProperty('item', item)
            self.layout.addRow(item, chbox)
            self.btn_grp.addButton(chbox)
            chbox.setChecked(True)

        self.btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        self.layout.addWidget(self.btn_box)

        self.setLayout(self.layout)
        self.setWindowTitle(title)

    def get_checked_items(self) -> list:
        """TODO"""
        checked_items = []
        for btn in self.btn_grp.buttons():
            if btn.isChecked():
                checked_items.append(btn.property('item'))

        return checked_items


class UITableModel(QtCore.QAbstractTableModel):
    """TODO"""
    def __init__(
        self,
        rows: typing.Sequence = (),
        header_data: typing.Sequence = (),
        parent: QtCore.QObject = None,
    ):
        """TODO"""
        super().__init__(parent)
        self._rows = rows
        self._header_data = header_data if header_data else [""]*len(rows[0])
        self._column_count = len(self._header_data)
        self._row_count = len(self._rows)
        self._model = QtGui.QStandardItemModel(self)

    def columnCount(self):
        """TODO"""
        return self._column_count

    def data(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        role: int = QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            data = self._rows[index.row()][index.column()]
        elif role in(QtCore.Qt.ToolTipRole, QtCore.Qt.WhatsThisRole):
            data = '?????'
        else:
            data = None

        return data

    def dropMimeData(
        self,
        mime_data: QtCore.QMimeData,
        action: int = QtCore.Qt.DropAction(),
        row: int = -1,
        column: int = -1,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        if action != QtCore.Qt.DropAction.IgnoreAction:
            mime_data_format = 'application/x-qabstractitemmodeldatalist'
            if mime_data.hasFormat(mime_data_format) and parent.isValid():
                byte_array = QtCore.QByteArray(mime_data.data(mime_data_format))
                data_stream = QtCore.QDataStream(byte_array)
                decoded_data = list()
                data_item = dict()
                row = data_stream.readInt32()
                column = data_stream.readInt32()
                map_items = data_stream.readInt32()
                while not data_stream.atEnd():
                    for _ in range(map_items):
                        key = data_stream.readInt32()
                        value = data_stream.readQVariant()
                        data_item[QtCore.Qt.ItemDataRole(key)] = value
                    decoded_data.append(data_item)
                txt = decoded_data[0][QtCore.Qt.DisplayRole]
                original_data = self.data(parent)
                source_index = self.index(row, column)
                self.setData(parent, txt)
                self.setData(source_index, original_data)
                return True
        return False

    def flags(
        self,
        index: QtCore.QModelIndex,
    ):
        """TODO"""
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable | \
               QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsDragEnabled | \
               QtCore.Qt.ItemIsDropEnabled

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal,
        role: int = QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                header_data = self._header_data[section]
            elif orientation == QtCore.Qt.Vertical:
                header_data = f'Row {section + 1:02d}'
        elif role == QtCore.Qt.WhatsThisRole:
            header_data = '?????'
        else:
            header_data = None
        return header_data

    def insertColumns(
        self,
        first_column: int,
        total_columns: int = 1,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> bool:
        """TODO"""
        last_column = first_column + total_columns - 1
        self.beginInsertColumns(index, first_column, last_column)

        for col in range(first_column, last_column + 1):
            self._header_data.insert(col, '')
            for row in self._rows:
                row.insert(col, '')
            self._column_count += 1

        self.endInsertColumns()

        return True

    def insertRows(
        self,
        first_row: int,
        total_rows: int = 1,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        last_row = first_row + total_rows - 1
        self.beginInsertRows(index, first_row, last_row)
        for row in range(first_row, last_row + 1):
            self._rows.insert(row, [''] * self._column_count)
            self._row_count += 1
        self.endInsertRows()
        return True

    def removeColumns(
        self,
        first_column: int,
        total_columns:int = 1,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        last_column = first_column + total_columns - 1
        self.beginRemoveColumns(index, first_column, last_column)
        del self._header_data[first_column : last_column + 1]
        for row in self._rows:
            del row[first_column : last_column + 1]
        self._column_count -= total_columns
        self.endRemoveColumns()
        return True

    def removeRows(
        self,
        first_row: int,
        total_rows: int = 1,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        last_row = first_row + total_rows - 1
        self.beginRemoveRows(index, first_row, last_row)
        del self._rows[first_row : last_row + 1]
        self._row_count -= total_rows
        self.endRemoveRows()
        return True

    def rowCount(self):
        """TODO"""
        return self._row_count

    def setData(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        value: object | type[None] = None,
        role: int = QtCore.Qt.EditRole,
    ):
        """TODO"""
        if any((role != QtCore.Qt.EditRole, not index.isValid(), not value)):
            return False
        self._rows[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def supportedDropActions(self):
        """TODO"""
        return QtCore.Qt.DropAction | QtCore.Qt.MoveAction | QtCore.Qt.CopyAction


class UITreeModelItem(list):
    """TODO"""
    def __init__(
        self,
        data: typing.Sequence,
        parent: typing.Sequence | None = None,
    ):
        """TODO"""
        super().__init__(data)
        self._children = []
        self._parent = parent

    def appendChildItem(
        self,
        tree_item: 'UITreeModelItem',
    ):
        """TODO"""
        return self._children.append(tree_item)

    def child(
        self,
        row: int,
    ):
        """TODO"""
        try:
            return self._children[row]
        except IndexError:
            return None

    def children(self):
        """TODO"""
        return self._children

    def childCount(self):
        """TODO"""
        return len(self._children)

    def columnCount(self):
        """TODO"""
        return len(self)

    def data(
        self,
        col: int,
    ):
        """TODO"""
        return str(self[col]) if col < self.columnCount() else None

    def parent(self):
        """TODO"""
        return self._parent

    def row(self) -> int:
        """TODO"""
        return self.parent().children().index(self) if self.parent() else 0


class UITreeModel(QtCore.QAbstractItemModel):
    """TODO"""
    MODEL_ITEM_TYPE = UITreeModelItem

    def __init__(
        self,
        header_columns: list[str] | tuple[str] = ('',),
        parent: QtWidgets.QApplication | None = None,
    ):
        """
        self.setModelData(data_dict, self._root_item)
        """
        super().__init__(parent)
        self._col_count = len(header_columns)
        self._root_item = self.MODEL_ITEM_TYPE(header_columns)


    def columnCount(
        self,
        parent=QtCore.QModelIndex(),
    ):
        """TODO"""
        if not parent.isValid():
            return self._root_item.columnCount()
        return parent.internalPointer().columnCount()

    def data(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
        role: int = QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if index.isValid() and (role == QtCore.Qt.DisplayRole):
            return index.internalPointer().data(index.column())

        return None

    def flags(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """TODO"""
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(
        self,
        section: int,
        orientation=QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if all((orientation == QtCore.Qt.Horizontal, role == QtCore.Qt.DisplayRole)):
            return self._root_item.data(section)

        return None

    def index(
        self,
        row: int,
        col: int,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> QtCore.QModelIndex:
        """TODO"""
        if not self.hasIndex(row, col, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, col, child_item)

        return QtCore.QModelIndex()

    def parent(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> QtCore.QModelIndex:
        """TODO"""
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()
        if parent_item == self._root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(
        self,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> int:
        """TODO"""
        if parent.column() > 0:
            return 0
        elif not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.childCount()

    def setModelData(
        self,
        data: typing.Iterable,
        parent: 'UITreeModelItem' = None,
    ):
        """TODO"""
        parent = parent if parent else self._root_item

        if isinstance(data, typing.Mapping):
            for key, val in sorted(data.items()):
                data_items = [None] * self._col_count
                data_items[0] = key
                tree_item = self.MODEL_ITEM_TYPE(data_items, parent)
                parent.appendChildItem(tree_item)
                self.setModelData(val, tree_item)

        elif isinstance(data, typing.Sequence):
            tree_item = self.MODEL_ITEM_TYPE(data, parent)
            parent.appendChildItem(tree_item)


def ui_get_app() -> QtWidgets.QApplication:
    """TODO"""
    return \
        QtWidgets.QApplication.instance() if QtWidgets.QApplication.instance() \
        else QtWidgets.QApplication(sys.argv)


def ui_get_checklist(
    title: str = '',
    text: str = '',
    items: typing.Sequence = (),
    parent: QtWidgets.QApplication = None,
) -> list:
    """TODO"""
    _ = ui_get_app()
    checklist_dialog = UIChecklistDialog(
        title,
        text,
        items,
        parent,
    )
    checklist_dialog.exec_()

    return checklist_dialog.get_checked_items()


def ui_get_directory(
    caption: str = '',
    dir_str: str = '',
    parent: QtWidgets.QApplication = None,
) -> pathlib.Path | None:
    """TODO"""
    _ = ui_get_app()
    result = QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        caption,
        dir_str,
    )

    return pathlib.Path(result) if result else None


def ui_get_file(
    caption: str = '',
    dir_str: str = '',
    filter_str: str = 'All Files (*.*)',
    select_multiple: bool = False,
    parent: QtWidgets.QApplication = None,
) -> pathlib.Path | list:
    """TODO"""
    _ = ui_get_app()

    if select_multiple:
        results, success = QtWidgets.QFileDialog.getOpenFileNames(
            parent,
            caption,
            dir_str,
            filter_str,
        )
        return [pathlib.Path(result) for result in results] if success else None

    else:
        result, success = QtWidgets.QFileDialog.getOpenFileName(
            parent,
            caption,
            dir,
            filter,
        )
        return pathlib.Path(result) if success else None


def ui_get_int(
    title: str = '',
    label: str = '',
    value: int = 0,
    min_value: int = 0,
    max_value: int = 9999,
    step: int = 1,
    parent: QtWidgets.QApplication = None,
) -> int | None:
    """TODO"""
    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getInt(
        parent,
        title,
        label,
        value=value,
        minValue=min_value,
        maxValue=max_value,
        step=step,
    )

    return result if success else None


def ui_get_item(
    title: str = '',
    label: str = '',
    items: typing.Sequence = (),
    default_item: str = '',
    editable: bool = False,
    parent: QtWidgets.QApplication = None,
) -> str | None:
    """TODO"""
    current = items.index(default_item) if default_item in items else 0

    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getItem(
        parent,
        title,
        label,
        items,
        current=current,
        editable=editable,
    )

    return result if success else None


def ui_get_text(
    title: str = '',
    label: str = '',
    text: str = '',
    parent: QtWidgets.QApplication = None,
) -> str | None:
    """TODO"""
    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getText(
        parent,
        title,
        label,
        text=text,
    )

    return result if success else None


def ui_launch_dialog(
    cls: typing.Type[QtWidgets.QDialog] | typing.Type[QtWidgets.QMainWindow],
    parent: QtWidgets.QApplication = None,
):
    """TODO"""
    _ = ui_get_app()
    ui_dialog = cls(parent)
    ui_dialog.exec_()

    return ui_dialog


def ui_message_box(
    title: str = '',
    text: str = '',
    message_box_type: str = 'about',
    parent: QtWidgets.QApplication = None,
) -> bool:
    """TODO"""
    message_box_types = {
        'about': QtWidgets.QMessageBox.about,
        'critical': QtWidgets.QMessageBox.critical,
        'information': QtWidgets.QMessageBox.information,
        'question': QtWidgets.QMessageBox.question,
        'warning': QtWidgets.QMessageBox.warning,
    }
    _ = ui_get_app()
    message_box = message_box_types.get(message_box_type, message_box_types['about'])
    result = message_box(parent, title, text)

    return bool(
        result in (
            None,
            QtWidgets.QMessageBox.StandardButton.Ok,
            QtWidgets.QMessageBox.StandardButton.Yes,
        )
    )
