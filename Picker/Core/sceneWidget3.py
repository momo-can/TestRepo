# -*- coding: utf-8 -*-
import sys
import os
import re
import imp
import ast
import copy

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class Scene(QGraphicsScene):
    def __init__(
        self,
        isEditable=True,
        namespaceWidget=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.isEditable = isEditable
        self.namespaceWidget = namespaceWidget
        self.selListOld = []
        self.mouseButtonType = 0
        dirname = os.path.dirname(__file__)
        dirname = dirname.replace(os.sep, '/')
        names = dirname.split('/')
        root = dirname.replace('/{}'.format(names[-1]), '')
        self.pluginPath = '/'.join([
            root,
            'Plugins'
        ])

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() is QEvent.Type.Enter:
            self.updateProcess()
        return super(self.__class__, self).eventFilter(object, event)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(60, 60, 60))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouseButtonType = 0
        if event.button() == Qt.MidButton:
            self.mouseButtonType = 1
        if event.button() == Qt.RightButton:
            self.mouseButtonType = 2

        if self.mouseButtonType != 0:
            return

        x = event.scenePos().x()
        y = event.scenePos().y()
        self.onItem = self.itemAt(
            x,
            y,
            QTransform()
        )

        # Get old item.
        items = self.selectedItems()
        self.oldItems = [item.itemName for item in items]

        # Clear item.
        for n in self.items():
            n.setSelected(False)

        modifiers = QApplication.keyboardModifiers()
        self.modifiers = 0
        if modifiers == Qt.ShiftModifier:
            self.modifiers = 1
        elif modifiers == Qt.ControlModifier:
            self.modifiers = 2

        if self.onItem and self.onItem._locked is False:
            for item in items:
                item.setSelected(True)

        super(self.__class__, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mouseButtonType != 0:
            return
        tempItems = self.selectedItems()
        self.newItems = []
        for item in tempItems:
            if not getattr(item, 'itemName', None):
                continue
            data = item.itemName
            self.newItems.append(data)

        targetNames = copy.deepcopy(self.oldItems)
        if self.modifiers == 0:
            targetNames = copy.deepcopy(self.newItems)
        if self.modifiers == 1:
            targetNames += self.newItems
            targetNames = list(set(targetNames))
        elif self.modifiers == 2:
            for n in self.newItems:
                if n in targetNames:
                    targetNames.remove(n)
                else:
                    targetNames.append(n)

        targetItems = []
        for n in self.items():
            if getattr(n, 'setSelectedFunc', None):
                n.setSelectedFunc()
            itemName = getattr(n, 'itemName', None)
            if not itemName:
                continue
            if n.itemName not in targetNames:
                continue
            targetItems.append(n)

        self.selListNew = self.selectedItems()
        # pickItemData = ''
        pickItemType = ''
        functionItems = []
        isItemVisibility = False
        for n in targetItems:
            if getattr(
                n, 'pickItemType', None
            ):
                pickItemType = n.pickItemType

            if pickItemType in ['ItemVisibility']:
                data = n.pickItemData
                data = ast.literal_eval(data)
                item = data.get('item', [])
                value = data.get('value', [])
                self.toggleVisible(
                    names=item,
                    value=value
                )
                isItemVisibility = True

            if pickItemType in ['Function']:
                functionItems.append(n)

        if functionItems:
            for func in functionItems:
                data = func.pickItemData
                self.executeCommand(data=data)
                for item in self.items():
                    item.setSelected(False)
            return

        # Select items.
        results = []
        for item in targetItems:
            value = True
            if getattr(
                item, 'pickItemData', None
            ):
                __data = item.pickItemData
                if re.search('\n', __data):
                    if self.isEditable is False:
                        value = False
                __data = __data.split('\n')
                __data = [n.encode('shift_jis') for n in __data]
                results += __data
            if getattr(item, 'setSelectedFunc', None):
                item.setSelectedFunc(value=value)
        if isItemVisibility:
            results = []
        self.selectCommand(results=results)

        # for t in targetItems:
        #     t.setSelected(True)
        super(self.__class__, self).mouseReleaseEvent(event)

    def toggleVisible(self, names=[], value=None):
        items = self.items()
        results = []
        for item in items:
            if item.itemName not in names:
                continue
            results.append(item)
        for res in results:
            __value = False if res.isVisible() else True
            if value is not None:
                __value = value
            res.setVisible(__value)

    def loadPlugin(self, name=''):
        if not os.path.isdir(self.pluginPath):
            return None
        pluginPath = '/'.join([
            self.pluginPath,
            '{}.py'.format(name)
        ])
        if not os.path.isfile(pluginPath):
            return None
        mod = imp.load_source(
            'mod_{}'.format(name),
            pluginPath
        )
        return mod

    def selectCommand(self, results=[]):
        name = 'select'
        mod = self.loadPlugin(name=name)
        if not mod:
            return
        flags = {'r': True}
        ns = self.namespaceWidget.getNamespace()
        if ns and results:
            results = [':'.join([ns, r]) for r in results]
        if not results:
            flags = {'cl': True}
        if self.modifiers in [1, 2]:
            flags['isRestore'] = True
        mod.main(nodes=results, **flags)

    def restoreSelection(self):
        name = 'restoreSelection'
        mod = self.loadPlugin(name=name)
        if not mod:
            return
        ns = self.namespaceWidget.getNamespace()
        flags = {'namespace': ns}
        results = mod.main(**flags)
        items = self.items()
        for item in items:
            itemName = getattr(item, 'itemName', None)
            if itemName:
                itemName = item.itemName
            if itemName not in results:
                __func = getattr(item, 'setSelectedFunc', None)
                if __func:
                    item.setSelectedFunc()
                continue
            item.setSelectedFunc(value=True)

    def selectAllItems(self):
        items = self.items()
        results = []
        for item in items:
            if getattr(item, 'setSelectedFunc', None):
                if item.pickItemData:
                    data = item.getStatus()
                    pickItemData = data.get('pickItemData', '')
                    if re.search('\n', pickItemData):
                        continue
                    item.setSelectedFunc(value=True)
                    results.append(item.pickItemData)
        self.selectCommand(results=results)

    def updateProcess(self):
        items = self.items()
        ns = self.namespaceWidget.getNamespace()
        mod = self.loadPlugin(name='getVisible')
        for item in items:
            pickItemShowHide = getattr(item, 'pickItemShowHide', None)
            if pickItemShowHide:
                pickItemShowHide = item.pickItemShowHide
            if not pickItemShowHide:
                continue
            if type(pickItemShowHide) != list:
                pickItemShowHide = [pickItemShowHide]
            result = 1
            for d in pickItemShowHide:
                _forceShow = getattr(item, '_forceShow', False)
                if _forceShow:
                    item.setVisible(True)
                    continue

                name = d.get('name', '')
                attribute = d.get('attribute', '')
                reverse = d.get('reverse', 0)
                if ns:
                    name = ':'.join([ns, name])
                __flags = {
                    'name': name,
                    'attribute': attribute,
                }
                value = mod.main(**__flags)
                if value is None:
                    value = True
                else:
                    if reverse == 1:
                        value = False if value else True
                result *= value
            item.setVisible(result)
        self.restoreSelection()

    def executeCommand(self, data=''):
        ns = self.namespaceWidget.getNamespace()
        mod = self.loadPlugin(name='setValue')
        data = ast.literal_eval(data)
        pluginType = data.get('pluginType', 'file')
        if pluginType in ['file']:
            data.update({'namespace': ns})
            mod.main(**data)
            self.updateProcess()
        else:
            data = data.get('data', '')
            exec(data)
