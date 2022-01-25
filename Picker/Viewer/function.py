# -*- coding: utf-8 -*-
import sys
import os
import glob
import re
import platform
import webbrowser

from pprint import pprint

try:
    from importlib import reload
except Exception:
    pass

# Maya
from maya import cmds

# Picker
import enviromentUtil
from AnimationPublisher.exportPlugins import exportAnimation
# Cast2
from cast2.core import attribute as cast2Attr
from cast2.tools.animation.bakeSimulationRig import widget as bsrw
from cast2.tools.animation.convertIkFkAnimation import widget as cia
from cast2.tools.animation.convertIkRotation import interface as cir
from cast2.tools.animation.convertPoleVector import interface as cpv
from cast2.tools.animation.convertParentSpace import interface as cps
from cast2.core import animation as cast2AnimUtil
# Picker
reload(enviromentUtil)
reload(exportAnimation)
# Cast2
reload(cast2Attr)
reload(bsrw)
reload(cia)
reload(cir)
reload(cpv)
reload(cps)
reload(cast2AnimUtil)

sys.dont_write_bytecode = True

platformSystem = platform.system()


def openHelp():
    apps = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    if platformSystem in ['Darwin', 'Linux']:
        apps = 'open -a /Applications/Google\ Chrome.app %s'

    url = 'https://docs.google.com/document/d/1i03_oaB5uZydAKfHCcNLi9OkL1tqijOJaoV37yjDCM0/edit?usp=sharing'
    webbrowser.get(apps).open(url)


def createPath(project='BORN', isLocal=False):
    envs = enviromentUtil.getProjectEnvironments()
    PROJECT_NAME = envs.get('PROJECT_NAME', '')
    if not PROJECT_NAME:
        PROJECT_NAME = project
    drive = 'M:'
    if platformSystem in ['Darwin', 'Linux']:
        if os.path.isdir('/M'):
            drive = drive.replace('M:', '/M')
        elif os.path.isdir('/Volumes/M'):
            drive = drive.replace('M:', '/Volumes/M')
    if isLocal:
        drive = 'D:'
        if platformSystem in ['Darwin', 'Linux']:
            drive = '/Volumes/Macintosh HD'
    result = '/'.join([
        drive,
        'project',
        PROJECT_NAME,
        'data',
        'RIG',
        'common',
        'picker'
    ])

    return result


def getPickerData(
    project='BORN',
    name='',
    forceTemplate='',
    isLocal=False
):
    projectPath = createPath(project='BORN', isLocal=isLocal)

    sceneAssets = exportAnimation.getReferenceAssetFromScene()
    assetType = 'CH'
    referencePath = ''
    for sa in sceneAssets:
        referenceNamespace = sa.get('referenceNamespace', '')
        if name not in [referenceNamespace]:
            continue
        assetType = sa.get('assetType', '')
        referencePath = sa.get('referencePath', '')
    basename = os.path.basename(referencePath)
    assetBaseName, ext = os.path.splitext(basename)

    if forceTemplate:
        assetBaseName = forceTemplate

    namedPath = '/'.join([
        projectPath,
        assetBaseName
    ])

    path = ''
    commonName = '{}Common'.format(assetType.lower())
    if not os.path.isdir(namedPath):
        path = '/'.join([
            projectPath,
            commonName
        ])
        namedPath = ''
    else:
        path = namedPath

    # Search from file.
    files = glob.glob('{}/*'.format(projectPath))
    if files:
        files = [os.path.basename(f) for f in files]
        files.sort()
        temp = ''
        matchList = {}
        matchValues = []
        for f in files:
            if not re.search(f, name):
                continue
            temp = f
            v = float(len(temp)) / float(len(assetBaseName))
            matchValues.append(v)
            matchList[f] = v
        if matchValues:
            matchValues.sort()
            v = matchValues[-1]
        for k in matchList.keys():
            matchValue = matchList.get(k)
            if matchValue is not v:
                continue
            temp = k
            break
        if temp and not namedPath:
            path = '/'.join([
                projectPath,
                temp
            ])

    return path


def selectAllController(namespace=''):
    setName = 'controllerSets'
    if namespace:
        setName = ':'.join([
            namespace,
            setName
        ])

    if not cmds.objExists(setName):
        return [False, setName]

    cmds.select(
        setName,
        r=True
    )

    return [True, None]


def resetControllerPosition():
    cmds.undoInfo(ock=True)
    cast2Attr.reset()
    cmds.undoInfo(cck=True)


def selectSymmetricController(isAdd=False):
    result = cast2AnimUtil.getSymmetricCtrl()
    if not result:
        return
    kwargs = {'r': True}
    if isAdd:
        kwargs = {'add': True}
    cmds.undoInfo(openChunk=True)
    symCtrlList = []
    for symCtrl in result:
        if not cmds.objExists(symCtrl):
            continue
        symCtrlList.append(symCtrl)
    try:
        cmds.select(symCtrlList, **kwargs)
    except Exception:
        pass
    cmds.undoInfo(closeChunk=True)


def mirrorPoseCopy():
    nodes = cmds.ls(sl=True) or []
    result = cast2AnimUtil.getSymmetricCtrl()
    if not nodes:
        return
    cmds.undoInfo(openChunk=True)
    try:
        for i, name in enumerate(nodes):
            keyAttrs = cmds.listAttr(name, k=True)
            mName = result[i]
            for ka in keyAttrs:
                src = '.'.join([name, ka])
                dst = '.'.join([mName, ka])
                attrExists = cmds.attributeQuery(
                    ka, n=mName, ex=True
                )
                if not attrExists:
                    continue
                value = cmds.getAttr(src)
                cmds.setAttr(dst, value)
    except Exception:
        pass
    cmds.undoInfo(closeChunk=True)


# Bake simulation rig
def bakeSimulationRig():
    bsrw.Main()


# Convert IKFK animation
def convertIKFKAnimation():
    cia.Main()


# Convert ik rotation.
def convertIkRotation():
    cir.main()


# Convert ik poleVector.
def convertPoleVector():
    cpv.main()


# Convert parent space
def convertParentSpace():
    cps.main()
