# -*- coding: utf-8 -*-
import sys
import re

try:
    from maya import cmds
except Exception:
    pass

sys.dont_write_bytecode = True


def selectAssetFromNode(names=[]):
    result = 0
    if not names:
        return result

    nodes = cmds.ls(sl=True) or []
    if not nodes:
        return result

    namespace = nodes[0].split(':')[0]
    for i, name in enumerate(names):
        if not re.search(':', nodes[0]):
            break
        if namespace not in [name]:
            continue
        result = i
        break
    return result


def getReferenceNamespace():
    try:
        items = cmds.ls(typ='reference') or []
        result = ['']
        for i, item in enumerate(items):
            try:
                ns = cmds.referenceQuery(
                    item,
                    namespace=True
                )
                ns = re.sub('^:', '', ns)
                result.append(ns)
            except Exception:
                pass
    except Exception:
        return []
    result = list(set(result))
    result.sort()
    return result
