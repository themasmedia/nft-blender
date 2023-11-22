#!$BLENDER_PATH/python/bin python

"""
NFT Blender - CORE - UTIL

"""

import functools
import logging


def util_get_attr_recur(obj, attr, *args):
    """"""
    
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    try:
        return functools.reduce(_getattr, [obj] + attr.split('.'))
    
    except AttributeError as attr_err:
        logging.warning(attr_err)
        return None


def util_set_attr_recur(obj, attr, val):
    """"""

    pre, _, post = attr.rpartition('.')

    attr = util_get_attr_recur(obj, pre) if pre else obj

    try:
        return setattr(attr, post, val)
    
    except AttributeError as attr_err:
        logging.warning(attr_err)
        return None
