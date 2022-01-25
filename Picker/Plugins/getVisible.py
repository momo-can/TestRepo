# -*- coding: utf-8 -*-
import sys

from maya import cmds

sys.dont_write_bytecode = True


def main(*args, **kwargs):
    name = kwargs.get('name', '')
    if not cmds.objExists(name) or not name:
        return False
    attribute = kwargs.get('attribute', '')
    if not cmds.attributeQuery(attribute, n=name, ex=True) or not attribute:
        return False
    plug = '.'.join([name, attribute])
    visible = cmds.getAttr(plug)
    return int(visible)
