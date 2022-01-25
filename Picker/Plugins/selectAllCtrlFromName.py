# -*- coding: utf-8 -*-
import sys

from maya import cmds

sys.dont_write_bytecode = True


def main(namespace='', **kwargs):
    sets = 'controllerSets'
    if namespace:
        sets = ':'.join([namespace, sets])
    if not cmds.objExists(sets):
        return
    cmds.select(sets, **kwargs)
