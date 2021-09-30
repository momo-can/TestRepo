# -*- coding: utf-8 -*-
import sys
import re
import os
import json
import glob

from pprint import pprint

from maya import cmds
from maya import mel

sys.dont_write_bytecode = True


def getExportConfig(configName=''):
    currentPath = os.path.dirname(__file__)
    currentPath = currentPath.replace(os.sep, '/')
    configPath = '/'.join([
        currentPath,
        'presets',
        configName
    ])

    if not configPath:
        return []

    fileId = open(configPath, 'r')
    data = json.load(fileId)
    fileId.close()

    return data


def setFbxSettings(**userInputs):
    if not userInputs:
        return

    results = []

    settings = userInputs.get('settings', [])
    optionVars = userInputs.get('optionVars', {})

    for setting in settings:
        print('-' * 30)
        print(setting)
        print('-' * 30)
        itemPath = setting.get('path', '')
        if not itemPath:
            continue

        itemValue = setting.get('value', '')
        if not itemValue:
            continue

        if re.search('BakeFrameStart', itemPath):
            itemValue = int(
                optionVars.get(
                    'startFrame',
                    cmds.playbackOptions(q=True, min=True)
                )
            )

        if re.search('BakeFrameEnd', itemPath):
            itemValue = int(
                optionVars.get(
                    'endFrame',
                    cmds.playbackOptions(q=True, max=True)
                )
            )
        dataType = setting.get('type')

        if dataType == 'property':
            if type(itemValue) in [str, unicode]:
                if re.search('', itemValue):
                    mel.eval(
                        'FBXProperty "{}" -v "{}";'.format(itemPath, itemValue)
                    )
            else:
                if itemValue is True:
                    itemValue = 'true'
                elif itemValue is False:
                    itemValue = 'false'
                mel.eval(
                    'FBXProperty "{}" -v {};'.format(itemPath, itemValue)
                )
            results.append({
                'type': 'FBXProperty',
                'flag': itemPath,
                'value': itemValue
            })
        elif dataType == 'command':
            itemPath = setting.get('path', '')
            itemFlag = setting.get('flag', '')
            itemValue = setting.get('value', '')
            mel.eval('{} {} {};'.format(
                itemPath,
                itemFlag,
                itemValue
            ))
            results.append({
                'type': 'command',
                'command': itemPath,
                'flag': itemFlag,
                'value': itemValue
            })
    pprint(results)


def fbxExport(
    path='',
    objects=[],
    isSelection=False
):
    path = path.replace(os.sep, '/')
    exportDirectory = os.path.dirname(path)
    if not os.path.isdir(exportDirectory):
        os.makedirs(exportDirectory)

    exportInfo = {
        'force': True,
        'typ': 'FBX export',
        'pr': True,
        'pmt': False
    }

    # Export selectoin is.
    if isSelection:
        exportInfo['es'] = True
        cmds.select(objects, r=True)
    else:
        exportInfo['ea'] = True

    print('*' * 30)
    print 'FBX Export'
    print('*' * 30)

    cmds.file(path, **exportInfo)
    print(path)
    print('')


def removeBackupFile(path=''):
    if not os.path.isdir(path):
        return

    backupFiles = glob.glob('{}*.fbx.backup'.format(path))
    if backupFiles:
        for bk in backupFiles:
            os.remove(bk)
    return


def main(**kwargs):
    # Load plugin.
    if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
        cmds.loadPlugin('fbxmaya.mll')

    path = kwargs.get('path', '')
    configName = kwargs.get('configName', '')
    objects = kwargs.get('objects', [])
    isSelection = kwargs.get('isSelection', True)
    optionVars = kwargs.get('optionVars', {})

    if not path:
        return {}

    if not objects:
        return

    # Change file dialog style. Use maya default.
    mel.eval('optionVar -iv FileDialogStyle 2;')

    if not configName:
        return {}

    if not objects:
        return {}

    settings = getExportConfig(configName=configName)

    userInputs = {
        'settings': settings,
        'optionVars': optionVars
    }
    setFbxSettings(**userInputs)

    fbxExport(
        path=path,
        objects=objects,
        isSelection=isSelection
    )

    removeBackupFile(path=os.path.dirname(path))

    return {}
