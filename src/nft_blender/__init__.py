#!$BLENDER_PATH/python/bin python

"""
init.py: Load the nft-blender Python module.

import pathlib
import site


user_site = pathlib.Path(site.getusersitepackages())
if str(user_site) not in site.getsitepackages():
    site.addsitedir(str(user_site))

import nft_blender
"""

__author__      = 'masangri.eth'
__copyright__   = 'Copyright 2022'
__credits__     = ['Mas']
__email__       = "masangri.art@gmail.com"
__license__     = "MIT"
__maintainer__  = "Mas"
__status__      = "Beta"
__version__     = "0.0.1"
