# -*- coding: utf-8 -*-
import os
import re
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

try:
    from maya import cmds
except Exception:
    pass

from Picker.CoreDebug import thumbnail
from Picker.CoreDebug import viewerWidget3 as viewerWidget
from Picker.CoreDebug import sceneWidget3 as sceneWidget
from Picker.CoreDebug import graphicsItemWidget
from Picker.CoreDebug import pixmapWidget2 as pixmapWidget
reload(thumbnail)
reload(viewerWidget)
reload(sceneWidget)
reload(graphicsItemWidget)
reload(pixmapWidget)

sys.dont_write_bytecode = True


class Widget(QWidget):
    def __init__(
        self,
        namespaceWidget=None,
        isEditable=True,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.itemInfo = {}

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(5, 0, 5, 0)

        self.sceneWidget = sceneWidget.Scene(
            isEditable=isEditable,
            namespaceWidget=namespaceWidget
        )

        self.gv = viewerWidget.View(
            sceneWidget=self.sceneWidget,
            isEditable=isEditable
        )
        self.mainLayout.addWidget(self.gv)

        self.setLayout(self.mainLayout)

    def getSelectedItems(self):
        return self.gv.getSelectedItems()

    def deleteItem(self, item):
        self.gv.deleteItem(item)

    def getObjectColor(self, objectName=''):
        color = None
        if not cmds.objExists(objectName):
            return color
        shapes = cmds.listRelatives(objectName, s=True) or []
        if shapes:
            if isinstance(shapes, list):
                shapes = shapes[0]
            if cmds.attributeQuery('overrideColorRGB', n=shapes, ex=True):
                color = cmds.getAttr('{}.overrideColorRGB'.format(shapes))
        return color

    def autoCreateShape(
        self,
        style='Box',
        scale=10.,
        color=QBrush(Qt.lightGray),
        text='Sample',
        font=None,
        pos_x=.0,
        pos_y=.0
    ):
        objects = cmds.ls(sl=True) or []
        if not objects:
            return
        positions = []
        bounsX = []
        bounsY = []
        object_names = []
        referenceNamespace = ''
        for obj in objects:
            pos = cmds.xform(obj, q=True, ws=True, rp=True)
            positions.append(pos)
            bounsX.append(pos[0])
            bounsY.append(pos[1])

            if re.search(':', obj):
                referenceNamespace = obj.split(':')[0]
                obj = re.sub(
                    '^{0}:'.format(referenceNamespace),
                    '',
                    obj
                )
            object_names.append(obj)
        bounsX.sort()
        bounsY.sort()

        for i, x in enumerate(positions):
            pos_x = positions[i][0]
            pos_y = -positions[i][1]
            object_name = object_names[i]
            __name = object_name
            if referenceNamespace:
                __name = ':'.join([referenceNamespace, __name])
            color = self.getObjectColor(objectName=__name)
            if not color:
                color = QBrush(Qt.lightGray)
            else:
                if isinstance(color, list):
                    color = list(color[0])
                color = [round(c * 255) for c in color]
                __color = QColor()
                __color.setRgb(*color)
                color = QBrush(__color)
            item = self.createShape(
                pos_x=pos_x,
                pos_y=pos_y,
                color=color,
                style=style,
                scale=scale,
                text=object_name,
                font=font
            )
            item.pickItemData = object_name

    def createShape(
        self,
        style='Box',
        scale=10.,
        text='Sample',
        font=None,
        color=QBrush(Qt.lightGray),
        pos_x=.0,
        pos_y=.0
    ):
        items = self.getSceneItem()
        number = len(items)
        itemName = 'item_{}'.format(str(int(number)))
        scene = self.gv.sceneWidget
        item = None
        # centerX = 250.0
        # centerY = 250.0
        item = graphicsItemWidget.GraphicsItem(
            style=style,
            scale=scale,
            text=text,
            font=font
        )
        item.setZValue(1)

        item.setBrush(color)
        item.setPos(pos_x, pos_y)
        item.setSelected(False)
        scene.addItem(item)
        item.itemName = itemName
        return item

    def screenCapture(self, workpath=''):
        __path = thumbnail.screenCapture(workpath=workpath)
        if not __path:
            return
        self.setImage(path=__path)

    def setImage(self, path=''):
        if not path:
            return
        if not os.path.isfile(path):
            return
        item = pixmapWidget.SimpleImgItem()
        item.setImage(path=path)

        scene = self.gv.sceneWidget
        scene.addItem(item)
        items = self.getSceneItem()
        number = len(items)
        itemName = 'image_{}'.format(str(int(number)))
        item.itemName = itemName
        return item

    def editColor(self):
        self.gv.editColor()

    def getItemStatus(self):
        items = self.getSceneItem()
        if not items:
            return []
        status_list = []
        for i, item in enumerate(items):
            status = item.getStatus()
            status_list.append(status)
        return status_list

    def getView(self):
        return self.gv

    def getSceneItem(self):
        return self.gv.items()

    def updateScene(self):
        self.gv.updateScene()
