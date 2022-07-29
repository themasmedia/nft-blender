#!$BLENDER_PATH/python/bin python

"""
NFT Blender - QT - OS

"""

import pathlib
import typing

from PySide6 import QtCore, QtWidgets
# from __feature__ import snake_case, true_property


class OSBlenderProcess(QtCore.QProcess):
    """
    System process for batch rendering with Blender locally.
    """

    def __init__(
        self,
        blender_app_path = pathlib.Path | str,
        blend_files: typing.Iterable[str] = (),
        parent: QtWidgets.QApplication = None,
    ) -> None:
        """
        Constructor method

        :param blender_app_path: Path to the installed Blender application.
        :param blend_files: Blender scene files (.blend) to render.
        :param parent: Parent application for the widget.
        """
        super().__init__(parent=parent)

        # Set app
        self.setProgram(blender_app_path.as_posix())

        # Set arguments
        args = ['-b']
        for blend_file in blend_files:
            args.append(blend_file)
            args.append('-a')
        self.setArguments(args)
