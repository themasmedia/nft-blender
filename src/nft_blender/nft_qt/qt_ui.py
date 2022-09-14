#!$BLENDER_PATH/python/bin python

"""
NFT Blender - QT - UI

"""

import pathlib
import sys
import typing

from PySide6 import QtCore, QtGui, QtUiTools, QtWidgets
# from __feature__ import snake_case, true_property


class UIDialogBase(QtWidgets.QDialog):
    """
    Abstract base class for Dialog Box UI generated from a Qt Designer .ui file.
    Class must be extended with class variables set.
    """
    #: Name of the .ui file (String)
    _UI_FILE_NAME = ''
    #: Name of the window (String)
    _UI_WINDOW_TITLE = ''

    def __init__(
        self,
        modality: bool = True,
        parent: QtCore.QObject = None,
    ) -> None:
        """
        Constructor method.

        :param modality: If True, the widget will be modal (default: True).
        :param parent: Parent object (Application, UI Widget, etc.).
        """
        super().__init__(parent=parent)

        self._ui = QtUiTools.QUiLoader().load(self._ui_file_path.as_posix())
        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self._ui)
        self.setLayout(self._layout)

        self.setModal(modality)
        self._ui.setModal(modality)

        self.setWindowTitle(self._ui_window_title)

        self._set_up_ui()

    def _set_up_ui(self) -> None:
        """
        Abstract method for additional UI set-up. Must be defined in the derived class.
        """
        raise NotImplementedError

    @classmethod
    @property
    def _ui_file_path(cls) -> pathlib.Path:
        """
        Verifies and returns the UI file path as a Path object.

        :returns: A Path object.
        """
        ui_dir_path = pathlib.Path(__file__).parent
        ui_file_path = ui_dir_path.joinpath(cls._UI_FILE_NAME)
        assert ui_file_path.exists() and ui_file_path.suffix == '.ui'

        return ui_file_path

    @classmethod
    @property
    def _ui_window_title(cls) -> str:
        """
        Verifies and returns the title for the Dialog Box UI.

        :returns: The window title.
        """
        assert len(cls._UI_WINDOW_TITLE) > 0

        return cls._UI_WINDOW_TITLE


class UIChecklistDialog(QtWidgets.QDialog):
    """
    Simple Dialog Box UI with a list of checkable options.
    """

    def __init__(
        self,
        title: str = '',
        text: str = '',
        items: typing.Iterable[str] = (),
        parent: QtCore.QObject = None,
    ) -> None:
        """
        Constructor method.

        :param title: Title of the Dialog Box UI.
        :param text: User instructions.
        :param items: List of items for the user to check (non-exclusive).
        :param parent: Parent object (Application, UI Widget, etc.).
        """
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
        """
        Gets the property values of all checked items..

        :returns: A list of checked item values.
        """
        checked_items = []
        for btn in self.btn_grp.buttons():
            if btn.isChecked():
                checked_items.append(btn.property('item'))

        return checked_items


# class UITableModel(QtCore.QAbstractTableModel):
#     """
#     Table model class.
#     """
#     def __init__(
#         self,
#         rows: typing.Sequence = (),
#         header_columns: typing.Sequence = (),
#         parent: QtCore.QObject = None,
#     ):
#         """
#         Constructor method.

#         :param rows: List of rows.
#         :param header_columns: List of column names.
#         :param parent: Parent object (Application, UI Widget, etc.).
#         """
#         super().__init__(parent)
#         self._rows = rows
#         self._header_data = header_columns if header_columns else [""]*len(rows[0])
#         self._column_count = len(self._header_data)
#         self._row_count = len(self._rows)
#         self._model = QtGui.QStandardItemModel(self)

#     def columnCount(self):
#         """"""
#         return self._column_count

#     def data(
#         self,
#         index: QtCore.QModelIndex = QtCore.QModelIndex(),
#         role: int = QtCore.Qt.DisplayRole,
#     ):
#         """"""
#         if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
#             data = self._rows[index.row()][index.column()]
#         elif role in(QtCore.Qt.ToolTipRole, QtCore.Qt.WhatsThisRole):
#             data = '?????'
#         else:
#             data = None

#         return data

