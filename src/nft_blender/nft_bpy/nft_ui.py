#!$BLENDER_PATH/python/bin python

import pathlib
import sys

import bpy


from PySide2 import QtCore, QtWidgets


class UI_BlenderProcess(QtCore.QProcess):
    """"""

    def __init__(
        self,
        blend_files: list = [],
        parent: QtWidgets.QApplication = None,
    ):
        """"""
        super().__init__(parent=parent)

        # Set app
        blender_app_path = pathlib.Path(bpy.app.binary_path)
        self.setProgram(blender_app_path.as_posix())

        # Set arguments
        args = ['-b']
        for blend_file in blend_files:
            args.append(blend_file)
            args.append('-a')
        self.setArguments(args)


class UI_ChecklistDialog(QtWidgets.QDialog):
    """PySide2 Checklist Dialog Widget"""
    
    def __init__(
        self,
        title: str = '',
        text: str = '',
        items: list = [],
        parent: QtWidgets.QApplication = None,
    ):
        """"""
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


    # def accept(self):
    #     """"""
    #     super().accept()
    

    def get_checked_items(self) -> list:
        """"""
        checked_items = []
        for btn in self.btn_grp.buttons():
            if btn.isChecked():
                checked_items.append(btn._item)

        return checked_items


def ui_get_app() -> QtWidgets.QApplication:
    """"""
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    return qapp


def ui_get_checklist(
    title: str = '',
    text: str = '',
    items: list = [],
    parent: QtWidgets.QApplication = None,
) -> list:
    """"""
    _ = ui_get_app()
    checklist_dialog = UI_ChecklistDialog(
        title,
        text,
        items,
        parent,
    )
    checklist_dialog.exec_()

    return checklist_dialog.get_checked_items()


def ui_get_directory(
    caption: str = '',
    dir: str = '',
    parent: QtWidgets.QApplication = None,
) -> pathlib.Path | None:
    """"""
    _ = ui_get_app()
    result = QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        caption,
        dir,
    )

    return pathlib.Path(result) if result else None


def ui_get_file(
    caption: str = '',
    dir: str = '',
    filter: str = 'All Files (*.*)',
    select_multiple: bool = False,
    parent: QtWidgets.QApplication = None,
) -> pathlib.Path | list:
    """"""
    _ = ui_get_app()
    
    if select_multiple:
        results, success = QtWidgets.QFileDialog.getOpenFileNames(
            parent,
            caption,
            dir,
            filter,
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
    minValue: int = 0,
    maxValue: int = 9999,
    step: int = 1,
    parent: QtWidgets.QApplication = None,
) -> int | None:
    """"""
    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getInt(
        parent,
        title,
        label,
        value=value,
        minValue=minValue,
        maxValue=maxValue,
        step=step,
    )

    return result if success else None


def ui_get_item(
    title: str = '',
    label: str = '',
    items: list = [],
    default_item: str = '',
    editable: bool = False,
    parent: QtWidgets.QApplication = None,
) -> str | None:
    """"""
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
    """"""
    _ = ui_get_app()
    result, success = QtWidgets.QInputDialog.getText(
        parent,
        title,
        label,
        text=text,
    )

    return result if success else None


def ui_message_box(
    title: str = '',
    text: str = '',
    message_box_type: str = 'about',
    parent: QtWidgets.QApplication = None,
) -> bool:
    """"""
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

    if result in(
        None,
        QtWidgets.QMessageBox.StandardButton.Ok,
        QtWidgets.QMessageBox.StandardButton.Yes,
    ):
        return True
    else:
        return False


def ui_set_workspace(
    workspace_name: str, 
):
    """"""
    bpy.context.window.workspace = bpy.data.workspaces.get(workspace_name) or bpy.context.window.workspace
