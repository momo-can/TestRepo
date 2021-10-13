# -*- coding: utf-8 -*-
import sys
from pprint import pprint

from maya import OpenMaya
from maya import cmds
from maya import mel


def error(message='', isRaise=False):
    OpenMaya.MGlobal.displayError(message)
    if isRaise:
        raise


def setCameraToActivePanel(camera=''):
    if not cmds.objExists(camera):
        return False
    panels = cmds.getPanel(visiblePanels=True) or []
    if not panels:
        return False
    try:
        cmd = ' '.join([
            'setNamedPanelLayout "Single Perspective View";',
            'lookThroughModelPanel',
            camera,
            panels[0],
            ';'
        ])
        mel.eval(cmd)
        return True
    except Exception as e:
        print e
        return False


def getModelPanel():
    mel.eval('setNamedPanelLayout "Single Perspective View";')
    focusPanel = cmds.getPanel(wf=True) or []
    if not focusPanel:
        focusPanel = 'modelPanel4'
    modelPanels = cmds.getPanel(type='modelPanel') or []
    if focusPanel not in modelPanels:
        focusPanel = 'modelPanel4'
    return focusPanel


'''
# Get current display status.
oldDisplayStatusList = editModelEditorViewStatus(query=True)

# Edit display status.
editDisplayStatusList = {
    'polymeshes': True
}
editModelEditorViewStatus(
    query=False,
    editDisplayStatusList=editDisplayStatusList
)

# Restore display status.
editModelEditorViewStatus(
    query=False,
    editDisplayStatusList=oldDisplayStatusList
)
'''
def editModelEditorViewStatus(*args, **kwargs):
    query = False
    if 'query' in kwargs.keys():
        query = True
    editDisplayStatusList = kwargs.get('editDisplayStatusList', {})

    flags = [
        'controllers',
        'nurbsCurves',
        'nurbsSurfaces',
        'controlVertices',
        'hulls',
        'polymeshes',
        'subdivSurfaces',
        'planes',
        'lights',
        'cameras',
        'imagePlane',
        'joints',
        'ikHandles',
        'deformers',
        'dynamics',
        'particleInstancers',
        'fluids',
        'hairSystems',
        'follicles',
        'nCloths',
        'nParticles',
        'nRigids',
        'dynamicConstraints',
        'locators',
        'dimensions',
        'pivots',
        'handles',
        'textures',
        'strokes',
        'motionTrails',
        'pluginShapes',
        'clipGhosts',
        'greasePencils',
        'manipulators',
        'grid',
        'hud',
        'hos',
        'selectionHiliteDisplay',
        'displayAppearance',
        'displayTextures',
        'displayLights'
    ]

    displayStatusList = {}
    panel = getModelPanel()
    editFrag = {}
    for flag in flags:
        __flag = {'query': True, flag: True}
        if not query:
            value = editDisplayStatusList.get(flag, False)
            editFrag[flag] = value
        else:
            value = cmds.modelEditor(
                panel,
                **__flag
            )
            displayStatusList[flag] = value
    if not query:
        editFrag['edit'] = True
        values = cmds.modelEditor(
            panel,
            **editFrag
        )

    return displayStatusList


def restoreModelEditorViewStatus(*args, **kwargs):
    restoreDisplayStatusList = kwargs.get('restoreDisplayStatusList', {})
    flags = [
        'controllers',
        'nurbsCurves',
        'nurbsSurfaces',
        'controlVertices',
        'hulls',
        'polymeshes',
        'subdivSurfaces',
        'planes',
        'lights',
        'cameras',
        'imagePlane',
        'joints',
        'ikHandles',
        'deformers',
        'dynamics',
        'particleInstancers',
        'fluids',
        'hairSystems',
        'follicles',
        'nCloths',
        'nParticles',
        'nRigids',
        'dynamicConstraints',
        'locators',
        'dimensions',
        'pivots',
        'handles',
        'textures',
        'strokes',
        'motionTrails',
        'pluginShapes',
        'clipGhosts',
        'greasePencils',
        'manipulators',
        'grid',
        'hud',
        'hos',
        'selectionHiliteDisplay',
        'displayAppearance',
        'displayTextures',
        'displayLights'
    ]

    displayStatusList = {}
    panels = cmds.getPanel(typ='modelPanel')
    for flag in flags:
        value = restoreDisplayStatusList.get(flag, False)
        __flag = {'edit': True, flag: value}
        try:
            for pane in panels:
                cmds.modelEditor(
                    [pane],
                    **__flag
                )
        except Exception:
            continue

    return displayStatusList
