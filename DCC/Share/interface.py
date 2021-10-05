# -*- coding: utf-8 -*-
import sys
import os
import re
from maya import OpenMaya, cmds, mel
sys.dont_write_bytecode = True

__filePath = __file__
__baseName = os.path.basename(__filePath)
__dirPath = __filePath.replace(__baseName,'')

__pluginPath = 'smoothSkinWeightCmd.py'
if cmds.pluginInfo(__pluginPath, q=True, l=True) == False:
	try:
		cmds.loadPlugin('%s%s'%(__dirPath, __pluginPath))
		print 'Request plugin...%s'%__pluginPath
	except:
		OpenMaya.MGlobal.displayError('Failed to load plugin. %s'%__pluginPath)
		raise
	finally:
		print 'Load of plug-ins was successful.'


class mainClass(object):
    def __init__(self):
        self.windowName = 'smoothSkinWeightWindow'
        self.windowTitle = 'Smooth Weight'
        self.show()


    def smoothCommand(self, args):
        smooth_param = cmds.floatFieldGrp(
            self.weightParam, q=True, v1=True)
        cmds.smoothSkinWeight(v=smooth_param)


    def show(self):
        if cmds.window(self.windowName,q=True,ex=True):
            cmds.deleteUI(self.windowName)
        cmds.window(self.windowName,t=self.windowTitle)
        cmds.columnLayout(adj=True)
        self.weightParam = cmds.floatFieldGrp(l='Smooth', v1=0.5, pre=3)
        cmds.button(l='Smooth', c=self.smoothCommand)
        cmds.setParent('..')
        cmds.showWindow(self.windowName)


def main():
    mc = mainClass()