#     def dropMimeData(
#         self,
#         mime_data: QtCore.QMimeData,
#         action: int = QtCore.Qt.DropAction(),
#         row: int = -1,
#         column: int = -1,
#         parent: QtCore.QModelIndex = QtCore.QModelIndex(),
#     ):
#         """"""
#         if action != QtCore.Qt.DropAction.IgnoreAction:
#             mime_data_format = 'application/x-qabstractitemmodeldatalist'
#             if mime_data.hasFormat(mime_data_format) and parent.isValid():
#                 byte_array = QtCore.QByteArray(mime_data.data(mime_data_format))
#                 data_stream = QtCore.QDataStream(byte_array)
#                 decoded_data = list()
#                 data_item = dict()
#                 row = data_stream.readInt32()
#                 column = data_stream.readInt32()
#                 map_items = data_stream.readInt32()
#                 while not data_stream.atEnd():
#                     for _ in range(map_items):
#                         key = data_stream.readInt32()
#                         value = data_stream.readQVariant()
#                         data_item[QtCore.Qt.ItemDataRole(key)] = value
#                     decoded_data.append(data_item)
#                 txt = decoded_data[0][QtCore.Qt.DisplayRole]
#                 original_data = self.data(parent)
#                 source_index = self.index(row, column)
#                 self.setData(parent, txt)
#                 self.setData(source_index, original_data)
#                 return True
#         return False

#     def flags(
#         self,
#         index: QtCore.QModelIndex,
#     ):
#         """"""
#         if not index.isValid():
#             return QtCore.Qt.ItemIsEnabled
#         return QtCore.Qt.ItemIsEnabled | \
#                QtCore.Qt.ItemIsSelectable | \
#                QtCore.Qt.ItemIsEditable | \
#                QtCore.Qt.ItemIsDragEnabled | \
#                QtCore.Qt.ItemIsDropEnabled

#     def headerData(
#         self,
#         section: int,
#         orientation: QtCore.Qt.Orientation = QtCore.Qt.Horizontal,
#         role: int = QtCore.Qt.DisplayRole,
#     ):
#         """"""
#         if role == QtCore.Qt.DisplayRole:
#             if orientation == QtCore.Qt.Horizontal:
#                 header_data = self._header_data[section]
#             elif orientation == QtCore.Qt.Vertical:
#                 header_data = f'Row {section + 1:02d}'
#         elif role == QtCore.Qt.WhatsThisRole:
#             header_data = '?????'
#         else:
#             header_data = None
#         return header_data

#     def insertColumns(
#         self,
#         first_column: int,
#         total_columns: int = 1,
#         index: QtCore.QModelIndex = QtCore.QModelIndex(),
#     ) -> bool:
#         """"""
#         last_column = first_column + total_columns - 1
#         self.beginInsertColumns(index, first_column, last_column)

#         for col in range(first_column, last_column + 1):
#             self._header_data.insert(col, '')
#             for row in self._rows:
#                 row.insert(col, '')
#             self._column_count += 1

#         self.endInsertColumns()

#         return True

#     def insertRows(
#         self,
#         first_row: int,
#         total_rows: int = 1,
#         index: QtCore.QModelIndex = QtCore.QModelIndex(),
#     ):
#         """"""
#         last_row = first_row + total_rows - 1
#         self.beginInsertRows(index, first_row, last_row)
#         for row in range(first_row, last_row + 1):
#             self._rows.insert(row, [''] * self._column_count)
#             self._row_count += 1
#         self.endInsertRows()
#         return True

#     def removeColumns(
#         self,
#         first_column: int,
#         total_columns:int = 1,
#         index: QtCore.QModelIndex = QtCore.QModelIndex(),
#     ):
#         """"""
#         last_column = first_column + total_columns - 1
#         self.beginRemoveColumns(index, first_column, last_column)
#         del self._header_data[first_column : last_column + 1]
#         for row in self._rows:
#             del row[first_column : last_column + 1]
#         self._column_count -= total_columns
#         self.endRemoveColumns()
#         return True

#     def removeRows(
#         self,
#         first_row: int,
#         total_rows: int = 1,
#         index: QtCore.QModelIndex = QtCore.QModelIndex(),
#     ):
#         """"""
#         last_row = first_row + total_rows - 1
#         self.beginRemoveRows(index, first_row, last_row)
#         del self._rows[first_row : last_row + 1]
#         self._row_count -= total_rows
#         self.endRemoveRows()
#         return True

#     def rowCount(self):
#         """"""
#         return self._row_count

#     def supportedDropActions(self):
#         """"""
#         return QtCore.Qt.DropAction | QtCore.Qt.MoveAction | QtCore.Qt.CopyAction


