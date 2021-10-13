# -*- coding: utf-8 -*-
import sys
import re
import os
import glob
import shutil
# import platform
# from pprint import pprint

try:
    from importlib import reload
except Exception:
    pass

from maya import cmds

from customLibs import playblast as playblastUtil
from customLibs import display as displayUtil
import layoutCameraUtil
reload(playblastUtil)
reload(displayUtil)
reload(layoutCameraUtil)

sys.dont_write_bytecode = True


def getModelPanel():
    result = displayUtil.getModelPanel()
    return result


def setCamera(cameraName=''):
    panel = getModelPanel()
    if not panel:
        return
    if not cmds.objExists(cameraName):
        return
    cmds.modelPanel(
        panel,
        e=True,
        camera=cameraName
    )


def getStartEnd(cameraGroup=''):
    if not cmds.objExists(cameraGroup):
        return []
    if cmds.attributeQuery('startFrame', n=cameraGroup, ex=True):
        startTime = cmds.getAttr('{}.startFrame'.format(cameraGroup))
    if cmds.attributeQuery('endFrame', n=cameraGroup, ex=True):
        endTime = cmds.getAttr('{}.endFrame'.format(cameraGroup))
    return [startTime, endTime]


def getOutpath(cameraName='', outputPath=''):
    if not cameraName:
        return {}
    sequenceName = ''
    if re.search(':', cameraName):
        sequenceName = cameraName.split(':')[0]

    if not re.search('^e', sequenceName):
        sequenceName = ''

    if not sequenceName:
        sceneName = cmds.file(q=True, sn=True)
        sceneName = sceneName.replace(os.sep, '/')
        basename = os.path.basename(sceneName)
        filename, fileext = os.path.splitext(basename)
        print(filename)
        if re.search('_AN_', filename):
            filenames = filename.split('_AN_')
            sequenceName = filenames[0]

    if not sequenceName:
        sequenceName = 'e00s00c000'

    tmp = re.search('s[0-9]+', sequenceName)
    episode = None
    if tmp:
        episode = sequenceName.split(tmp.group())[0]
    tmp = re.search('c[0-9]+', sequenceName)
    sequence = None
    if tmp:
        sequence = sequenceName.split(tmp.group())[0]
        sequence = sequence.replace(episode, '')
    shot = sequenceName.replace(episode, '')
    shot = shot.replace(sequence, '')
    outpath = '/'.join([
        outputPath,
        episode,
        sequence,
        shot
    ])

    return {
        'outpath': outpath,
        'sequenceName': sequenceName,
        'episode': episode,
        'sequence': sequence,
        'shot': shot
    }


def versionup(path='', name='', outFormat='', suffix=''):
    version = 0
    if not os.path.isdir(path):
        return

    fileext = ''
    if outFormat != 'image':
        fileext = '.mov'
    searchPath = '/'.join([path, name + '*' + fileext])
    files = glob.glob(searchPath)

    if not files:
        return
    if files:
        if outFormat == 'image':
            files = [f for f in files if os.path.isdir(f)]
        else:
            files = [f for f in files if os.path.isfile(f)]
    if not files:
        return

    files.sort()

    latest = files[-1]
    latestName = os.path.basename(latest)
    sequenceName, temp = latestName.split(suffix)
    currentVersion = None
    fileext = ''
    if outFormat != 'image':
        currentVersion, fileext = os.path.splitext(temp)
    else:
        currentVersion = temp
    version = int(currentVersion) + 1
    src = '/'.join([
        path,
        ''.join([
            sequenceName,
            '{}00{}'.format(suffix, fileext)
        ])

    ])
    dst = '/'.join([
        path,
        ''.join([
            sequenceName,
            '{}{}{}'.format(
                suffix,
                str(version).zfill(2),
                fileext
            )
        ])
    ])
    if not os.path.isfile(src):
        return

    log = ''
    if outFormat != 'image':
        shutil.copyfile(src, dst)
    else:
        shutil.copytree(src, dst)
        shutil.rmtree(src)
        log += '\n'
        log += '> Remove tree\n'
        log += '{}\n'.format(src)
    tmp = '\n'
    tmp += '> Copy complete\n'
    tmp += '{}\n'.format(src)
    tmp += '|\n'
    tmp += '{}\n'.format(dst)
    print(tmp + log)


