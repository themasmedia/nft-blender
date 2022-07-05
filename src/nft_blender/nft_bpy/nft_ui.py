#!$BLENDER_PATH/python/bin python

import pathlib
import sys
import typing

from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets


class UIDialogBase(QtWidgets.QDialog):
    """TODO"""
    _UI_FILE_PATH = ''

    def __init__(
        self,
        parent: QtWidgets.QApplication = None,
    ):
        """TODO"""
        super().__init__(parent=parent)
        self._ui_setup()
        self._connect_widgets()

    def _connect_widgets(self):
        """TODO"""
        raise NotImplementedError

    def _ui_setup(self):
        """TODO"""
        self._ui = QtUiTools.QUiLoader().load(self._ui_file_path.as_posix())
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self._ui)
        self.setLayout(self._layout)

    @classmethod
    @property
    def _ui_file_path(cls) -> pathlib.Path:
        """TODO"""
        ui_file_path = pathlib.Path(cls._UI_FILE_PATH)
        assert ui_file_path.exists() and ui_file_path.suffix == '.ui'
        return ui_file_path


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
            cb = QtWidgets.QCheckBox()
            cb._item = item
            self.layout.addRow(item, cb)
            self.btn_grp.addButton(cb)
            cb.setChecked(True)

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
                checked_items.append(btn._item)

        return checked_items


class TableModel(QtCore.QAbstractTableModel):
    """TODO"""
    def __init__(
        self,
        rows: typing.Sequence = (),
        header_data: typing.Sequence = (),
        parent=None,
        *args,
    ):
        """TODO"""
        super().__init__(parent, *args)
        self._rows = rows
        self._header_data = header_data if header_data else [""]*len(rows[0])
        self._column_count = len(self._header_data)
        self._row_count = len(self._rows)
        self._model = QtGui.QStandardItemModel(self)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """TODO"""
        return self._column_count

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        """TODO"""
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            data = self._rows[index.row()][index.column()]
        elif role in(QtCore.Qt.ToolTipRole, QtCore.Qt.WhatsThisRole):
            data = '?????'
        else:
            data = None
        return data

    def dropMimeData(self, mime_data, action=QtCore.Qt.DropAction, row=-1, column=-1, parent=QtCore.QModelIndex()):
        """TODO"""
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist") and parent.isValid():
            byte_array = QtCore.QByteArray(mime_data.data("application/x-qabstractitemmodeldatalist"))
            data_stream = QtCore.QDataStream(byte_array)
            decoded_data = list()
            data_item = dict()
            row = data_stream.readInt32()
            column = data_stream.readInt32()
            map_items = data_stream.readInt32()
            while not data_stream.atEnd():
                for i in range(map_items):
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

    def flags(self, index):
        """TODO"""
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable | \
               QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsDragEnabled | \
               QtCore.Qt.ItemIsDropEnabled

    def headerData(self, section, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
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

    def insertColumns(self, first_column, total_columns=1, index=QtCore.QModelIndex()):
        """TODO"""
        lastColumn = first_column + total_columns - 1
        self.beginInsertColumns(index, first_column, lastColumn)
        for i, c in enumerate(range(first_column, lastColumn+1)):
            self._header_data.insert(c, "")
            for row in self._rows:
                row.insert(c, "")
            self._column_count += 1
        self.endInsertColumns()
        return True

    def insertRows(self, first_row, total_rows=1, index=QtCore.QModelIndex()):
        """TODO"""
        last_row = first_row + total_rows - 1
        self.beginInsertRows(index, first_row, last_row)
        for i, r in enumerate(range(first_row, last_row+1)):
            self._rows.insert(r, ["" for i in range(self._column_count)])
            self._row_count += 1
        self.endInsertRows()
        return True

    def removeColumns(self, first_column, total_columns=1,  index=QtCore.QModelIndex()):
        """TODO"""
        lastColumn = first_column + total_columns - 1
        self.beginRemoveColumns(index, first_column, lastColumn)
        del self._header_data[first_column : lastColumn + 1]
        for row in self._rows:
            del row[first_column : lastColumn + 1]
        self._column_count -= total_columns
        self.endRemoveColumns()
        return True

    def removeRows(self, first_row, total_rows=1, index=QtCore.QModelIndex()):
        """TODO"""
        last_row = first_row + total_rows - 1
        self.beginRemoveRows(index, first_row, last_row)
        del self._rows[first_row : last_row + 1]
        self._row_count -= total_rows
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        """TODO"""
        return self._row_count

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """TODO"""
        if any((role != QtCore.Qt.EditRole, not index.isValid(), not value)):
            return False
        self._rows[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def supportedDropActions(self):
        """TODO"""
        return QtCore.Qt.DropAction | QtCore.Qt.MoveAction | QtCore.Qt.CopyAction


class UITreeModel(QtCore.QAbstractItemModel):
    """TODO"""
    def __init__(
        self,
        header_columns: list | tuple = (),
        display_data_function: typing.Callable | None = None,
        parent: QtWidgets.QApplication | None = None,
    ):
        """
        self.setModelData(data_dict, self._root_item)
        """
        super().__init__(parent)
        self._col_count = len(header_columns)
        self._func = display_data_function
        self._root_item = UI_TreeItem(header_columns)

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
        role=QtCore.Qt.DisplayRole,
    ):
        """TODO"""
        if any((not index.isValid(), role != QtCore.Qt.DisplayRole)):
            return None
        return index.internalPointer().data(index.column())

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
        section,
        orientation=QtCore.Qt.Orientation,
        role=QtCore.Qt.DisplayRole
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
    ):
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
    ):
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
        data,
        parent=None,
    ):
        """TODO"""
        parent = parent if parent else self._root_item
        for k, v in sorted(data.items(), key=lambda k: k):
            data_items = ['' for i in range(self._col_count)]
            data_items[0] = k
            if isinstance(v, dict):
                tree_item = UI_TreeItem(data_items, parent)
                parent.appendChildItem(tree_item)
                self.setModelData(v, tree_item)
            else:
                if len(data_items) > 1:
                    data_items[-1] = v
                tree_item = UI_TreeItem(data_items, parent, self._func)
                parent.appendChildItem(tree_item)
        return True


class UITreeItem(object):
    """TODO"""
    def __init__(
        self,
        data: list | tuple = (),
        display_data_function: typing.Callable | None = None,
        parent: QtWidgets.QApplication | None = None,
    ):
        """TODO"""
        self._func = display_data_function
        self._item_data = data
        self._parent_item = parent
        self._child_items = list()

    def appendChildItem(
        self,
        tree_item: 'UI_TreeItem',
    ):
        """TODO"""
        return self._child_items.append(tree_item)

    def child(self, row: int,):
        """TODO"""
        return self._child_items[row]

    def childCount(self):
        """TODO"""
        return len(self._child_items)

    def columnCount(self):
        """TODO"""
        return len(self._item_data)

    def data(self, col,):
        """TODO"""
        if col < self.columnCount():
            if isinstance(self._item_data[col], str):
                return self._item_data[col]
            elif self._func:
                return self._func(self._item_data[col])

        return None

    def parent(self):
        """TODO"""
        return self._parent_item

    def row(self) -> int:
        """TODO"""
        if self.parent():
            return self.parent()._child_items.index(self)

        return 0


def ui_get_app() -> QtWidgets.QApplication:
    """TODO"""
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    return qapp


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
