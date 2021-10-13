# -*- coding: utf-8 -*-
import sys

try:
    from importlib import reload
except Exception:
    pass

from maya import cmds

from customLibs import display
reload(display)

sys.dont_write_bytecode = True


def main(**kwargs):
    cameraGroupList = kwargs.get('cameraGroupList', [])
    oldDisplayStatusList = kwargs.get('oldDisplayStatusList', {})

    # Check custom plugin "shotmask".
    shotmask = cmds.ls(type='shotmask2Shape') or []
    if shotmask:
        __parent = cmds.listRelatives(shotmask, p=True) or []
        if __parent:
            cmds.delete(__parent)

    # Check custom plugin "spReticleLocator".
    spReticleLoc = cmds.ls(type='spReticleLoc') or []
    if spReticleLoc:
        for n in spReticleLoc:
            __parent = cmds.listRelatives(spReticleLoc, p=True, f=True) or []
            if not __parent:
                continue
            if isinstance(__parent, list):
                __parent = __parent[0]
            try:
                cmds.lockNode(spReticleLoc, lock=False)
                cmds.lockNode(__parent, lock=False)
                cmds.setAttr('{}.v'.format(__parent), False)
            except Exception as e:
                print(e.message)
                print(e.args)

    if cameraGroupList:
        for cam in cameraGroupList:
            cmds.setAttr('{}.visibility'.format(cam), True)

    # Restore display status.
    if oldDisplayStatusList:
        display.editModelEditorViewStatus(
            editDisplayStatusList=oldDisplayStatusList
        )

    # Restore viewport renderer.
    modelPanel = display.getModelPanel()
    oldModelPanelRenderName = kwargs.get(
        'oldModelPanelRenderName',
        'base_OpenGL_Renderer'
    )
    cmds.modelEditor(
        modelPanel,
        e=True,
        rendererName=oldModelPanelRenderName
    )

    return kwargs