def main(**kwargs):
    cameraList = kwargs.get('cameraList', [])
    outFormat = kwargs.get('outFormat', 'mov')
    reso = kwargs.get('reso', {'height': 720, 'width': 1280})
    isView = kwargs.get('isView', False)
    outputPath = kwargs.get('outputPath', '')
    isOutput = kwargs.get('isOutput', False)

    flags = kwargs.get('flags', {})
    suffix = flags.get('fileSuffix', '_None_')

    compression = 'H.264'
    if outFormat == 'png':
        compression = 'png'
        outFormat = 'image'

    dmLight = cmds.ls('dmLight', l=True) or []

    shotmask = cmds.ls(type='shotmaskShape', l=True) or []
    if shotmask and isinstance(shotmask, list):
        shotmask = shotmask[0]

    if not isinstance(cameraList, list):
        cameraList = [cameraList]

    for cameraName in cameraList:
        sequenceName = None
        outpath = None
        if isOutput:
            outInfo = getOutpath(
                cameraName=cameraName,
                outputPath=outputPath
            )
            outpath = outInfo.get('outpath')
            sequenceName = outInfo.get('sequenceName')
            episode = outInfo.get('episode')
            sequence = outInfo.get('sequence')
            shot = outInfo.get('shot')

            if not os.path.isdir(outpath):
                print('')
                print('> Make directory')
                print(outpath)
                os.makedirs(outpath)
            name = ''.join([
                episode,
                sequence,
                shot,
                suffix
            ])

            versionup(
                path=outpath,
                name=name,
                outFormat=outFormat,
                suffix=suffix
            )

            name += '00'
        if outFormat == 'image':
            outpath = '/'.join([outpath, name])
            if not os.path.isdir(outpath):
                os.makedirs(outpath)
            name = 'image'

        startTime = cmds.playbackOptions(q=True, min=True)
        endTime = cmds.playbackOptions(q=True, max=True)
        camGroup = None
        if sequenceName:
            camGroup = '{}:cam_group'.format(sequenceName)
        if cmds.objExists(camGroup):
            if cmds.objExists(camGroup):
                startTime, endTime = getStartEnd(cameraGroup=camGroup)
            cmds.setAttr('{}.visibility'.format(camGroup), False)

        settings = {
            'compression': compression,
            'outFormat': outFormat,
            'startTime': int(startTime),
            'endTime': int(endTime),
            'forceOverwrite': True,
            'showOrnaments': False,
            'framePadding': 1,
            'percent': 100,
            'width': reso.get('width', 1280),
            'height': reso.get('height', 720),
            'quality': 100,
            'offScreen': True,
            'viewer': isView
        }

        audioFile = cmds.ls(
            ['audio_{}'.format(sequenceName)],
            type='audio'
        ) or []
        if not audioFile:
            audioFile = cmds.ls(type='audio') or []

        if audioFile:
            settings['sound'] = audioFile[0]

        playblastTemplate = {
            'settings': settings
        }
        if isOutput:
            playblastTemplate.update({
                'path': outpath,
                'name': name,
            })

        setCamera(cameraName=cameraName)
        cmds.setAttr('{}.displayFilmGate'.format(cameraName), False)
        cmds.setAttr('{}.displayResolution'.format(cameraName), False)
        cmds.setAttr('{}.overscan'.format(cameraName), 1.)

        if cmds.objExists(camGroup):
            cmds.setAttr('{}.offsetCtrl'.format(camGroup), False)
            cmds.setAttr('{}.overScanFrame'.format(camGroup), False)

        # cameraGroup = '{}:cam_group'.format(cameraName.split(':')[0])
        # if cmds.objExists(cameraGroup):
        #     v = cmds.getAttr('{}.overScanScale'.format(cameraGroup))
        #     cmds.setAttr(
        #         '{}.overscanSize'.format(shotmask),
        #         str(v),
        #         type='string'
        #     )
        #     v = cmds.getAttr('{}.useShake'.format(cameraGroup))
        #     nodeName = '{}:cameraPosition'.format(cameraName.split(':')[0])
        #     cameraShakeType = ['none', '2D', '3D'][int(v)]
        #     if cmds.objExists(nodeName):
        #         cmds.setAttr('{}.visibility'.format(shotmask), False)
        #         kwargs['positionNode'] = nodeName
        #         kwargs['start'] = startTime
        #         kwargs['end'] = endTime
        #         __temp = layoutCameraUtil.get2d3d(**kwargs)
        #         if __temp[0] and __temp[1]:
        #             cameraShakeType = '2D/3D'
        #         cmds.setAttr('{}.visibility'.format(shotmask), True)
        #     cmds.setAttr(
        #         '{}.cameraShakeType'.format(shotmask),
        #         cameraShakeType,
        #         type='string'
        #     )

        # setCamera(cameraName=cameraName)

        if not re.search('^e', cameraName):
            node = cmds.ls(type='shotmask2Shape') or []
            if cmds.attributeQuery(
                    'userCameraName',
                    n=node[0],
                    ex=True
            ):
                cmds.setAttr(
                    '{}.userCameraName'.format(node[0]),
                    sequenceName,
                    type="string"
                )

        cmds.playbackOptions(e=True, min=startTime, max=endTime)
        cmds.refresh()

        if isOutput is False:
            playblastTemplate.update({'isOutput': isOutput})
        try:
            if dmLight:
                cmds.select(dmLight, r=True)
            playblastUtil.create(**playblastTemplate)
        except Exception as e:
            print('')
            print('> Playblast error.')
            print(e)

        if cmds.objExists(camGroup):
            cmds.setAttr('{}.offsetCtrl'.format(camGroup), 0)
            cmds.setAttr('{}.overScanFrame'.format(camGroup), 0)
            cmds.setAttr('{}.visibility'.format(camGroup), False)

        if outpath:
            print('> output')
            print(outpath)
            print('')

    return kwargs