class UITreeModelItem(list):
    """
    Tree Model Item class for objects in tree model objects.
    """
    def __init__(
        self,
        data: typing.Sequence,
        parent: QtCore.QObject = None,
    ) -> None:
        """
        Constructor method.

        :param data: List of column values.
        :param parent: Parent object (Application, UI Widget, etc.).
        """
        super().__init__(data)
        self._children = []
        self._parent = parent

    def child(
        self,
        row: int,
    ) -> 'UITreeModelItem':
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        try:
            return self._children[row]

        except IndexError:
            return None

    def children(self) -> list:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return self._children

    def childCount(self) -> int:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return len(self._children)

    def columnCount(self) -> int:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return len(self)

    def data(
        self,
        col: int,
    ) -> object:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return self[col] if col < self.columnCount() else None

    def insertChildren(
        self,
        tree_items: typing.Sequence['UITreeModelItem'],
        pos: int = -1,
        sort: bool = True,
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if pos > len(self._children):
            return False

        elif pos > 0:
            self._children = self._children[:pos] + tree_items + self._children[pos:]

        else:
            self._children.extend(tree_items)

        if sort:
            self._children.sort(key=lambda k: k[0].lower() if len(k) > 0 else '')

        return True

    def parent(self) -> 'UITreeModelItem':
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return self._parent

    def removeChildren(self, start_pos, count=1):
        """"""
        if (start_pos < 0) or (start_pos + count > self.childCount()):
            return False

        del self._children[start_pos: start_pos + count]

        return True

    def row(self) -> int:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return self.parent().children().index(self) if self.parent() else 0

    def setData(
        self,
        col: int,
        value: object,
    ) -> bool:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if 0 <= col < len(self):
            self[col] = value
            return True

        return False


class UITreeModel(QtCore.QAbstractItemModel):
    """
    Tree Model class.
    """
    #: Tree Model Item class to be used for all child objects.
    MODEL_ITEM_TYPE = UITreeModelItem

    def __init__(
        self,
        header_columns: typing.Iterable[str] = ('',),
        parent: QtCore.QObject = None,
    ):
        """
        Constructor method.

        :param header_columns: List of column names.
        :param parent: Parent object (Application, UI Widget, etc.).
        """
        super().__init__(parent)
        self._root_item = self.MODEL_ITEM_TYPE(header_columns)
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount() - 1)

    def clear(self):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        self.removeRows(0, self.rowCount())
        self.setModelData()

    def columnCount(
        self,
        parent=QtCore.QModelIndex(),
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        return self.getItem(parent).columnCount()

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
        if index.isValid() and (role == QtCore.Qt.DisplayRole):
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

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getItem(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if index.isValid():
            if index.internalPointer():
                return index.internalPointer()

        return self._root_item

    def headerData(
        self,
        section: int,
        orientation=QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if all((orientation == QtCore.Qt.Horizontal, role == QtCore.Qt.DisplayRole)):
            return self._root_item.data(section)

        return None

    def index(
        self,
        row: int,
        col: int,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> QtCore.QModelIndex:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if not self.hasIndex(row, col, parent):
            return QtCore.QModelIndex()

        parent_item = self.getItem(parent)

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, col, child_item)

        return QtCore.QModelIndex()

    def insertRows(
        self,
        pos: int = -1,
        rows: typing.Iterable = (),
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        rows = list(rows)
        if not rows:
            return False

        parent_item = self.getItem(parent)
        if pos < 0:
            pos = parent_item.childCount()

        tree_item_empty = [None] * (self.columnCount() - 1)
        tree_items = [
            self.MODEL_ITEM_TYPE([row] + tree_item_empty, parent_item) for row in rows
        ]

        self.beginInsertRows(parent, pos, pos + len(rows) - 1)
        success = parent_item.insertChildren(tree_items, pos)
        self.endInsertRows()

        return success

    def modelData(
        self,
        col: int = 0,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> dict:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        model_item_data = {}

        for row in range(self.rowCount(parent)):
            child = self.index(row, col, parent)
            if child.isValid():
                model_item_data[self.data(child)] = self.modelData(col, child)

        return model_item_data

    def parent(
        self,
        index: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> QtCore.QModelIndex:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = self.getItem(index)
        parent_item = child_item.parent()
        if parent_item == self._root_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def removeRows(
        self,
        first_row: int,
        total_rows: int = 1,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ):
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        last_row = first_row + total_rows - 1
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()

        self.beginRemoveRows(parent, first_row, last_row)
        parent_item.removeChildren(start_pos=first_row, count=total_rows)
        self.endRemoveRows()

        return True

    def rowCount(
        self,
        parent: QtCore.QModelIndex = QtCore.QModelIndex(),
    ) -> int:
        """
        TODO

        :param TODO:
        :returns: TODO
        """
        if parent.column() > 0:
            return 0

        parent_item = self.getItem(parent)

        return parent_item.childCount()

    def setModelData(
        self,
        data: typing.Iterable = (),
        parent_item: 'UITreeModelItem' = None,
    ):
        """
        TODO self.setModelData(data_dict, self._root_item)

        :param TODO:
        :returns: TODO
        """
        parent_item = parent_item if parent_item else self._root_item
        if parent_item == self._root_item:
            self.beginResetModel()

        if isinstance(data, typing.Mapping):
            for key, val in sorted(data.items()):
                data_items = [None] * self.columnCount()
                data_items[0] = key
                tree_item = self.MODEL_ITEM_TYPE(data_items, parent_item)
                parent_item.insertChildren([tree_item])
                self.setModelData(val, tree_item)

        elif isinstance(data, typing.Sequence):
            tree_item = self.MODEL_ITEM_TYPE(data, parent_item)
            parent_item.insertChildren([tree_item])

        if parent_item == self._root_item:
            self.endResetModel()


def ui_get_app() -> QtWidgets.QApplication:
    """
    Gets the Application instance for the current application environment,
    or creates a new instance if none exist.

    :returns: The Application instance.
    """
    return \
        QtWidgets.QApplication.instance() if QtWidgets.QApplication.instance() \
        else QtWidgets.QApplication(sys.argv)


def ui_get_checklist(
    title: str = '',
    text: str = '',
    items: typing.Sequence = (),
    parent: QtCore.QObject = None,
) -> list:
    """
    Prompts the user with an Checklist Dialog UI with a list of items to choose from.

    :param title: Title of the Checklist Dialog UI.
    :param text: User instructions.
    :param items: List of items to choose from.
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: A list of items that were checked by the user.
    """
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
    parent: QtCore.QObject = None,
) -> pathlib.Path:
    """
    Prompts the user with a File Dialog UI to select a folder.

    :param caption: Title of the File Dialog UI.
    :param dir_str: Directory in which the File Dialog UI will begin.
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The directory Path, if one was selected.
    """
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
    parent: QtCore.QObject = None,
) -> typing.Union[pathlib.Path, list]:
    """
    Prompts the user to select a file(s).

    :param caption: Title of the File Dialog UI.
    :param dir_str: Directory in which the File Dialog UI will begin.
    :param filter_str: File type filter.
    :param select_multiple: If True, multiple file(s) can be selected (default: False).
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The directory Path, if one was selected.
    """
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
    parent: QtCore.QObject = None,
) -> int:
    """
    Prompts the user with an Input Dialog UI to select an integer.

    :param title: Title of the Input Dialog UI.
    :param label: User instructions.
    :param value: Default integer value.
    :param min_value: Lowest permitted integer.
    :param max_value: Highest permitted integer.
    :param step: Increment value for the integer Spin Box.
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The integer selected by the user.
    """
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
    parent: QtCore.QObject = None,
) -> str:
    """
    Prompts the user with an Input Dialog UI with a dropdown list of items to choose from.

    :param title: Title of the Input Dialog UI.
    :param label: User instructions.
    :param items: List of items to choose from.
    :param default_item: Initially selected item.
    :param editable: If True, items can be editted by the user (default: False).
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The selected item.
    """
    if not all((isinstance(item, str) for item in items)):
        item_strings = [repr(item) for item in items]
    else:
        item_strings = items

    current = items.index(default_item) if default_item in item_strings else 0

    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getItem(
        parent,
        title,
        label,
        item_strings,
        current=current,
        editable=editable,
    )

    if success:
        return items[item_strings.index(result)]

    return None


def ui_get_text(
    title: str = '',
    label: str = '',
    text: str = '',
    parent: QtCore.QObject = None,
) -> str:
    """
    Prompts the user with an Input Dialog UI to input text.

    :param title: Title of the Input Dialog UI.
    :param label: User instructions.
    :param text: Default text.
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The text input by the user.
    """
    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getText(
        parent,
        title,
        label,
        text=text,
    )

    return result if success else ''


def ui_launch_dialog(
    cls: typing.Union[QtWidgets.QDialog, QtWidgets.QMainWindow],
    parent: QtCore.QObject = None,
) -> QtWidgets.QDialog:
    """
    Helper function for launching a Dialog Box or Main Window UI instance.

    :param cls: Class of the widget to create an instance of.
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: The UI widget instance.
    """
    _ = ui_get_app()
    ui_dialog = cls(parent)
    ui_dialog.exec_()

    return ui_dialog


def ui_message_box(
    title: str = '',
    text: str = '',
    message_box_type: str = 'about',
    parent: QtCore.QObject = None,
) -> bool:
    """
    Prompts the user with a simple Message Box UI.

    :param title: Title of the Message Box UI.
    :param text: A message for the user.
    :param message_box_type: The name of the Message Box type.
        Options: ['about', 'critical', 'information', 'question', 'warning']
    :param parent: Parent object (Application, UI Widget, etc.).
    :returns: True if the user exited the UI with an accepted status; otherwise False.
    """
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
