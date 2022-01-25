# -*- coding: utf-8 -*-
import sys
import re

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class View(QGraphicsView):
    def __init__(
        self,
        sceneWidget=None,
        isEditable=True,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.mouseButtonType = 0
        self.isEditable = isEditable
        self.zoomValue = 1.1

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        # self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.sceneWidget = sceneWidget
        self.setScene(self.sceneWidget)
        self.setSceneRect(-500, -500, 3000, 3000)
        if self.isEditable is False:
            self.setSceneRect(-100, -200, 100, 200)

        self.selectedItems = []

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def keyPressEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if self.isEditable:
            if event.key() == Qt.Key_Delete:
                self.deleteSceneItem()
                return
        if event.key() == Qt.Key_A:
            if modifiers == Qt.ControlModifier:
                self.sceneWidget.selectAllItems()
            else:
                # if self.isEditable is False:
                #     self.setSceneRectFromItems()
                self.viewFit()
            return
        if event.key() == Qt.Key_Up and self.isEditable:
            self.updateItemFuncA()
        super(self.__class__, self).keyPressEvent(event)

    def viewFit(self):
        __rect = self.sceneWidget.itemsBoundingRect()
        self.fitInView(__rect, Qt.KeepAspectRatio)
        self.updateScene()

    def setSceneRectFromItems(self):
        __rect = self.sceneWidget.itemsBoundingRect()
        __rect.setX(__rect.x() - 200)
        __rect.setY(__rect.y() - 200)
        __rect.setWidth(__rect.width() + 200)
        __rect.setHeight(__rect.height() + 200)
        self.setSceneRect(__rect)

    def contextMenu(self, pos):
        if self.isEditable is False:
            return
        # Get item from cursor's position.
        onItem = self.itemAt(pos)
        if onItem:
            self.selectedItems.append(onItem)
        menu = QMenu(self)

        deleteAction = None
        lockAction = None
        lockAllAction = None
        unLockAction = None
        unLockAllAction = None
        forceShowEnable = None
        forceShowDisable = None
        selectCtrlFromCurrentTab = None
        if self.isEditable:
            deleteAction = menu.addAction('Delete Item')
            lockAction = menu.addAction('Lock')
            lockAllAction = menu.addAction('Lock All')
            unLockAction = menu.addAction('UnLock')
            unLockAllAction = menu.addAction('UnLock All')
            forceShowEnable = menu.addAction('Forced show of items')
            forceShowDisable = menu.addAction('Forced hide of items')
            selectCtrlFromCurrentTab = menu.addAction(
                'Select all controllers in the tab.'
            )
            showText = menu.addAction('Show Text')
            hideText = menu.addAction('Hide Text')

        currentAct = menu.exec_(self.mapToGlobal(pos))
        if deleteAction == currentAct:
            self.deleteSceneItem()
        elif lockAction == currentAct:
            for item in self.selectedItems:
                item.setFlags(QGraphicsItem.GraphicsItemFlags())
                if item.getType() == 'SimpleShapeItem':
                    if item.style not in ['Groups']:
                        item.setFlags(
                            QGraphicsItem.ItemIsSelectable
                        )
                item._locked = True
        elif lockAllAction == currentAct:
            for item in self.sceneWidget.items():
                item.setFlags(QGraphicsItem.GraphicsItemFlags())
                if item.getType() == 'SimpleShapeItem':
                    if item.style not in ['Groups']:
                        item.setFlags(
                            QGraphicsItem.ItemIsSelectable
                        )
                item._locked = True
        elif unLockAction == currentAct:
            for item in self.selectedItems:
                item.setFlags(
                    QGraphicsItem.ItemIsMovable |
                    QGraphicsItem.ItemIsSelectable
                )
                item._locked = False
        elif unLockAllAction == currentAct:
            for item in self.sceneWidget.items():
                item.setFlags(QGraphicsItem.GraphicsItemFlags())
                item.setFlags(
                    QGraphicsItem.ItemIsMovable |
                    QGraphicsItem.ItemIsSelectable
                )
                item._locked = False
        elif showText is currentAct:
            for item in self.selectedItems:
                item.view_text = True
        elif hideText is currentAct:
            for item in self.selectedItems:
                item.view_text = False
        elif forceShowEnable == currentAct:
            items = self.sceneWidget.items()
            for item in items:
                if not getattr(item, 'pickItemShowHide', None):
                    continue
                item._forceShow = True
                item.setVisible(True)
        elif forceShowDisable == currentAct:
            items = self.sceneWidget.items()
            for item in items:
                if not getattr(item, 'pickItemShowHide', None):
                    continue
                item._forceShow = False
        elif selectCtrlFromCurrentTab == currentAct:
            self.sceneWidget.selectAllItems()
        self.updateScene()

    def updateItemFuncA(self):
        if self.isEditable is False:
            return

        if not self.sceneWidget.items():
            return
        groupsCount = 1
        baseCount = 1
        for item in self.items():
            newName = None
            pickItemType = getattr(item, 'pickItemType', None)
            if pickItemType:
                pickItemType = item.pickItemType
            if pickItemType not in ['Select']:
                continue

            pickItemData = getattr(item, 'pickItemData', None)
            if pickItemData:
                pickItemData = item.pickItemData
                newName = pickItemData
                if re.search('\n', pickItemData):
                    newName = 'item_{}'.format(baseCount)
                    baseCount += 1

            style = getattr(item, 'style', None)
            if style:
                style = item.style
            if style in ['Groups']:
                newName = 'item_Groups_{}'.format(groupsCount)
                groupsCount += 1
            if newName is None:
                shapeType = item.shapeType
                newName = 'item_{}_{}'.format(shapeType, baseCount)
                baseCount += 1
            item.itemName = newName

    def deleteSceneItem(self):
        if not self.selectedItems:
            return
        for item in self.selectedItems:
            self.deleteItem(item)

    def deleteItem(self, item):
        self.sceneWidget.removeItem(item)
        self.updateScene()

    def mousePressEvent(self, event):
        self.selectedItems = self.sceneWidget.selectedItems()
        if event.button() == Qt.LeftButton:
            self.mouseButtonType = 0
        if event.button() == Qt.MidButton:
            self.mouseButtonType = 1
            self.setCursor(Qt.ClosedHandCursor)
            self.dragPos = event.pos()
            self.setDragMode(QGraphicsView.NoDrag)
        if event.button() == Qt.RightButton:
            self.mouseButtonType = 2
        self.updateScene()
        super(self.__class__, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mouseButtonType == 1:
            diff = event.pos() - self.dragPos
            self.dragPos = event.pos()
            valueH = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(
                valueH - diff.x()
            )
            valueV = self.verticalScrollBar().value()
            self.verticalScrollBar().setValue(
                valueV - diff.y()
            )
        self.updateScene()
        super(self.__class__, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        if event.button() != Qt.RightButton:
            self.selectedItems = self.sceneWidget.selectedItems()
        self.updateScene()
        super(self.__class__, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # Zoom Factor
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Set Anchors
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.delta() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())
        super(self.__class__, self).wheelEvent(event)

    def changeBrushPos(self, pos):
        scenePos = self.mapToScene(pos)
        self.sceneWidget().changeBrushPos(scenePos)
        self.updateScene()

    def getSelectedItems(self):
        return self.sceneWidget.selectedItems()

    def getSceneItems(self):
        return self.sceneWidget.getSceneItems()

    def updateScene(self):
        self.sceneWidget.update()
