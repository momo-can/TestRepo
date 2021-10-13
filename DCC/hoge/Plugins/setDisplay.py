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
    # Get current display status.
    oldDisplayStatusList = display.editModelEditorViewStatus(query=True)

    # Edit display status.
    editDisplayStatusList = {
        'polymeshes': True,
        'nurbsCurves': True,
        'nurbsSurfaces': True,
        'locators': False,
        'pluginShapes': True,
        'dynamics': True,
        'particleInstancers': True,
        'nParticles': True,
        'displayAppearance': 'smoothShaded',
        'displayTextures': True,
        # 'displayLights': 'default',
        'displayLights': 'all'
    }

    # if cmds.objExists('dmLight'):
    #     dmLight = cmds.ls('dmLight', l=True) or []
    #     __childs = cmds.listRelatives(dmLight, ad=True, f=True) or []
    #     if __childs:
    #         print('> Dummy light, found.')
    #         editDisplayStatusList['displayLights'] = 'selected'
    #         cmds.select(dmLight, r=True)
    #         cmds.refresh()

    display.editModelEditorViewStatus(
        editDisplayStatusList=editDisplayStatusList
    )

    kwargs['newDisplayStatusList'] = editDisplayStatusList
    kwargs['oldDisplayStatusList'] = oldDisplayStatusList

    # Set viewport renderer.
    modelPanel = display.getModelPanel()
    oldModelPanelRenderName = cmds.modelEditor(
        modelPanel,
        q=True,
        rendererName=True
    )
    kwargs['oldModelPanelRenderName'] = oldModelPanelRenderName
    cmds.modelEditor(modelPanel, e=True, rendererName='vp2Renderer')

    return kwargs
