# -*- coding: utf-8 -*-
import sys
import os
import json
import re

try:
    from importlib import reload
except Exception:
    pass

from maya import cmds

import stringUtil

sys.dont_write_bytecode = True

reload(stringUtil)

currnetDir = os.path.dirname(__file__)
configRootPath = '/'.join([
    currnetDir.replace(os.sep, '/'),
    'config'
])


def findConfigs(path=''):
    results = []
    if not os.path.isdir(path):
        return results
    for path, dirs, files in os.walk(path):
        for file in files:
            if not re.search('config', file):
                continue
            path = path.replace(os.sep, '/')
            try:
                __configPath = '/'.join([
                    path,
                    file
                ])

                fileId = open(__configPath, 'r')
                data = json.load(fileId)
                fileId.close()

                temp = json.loads(json.dumps(data))
                results += temp
            except Exception:
                pass
    return results


def createMenu():
    projectMenu = getProjectMenu()
    if not projectMenu:
        PROJECT_NAME = os.environ.get('PROJECT_NAME', 'COMMON')
        label = '{}_menu'.format(PROJECT_NAME)
        projectMenu = cmds.menu(
            label,
            l=PROJECT_NAME,
            tearOff=True,
            parent="MayaWindow"
        )
    return projectMenu


def createMenuItem(projectMenu=None):
    if not projectMenu:
        return

    menuList = findConfigs(configRootPath)

    menuInfo = {}
    for menuData in menuList:
        try:
            menuName = menuData.get('name', '')
            flags = menuData.get('flags', {})
            parentName = menuData.get('parent', None)
            flags['parent'] = projectMenu
            if parentName:
                parentItem = menuInfo.get(parentName, None)
                if parentItem:
                    flags['parent'] = parentItem
            if not menuName:
                menuName = stringUtil.stringGenerator(
                    size=10,
                    isStringUppercase=False
                )
            __flags = {}
            for f in flags:
                value = flags.get(f)
                __flags[f.encode('shift_jis')] = value
            menuItem = cmds.menuItem(**__flags)
            menuInfo[menuName] = menuItem
        except Exception:
            pass

    print('Create {}'.format(projectMenu))
    return True


def getProjectMenu():
    PROJECT_NAME = os.environ.get('PROJECT_NAME', 'COMMON')
    projectMenu = '{}_menu'.format(PROJECT_NAME)
    if cmds.menu(projectMenu, exists=True):
        return projectMenu
    else:
        return None


def deleteMenu():
    projectMenu = getProjectMenu()
    if not projectMenu:
        return
    try:
        print('')
        print('Deleted {}'.format(projectMenu))
        cmds.deleteUI(projectMenu)
        return True
    except Exception as err:
        print('')
        print(err)
        return False


def reloadMenu():
    cmds.evalDeferred(reloadMenuDef)


def reloadMenuDef():
    projectMenu = getProjectMenu()
    if projectMenu:
        cmds.menu(projectMenu, edit=True, deleteAllItems=True)
    else:
        projectMenu = createMenu()
    createMenuItem(projectMenu=projectMenu)
