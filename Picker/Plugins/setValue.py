# -*- coding: utf-8 -*-
import sys
from pprint import pprint

from maya import cmds

sys.dont_write_bytecode = True


def main(**kwargs):
    name = kwargs.get('name', '')
    namespace = kwargs.get('namespace', None)
    if namespace:
        name = ':'.join([
            namespace,
            name
        ])
    if not cmds.objExists(name) or not name:
        return None
    attribute = kwargs.get('attribute', '')
    if not cmds.attributeQuery(attribute, n=name, ex=True) or not attribute:
        return None
    plug = '.'.join([name, attribute])
    value = kwargs.get('value', None)
    if value is None:
        return
    args = (plug, value)
    kwargs = kwargs.get('flags', {})
    cmds.setAttr(*args, **kwargs)
