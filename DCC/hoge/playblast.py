# -*- coding: utf-8 -*-
import sys
import os
import tempfile
# import re
from pprint import pprint
import platform

from maya import cmds

sys.dont_write_bytecode = True


# Template sample.
# playblastTemplate = {
#     'path': 'C:/Users/masahiro-ohmomo/Documents/maya/projects/default/images/sample/sample2',
#     'name': 'hogehoge',
#     'settings': {
#         'compression': 'png',
#         'outFormat': 'image',
#         'startTime': 0,
#         'endTime': 24,
#         'forceOverwrite': True,
#         'showOrnaments': False,
#         'framePadding': 1,
#         'percent': 100,
#         'width': 1920,
#         'height': 1080,
#         'quality': 100,
#         'offScreen': True
#     }
# }
def create(*args, **kwargs):
    path = kwargs.get('path', '')
    name = kwargs.get('name', '')
    isOutput = kwargs.get('isOutput', True)
    settings = kwargs.get('settings', {})

    if isOutput:
        if not path and not name:
            print('')
            print('> Argument Error')
            print('path or name was not found.')
            print('> path')
            print(path)
            print('> name')
            print(name)
            return

        if not os.path.isdir(path):
            os.makedirs(path)

    defaultTempdir = os.environ.get('TMP')
    tempdir = tempfile.mkdtemp()
    tempdir = tempdir.replace(os.sep, '/')
    os.environ['TMP'] = tempdir

    compression = settings.get('compression', 'png')

    outFormat = settings.get('outFormat', 'qt')
    fileExtension = '.mov'
    if outFormat == 'avi':
        fileExtension = '.avi'
        compression = 'none'
    elif outFormat == 'image':
        fileExtension = ''

    settings['compression'] = compression
    settings['format'] = outFormat
    settings.pop('outFormat')

    if platform.system() == 'Darwin' and outFormat == '.mov':
        settings['format'] = 'avfoundation'

    # Edit filename.
    if isOutput:
        if settings.get('completeFilename'):
            filename = '/'.join([
                path,
                ''.join([
                    settings.get('completeFilename', 'untitled'),
                    fileExtension
                ])
            ])
            settings['completeFilename'] = filename
        else:
            filename = '/'.join([
                path,
                ''.join([name, fileExtension])
            ])
            settings['filename'] = filename

    startTime = settings.get(
        'startTime',
        int(cmds.playbackOptions(q=True, ast=True))
    )
    settings['startTime'] = startTime

    endTime = settings.get(
        'endTime',
        int(cmds.playbackOptions(q=True, aet=True))
    )
    settings['endTime'] = endTime

    forceOverwrite = settings.get('forceOverwrite', True)
    settings['forceOverwrite'] = forceOverwrite
    viewer = settings.get('viewer', False)
    settings['viewer'] = viewer
    showOrnaments = settings.get('showOrnaments', False)
    settings['showOrnaments'] = showOrnaments
    framePadding = settings.get('framePadding', 4)
    settings['framePadding'] = framePadding
    percent = settings.get('percent', 100)
    settings['percent'] = percent

    width = settings.get('width', 1920)
    settings.pop('width')
    height = settings.get('height', 720)
    settings.pop('height')
    widthHeight = [width, height]
    settings['widthHeight'] = widthHeight
    quality = settings.get('quality', 100)
    settings['quality'] = quality
    offScreen = settings.get('offScreen', True)
    settings['offScreen'] = offScreen
    clearCache = settings.get('clearCache', True)
    settings['clearCache'] = clearCache

    print('*' * 30)
    print('Playblast')
    print('*' * 30)
    pprint(settings)
    print('')
    cmds.playblast(**settings)

    os.environ['TMP'] = defaultTempdir

    return {}
