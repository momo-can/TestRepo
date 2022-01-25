# -*- coding: utf-8 -*-
import sys
import re

from maya import cmds

sys.dont_write_bytecode = True


def main(**kwargs):
    namespace = kwargs.get('namespace', '')
    objects = cmds.ls(sl=True) or []
    results = []
    for obj in objects:
        name = obj
        if namespace:
            if not re.search(namespace, name):
                continue
        if re.search(':', obj):
            name = obj.split(':')[-1]
        results.append(name)
    return results
