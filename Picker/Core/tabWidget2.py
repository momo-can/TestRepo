# -*- coding: utf-8 -*-
import sys
import os
import json

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class RemoveDialogBox(QDialog):
    def __init__(
        self,
        text='',
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle('Warning')
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        label = QLabel('Do you want to delete "{0}" tab ?'.format(text))
        layout.addWidget(label)
        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        layout.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)


class ImportDialogBox(QDialog):
    def __init__(
        self,
        items=[],
        parent=None,
        pickerInterfaceCore=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle('Infomation')
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        label = QLabel('Please choice an item.')
        layout.addWidget(label)
        self.list = QListWidget()
        self.list.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        layout.addWidget(self.list)
        self.list.addItems(items)
        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        layout.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)


class TabBar(QTabBar):
    doubleClicked = Signal()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonDblClick:
            if self.tabRect(self.currentIndex()).contains(event.pos()):
                self.doubleClicked.emit()
        else:
            super(self.__class__, self).mousePressEvent(event)


class TabWidget(QTabWidget):
    def __init__(
        self,
        namespaceWidget=None,
        isEditable=True,
        pickerInterfaceCore=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.isEditable = isEditable
        self.pickerInterfaceCore = pickerInterfaceCore
        self.namespaceWidget = namespaceWidget

    def build(self):
        tabBar = TabBar(self)
        self.setTabBar(tabBar)
        if self.isEditable:
            tabBar.doubleClicked.connect(self.__renameTab)

        self.__addTab(user_name='New Tab', user_index=0)
        if self.isEditable:
            self.plusBtn = QPushButton('+')
            self.plusBtn.setFlat(True)
            self.plusBtn.clicked.connect(self.__addTab)
            self.setCornerWidget(self.plusBtn, Qt.TopRightCorner)

            # Properties
            self.setMovable(True)
            self.setTabsClosable(True)
            self.tabCloseRequested.connect(self.__remTab)

    def getCurrentTab(self):
        currentWidget = self.currentWidget()
        if not currentWidget:
            return None
        return currentWidget

    def getCurrentPickerView(self):
        tab = self.getCurrentTab()
        if not tab:
            return
        childs = tab.children()
        pickerWidget = None
        for child in childs:
            __objectName = child.objectName()
            if __objectName == 'pickerWidget':
                pickerWidget = child
                break
        return pickerWidget

    def getPickerWidget(self, tab=None):
        pickerWidget = None
        if not tab:
            return pickerWidget
        children_widget = tab.children()
        for child_widget in children_widget:
            child_object_name = child_widget.objectName()
            if child_object_name == 'pickerWidget':
                pickerWidget = child_widget
                break
        return pickerWidget

    def deleteTab(self):
        tab_indecies = self.count()
        self.__addTab(
            user_name='New Tab',
            user_index=0
        )
        for i in xrange(tab_indecies):
            self.__remTab(index=i, prompt=False)

    def openPickerData(
        self,
        isViewer=False,
        option='',
        userPath=''
    ):
        # File dialog.
        if not userPath:
            dlg = QFileDialog(self, 'Open', 'C:/')
            dlg.setFileMode(QFileDialog.Directory)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
            dlg.setOptions(
                QFileDialog.ShowDirsOnly |
                QFileDialog.HideNameFilterDetails |
                QFileDialog.DirectoryOnly
            )
            dlg.setLabelText(QFileDialog.Accept, 'Save')
            path = dlg.getExistingDirectory()
            if not path:
                return ''
            if path:
                dlg.setHistory(path)
            if isinstance(path, list):
                path = path[0].replace(os.sep, '/')
        else:
            path = userPath
        self.workpath = path

        # Get data.
        dataPath = '/'.join([path, 'pickerData.json'])
        if not os.path.isfile(dataPath):
            return ''
        fileId = open(dataPath, 'r')
        pickerData = json.load(fileId)
        fileId.close()
        # Get data version.
        pickerData.pop(0)

        # Delete all tab.
        if option not in ['import'] or not option:
            self.removeAllTab()
        else:
            tabNames = []
            for i, data in enumerate(pickerData):
                tabName = data.get('tabName', 'New Tab')
                tabNames.append(tabName)
            dialog = ImportDialogBox(items=tabNames)
            if dialog.exec_() != QDialog.Accepted:
                return
            items = dialog.list.selectedItems()
            items = [list_item.text() for list_item in items]

        # Create tabs.
        for i, data in enumerate(pickerData):
            tabName = data.get('tabName', 'New Tab')
            pickerWidget = self.getCurrentPickerView()
            if option == 'import':
                if tabName not in items:
                    continue
            if i == 0 and option != 'import':
                self.__renameTab(text=tabName, prompt=False)
                items = pickerWidget.getSceneItem()
                for item in items:
                    pickerWidget.deleteItem(item)
            else:
                self.__addTab(user_name=tabName)

            # Create tab items.
            tab_item = data.get('tab_item', [])
            for i, item in enumerate(tab_item):
                shapeType = item.get('shapeType', None)
                if shapeType == 'ImageItem':
                    filename = item.get('image_path', '')
                    locked = item.get('locked', True)
                    if isViewer:
                        locked = True
                    pos_x = item.get('x', 0.0)
                    pos_y = item.get('y', 0.0)
                    scale = item.get('scale', 5.0)
                    __path = '/'.join([self.workpath, filename])
                    item = self.importImage(path=__path)
                    item.setScale(scale)
                    item.setX(pos_x)
                    item.setY(pos_y)
                    if locked:
                        item.setFlags(QGraphicsItem.GraphicsItemFlags())
                        item._locked = locked
                else:
                    color = item.get('color', [128, 128, 128, 255])
                    font = item.get('font', 'Tahoma,12,-1,5,50,0,0,0,0,0')
                    locked = item.get('locked', False)
                    if isViewer:
                        locked = True
                    pickItemData = item.get('pickItemData', '')
                    pickItemType = item.get('pickItemType', 'object')
                    pickItemShowHide = item.get('pickItemShowHide', {})
                    pos_x = item.get('x', .0)
                    pos_y = -item.get('y', .0)
                    rect_scale = item.get('rect_scale', 10.0)
                    scale = item.get('scale', 1.0)
                    style = item.get('style', 'Square')
                    text = item.get('text', '')
                    view_text = item.get('view_text', False)
                    itemName = item.get('itemName', '')
                    groupsRectSize = item.get('groupsRectSize', [1, 1])
                    qfont = QFont()
                    font_data = font.split(',')
                    qfont.setFamily(font_data[0])
                    qfont.setPixelSize(int(font_data[1]))
                    if int(font_data[4]) == 75:
                        qfont.setBold(True)
                    if int(font_data[5]) == 1:
                        qfont.setItalic(True)
                    item = self.createShape(
                        style=style,
                        scale=rect_scale,
                        color=QBrush(
                            QColor(
                                color[0],
                                color[1],
                                color[2],
                                color[3]
                            )
                        ),
                        text=text,
                        font=qfont,
                        pos_x=pos_x,
                        pos_y=pos_y
                    )
                    item.setScale(scale)
                    item.pickItemData = pickItemData
                    item.pickItemType = pickItemType
                    item.pickItemShowHide = pickItemShowHide
                    item.view_text = view_text
                    item.itemName = itemName
                    item.groupsRectSize = groupsRectSize
                    if locked:
                        item.setFlags(QGraphicsItem.GraphicsItemFlags())
                        item.setFlags(
                            QGraphicsItem.ItemIsSelectable
                        )
                        item._locked = locked
                    if isViewer and pickItemType in ['Select']:
                        if style in ['Groups']:
                            item.setFlags(QGraphicsItem.GraphicsItemFlags())
        for i in xrange(self.count()):
            tabWidget = self.widget(i)
            pickerWidget = self.getPickerWidget(tab=tabWidget)
            view = pickerWidget.getView()
            if self.isEditable is False:
                view.setSceneRectFromItems()
            view.viewFit()
        self.setCurrentIndex(0)

        return path

    def savePickerData(self, workpath=''):
        pickerData = []
        pickerData.append({'version': 1.0})
        for i in xrange(self.count()):
            tabWidget = self.widget(i)
            if not tabWidget:
                continue
            tabName = self.tabText(i)
            pickerWidget = self.getPickerWidget(tab=tabWidget)
            if not pickerWidget:
                continue
            item_status = pickerWidget.getItemStatus()
            pickerData.append({
                'tabName': tabName.encode('shift_jis'),
                'tab_index': i,
                'tab_item': item_status
            })

        if not workpath:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.Directory)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
            dlg.setOptions(
                QFileDialog.ShowDirsOnly |
                QFileDialog.HideNameFilterDetails |
                QFileDialog.DirectoryOnly
            )
            dlg.setLabelText(QFileDialog.Accept, 'Save')
            workpath = dlg.getExistingDirectory()
            if not workpath:
                return
            if workpath:
                dlg.setHistory(workpath)
            if isinstance(workpath, list):
                workpath = workpath[0].replace(os.sep, '/')

        if not os.path.isdir(workpath):
            os.makedirs(workpath)
        dataPath = '/'.join([workpath, 'pickerData.json'])
        fileId = open(dataPath, 'w')
        json.dump(
            pickerData,
            fileId,
            indent=4
        )
        fileId.close()

        return workpath

    def getSelectedItems(self):
        pickerWidget = self.getCurrentPickerView()
        return pickerWidget.getSelectedItems()

    def getSceneItem(self):
        pickerWidget = self.getCurrentPickerView()
        return pickerWidget.getSceneItem()

    def getWorkpath(self):
        return self.workpath

    def screenShot(self, workpath=''):
        pickerWidget = self.getCurrentPickerView()
        pickerWidget.screenCapture(workpath=workpath)

    def importImage(self, path=''):
        pickerWidget = self.getCurrentPickerView()
        item = pickerWidget.setImage(path=path)
        return item

    def autoCreateShape(
        self,
        style='Square',
        scale=1.0,
        color=QBrush(Qt.lightGray),
        text='',
        font=QFont('MS UI Gothic', 20, QFont.Bold),
        pos_x=.0,
        pos_y=.0
    ):
        pickerWidget = self.getCurrentPickerView()
        pickerWidget.autoCreateShape(
            style=style,
            scale=scale,
            color=color,
            text=text,
            font=font,
            pos_x=pos_x,
            pos_y=pos_y
        )

    def createShape(
        self,
        style='Square',
        scale=1.0,
        color=QBrush(Qt.lightGray),
        text='',
        font=QFont('MS UI Gothic', 20, QFont.Bold),
        pos_x=.0,
        pos_y=.0
    ):
        pickerWidget = self.getCurrentPickerView()
        item = pickerWidget.createShape(
            style=style,
            scale=scale,
            color=color,
            text=text,
            font=font,
            pos_x=pos_x,
            pos_y=pos_y
        )
        return item

    def __addTab(
        self,
        user_name='',
        user_index=None
    ):
        tabName = ''
        status = None
        if not user_name and not user_index:
            tabName, status = QInputDialog.getText(
                self,
                'Add Tab',
                'Specify new name',
                QLineEdit.Normal,
                'New Tab'
            )
        else:
            status = True
        if not status:
            return
        index = self.count()

        if user_name:
            tabName = user_name
        if user_index is not None:
            index = user_index

        tmpWidget = QWidget()
        tmpWidget.setObjectName('pickerWidget')
        tmpLayout = QVBoxLayout()
        tmpLayout.setContentsMargins(5, 0, 5, 0)
        tmpWidget.setLayout(tmpLayout)
        pickerWidget = self.pickerInterfaceCore.Widget(
            namespaceWidget=self.namespaceWidget,
            isEditable=self.isEditable
        )
        # pickerWidget.setObjectField(widget=self.function_widget[0])
        # pickerWidget.setScriptField(widget=self.function_widget[1])
        pickerWidget.setObjectName('pickerWidget')
        tmpLayout.addWidget(pickerWidget)

        self.insertTab(index, tmpWidget, tabName)
        self.setCurrentIndex(index)

    def removeAllTab(self):
        self.__addTab(user_name='__TEMP Tab', user_index=0)
        count = self.count()
        for i in range(count):
            __index = count - i
            text = self.tabText(__index)
            if text in ['__TEMP Tab']:
                continue
            self.__remTab(index=__index, prompt=False)
        self.__addTab(user_name='New Tab', user_index=0)
        self.__remTab(index=1, prompt=False)

    def __remTab(self, index=0, prompt=True):
        if self.count() <= 1:
            return
        text = self.tabText(index)
        if prompt:
            dialog = RemoveDialogBox(text=text)
            if dialog.exec_() != QDialog.Accepted:
                return
        self.removeTab(index)

    def __renameTab(self, text='New Tab', prompt=True):
        status = True
        if prompt:
            text, status = QInputDialog.getText(
                self,
                'Rename Tab',
                'Specify new name',
                QLineEdit.Normal,
                self.tabText(self.currentIndex())
            )

        if not status:
            return

        self.setTabText(self.currentIndex(), text)

    def updateView(self):
        __view = self.getCurrentPickerView()
        __view.updateScene()
