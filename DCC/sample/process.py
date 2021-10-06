# -*- coding: utf-8 -*-
import os
import imp
import sys
from pprint import pprint

from maya import cmds

from AnimationPublisher import function as publishFunction

try:
    from importlib import reload
except Exception:
    pass

reload(publishFunction)

try:
    department = '---department---'
    configName = '---configName---'
    publishTemplate = publishFunction.getPublishPorcess(
        department=department,
        configName=configName
    )

    process = publishTemplate.get('process', [])
    userInput = publishTemplate.copy()
    exportPluginPath = '/'.join([
        os.path.dirname(publishFunction.__file__).replace(os.sep, '/'),
        'exportPlugins'
    ])
    if os.path.isdir(exportPluginPath) == False:
        raise

    userInput.update({
        'shot': '---shot---',
        'newStatus': '---newStatus---'
    })

    for p in process:
        pluginName = p.get('pluginName')

        flags = p.get('flags', {})
        isSkipProcess = False
        if flags:
            isSkipProcess = p.get('isSkipProcess', False)
        if isSkipProcess:
            continue

        pluginPath = '/'.join([
            exportPluginPath,
            pluginName
        ])

        if not os.path.isfile(pluginPath):
            continue

        name, ext = os.path.splitext(pluginName)
        userInput['flags'] = flags
        mod = imp.load_source('{}Module'.format(name), pluginPath)

        print('*' * 30)
        print(pluginName)
        print('*' * 30)
        print('')

        result = mod.main(userInput=userInput)
        if result:
            userInput.update(result)
except Exception as e:
    print('')
    print('')
    print('*' * 30)
    print('     Publish Error.')
    print('*' * 30)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(
        exc_tb.tb_frame.f_code.co_filename
    )[1]
    print(exc_type)
    print(fname)
    print(exc_tb.tb_lineno)
    print('')
    print('')
    print(e.message)
    print(e.args)
    print('')
    print('')
    raise

print('')
print('')
print('*' * 30)
print('     Publish Complete.')
print('*' * 30)
print('')
print('')
