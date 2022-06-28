#!$BLENDER_PATH/python/bin python

import logging
import os
import pathlib
import pkgutil
import site
import subprocess
import sys

import bpy


__LOGGER__ = logging.getLogger(__name__)
__LOGGER__.addHandler(logging.StreamHandler(sys.stdout))
__LOGGER__.setLevel(logging.INFO)

# bpy.ops.wm.console_toggle()


MODULES = {
    'nft_blender': {
        'reinstall': True,
        'specifier': 'git+https://github.com/Masangri/nft-blender.git@main#egg=nft-blender',
    },
    # Dependencies (installed automatically with `nft-blender` module):
    'PySide2': {
        'reinstall': False,
        'specifier': 'PySide2',
    },
    'shiboken2': {
        'reinstall': False,
        'specifier': 'shiboken2',
    },
}


def _ensure_pip():
    """Ensure that `pip` is installed (comes preinstalled for Blender 3.x)."""
    __LOGGER__.debug('Checking if pip is installed:\n')
    subprocess.call([sys.executable, '-m', 'ensurepip'])


def _get_user_site() -> pathlib.Path:
    """"""
    return pathlib.Path(site.getusersitepackages())


def install_package(module_name: str) -> bool:
    """"""
    os.system('cls')

    # Retrieve module name and location
    module_data = MODULES.get(module_name, {})
    module_specifier = module_data.get('specifier')

    # Abort if module info isn't found.
    if not module_specifier:
        __LOGGER__.warning(f'`{module_name}` is not a valid option. Aborting!')
        return False

    # Upgrade `pip` if necessary.
    __LOGGER__.debug('Updating pip')
    subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    # Access to Blender's internal site packages might be restricted on Windows.
    # Install package to user's Python site-packages directory instead (same version of Python 3.x recommended).
    user_site = _get_user_site()
    if str(user_site) not in site.getsitepackages():
        __LOGGER__.debug('Adding user\'s `site-packages` directory as potential installation location.')
        site.addsitedir(str(user_site))

    installed_module_names = [mod.name for mod in pkgutil.iter_modules()]
    subprocess_args = [sys.executable, '-m', 'pip', 'install', module_specifier]

    # Install module and dependencies from GitHub repository (branch: `main`), if not already.
    if module_name not in installed_module_names:
        __LOGGER__.debug(f'Installing Python module: `{module_name}`')

    # Update module and dependencies.
    else:
        __LOGGER__.debug(f'Updating Python module: `{module_name}`')
        if module_data.get('reinstall'):
            subprocess_args.append('--force-reinstall')
        subprocess_args.append('--upgrade')

    subprocess.call(subprocess_args)

    __LOGGER__.info(
        '\n\nPlease create the following user environment variable:\n'
        f'PYTHONPATH="{str(user_site)}"\n'
    )

    return True


def uninstall_package(module_name: str) -> bool:
    """"""
    # Uninstall module and dependencies, if they are installed.
    installed_module_names = [mod.name for mod in pkgutil.iter_modules()]
    if module_name in installed_module_names:
        __LOGGER__.debug(f'Uninstalling Python module: `{module_name}`')
        subprocess.call([sys.executable, '-m', 'pip', 'uninstall', '-y', module_name])

        return True

    return False


if __name__ == '__main__':

    install_package('nft_blender')
