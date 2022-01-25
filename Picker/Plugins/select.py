# -*- coding: utf-8 -*-
import sys
import copy

from maya import cmds

sys.dont_write_bytecode = True


def main(nodes=[], **kwargs):
    args = []
    selected = cmds.ls(sl=True, l=True) or []
    isRestore = kwargs.get('isRestore', False)
    if selected and isRestore:
        args = copy.deepcopy(selected)
    if 'isRestore' in kwargs.keys():
        kwargs.pop('isRestore')
    for n in nodes:
        if not cmds.objExists(n):
            continue
        args.append(n)
    cmds.select(*args, **kwargs)
