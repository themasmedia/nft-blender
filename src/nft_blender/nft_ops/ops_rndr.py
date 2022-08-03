#!$BLENDER_PATH/python/bin python

"""
NFT Blender - OPS - Render

"""

from nft_blender.nft_qt import qt_os, qt_ui


def rndr_batch_render() -> None:
    """
    Renders the selected Blender file(s) in a detached local process (not meant for production).
    """
    batch_render_dir_path = qt_ui.ui_get_directory(
        caption='Select directory with files to batch render',
    )
    if batch_render_dir_path.is_dir():
        batch_render_file_paths = [f.as_posix() for f in batch_render_dir_path.glob('*.blend')]

        ui_blender_process = qt_os.OSBlenderProcess(blend_files=batch_render_file_paths)
        ui_blender_process.startDetached()
