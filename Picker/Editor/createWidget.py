# -*- coding: utf-8 -*-
import os
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

from Picker import customWidgets
from Picker import config
from Picker.Editor import fontboxWidget
reload(customWidgets)
reload(config)
reload(fontboxWidget)

sys.dont_write_bytecode = True


class CreateSection(QWidget):
    def __init__(
        self,
        tabWidget=None,
        parent=None,
        isEditableShape=True,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.tabWidget = tabWidget
        self.editWidget = None
        self.workpath = ''
        self.isEditableShape = isEditableShape

        baseLaoyut = QVBoxLayout()
        baseLaoyut.setContentsMargins(0, 0, 0, 0)
        baseLaoyut.setSpacing(0)
        self.setLayout(baseLaoyut)

        mainGroup, mainLayout, = customWidgets.groupWidget(label='Create')
        baseLaoyut.addWidget(mainGroup)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        gbox, lay, = customWidgets.groupWidget(
            label='Item Style', layoutType=1
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.shapeStyle = customWidgets.ComboBox()
        self.shapeStyle.addItems(config.itemStyle)
        lay.addWidget(self.shapeStyle)

        gbox, lay, = customWidgets.groupWidget(
            label='Item Size'
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignRight)

        self.shapeSize = customWidgets.DoubleFieldGrp(
            text='',
            minimum=1,
            maximum=999,
            precision=0
        )
        self.shapeSize.setFixedWidth(100)
        lay.addWidget(self.shapeSize)
        self.shapeSize.field.setText('10')

        gbox, lay, = customWidgets.groupWidget(
            label='Label'
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.fontBox = fontboxWidget.MainClass()
        lay.addWidget(self.fontBox)
        self.fontBox.btn1.setVisible(False)

        gbox, lay, = customWidgets.groupWidget(
            label='Create Functions', layoutType=1
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        createBtn = QPushButton('Create')
        lay.addWidget(createBtn)
        createBtn.clicked.connect(self.createShape)

        autoCreateBtn = QPushButton('Auto')
        lay.addWidget(autoCreateBtn)
        autoCreateBtn.clicked.connect(self.autoCreateShape)

    def savePickerData(self, workpath=''):
        self.workpath = self.tabWidget.savePickerData(workpath=workpath)

    def createShape(self):
        shapeColor = QColor(Qt.lightGray)
        if self.editWidget:
            r, g, b = self.editWidget.getColor()
            shapeColor = QBrush(QColor(r, g, b))
        __style = self.shapeStyle.currentText()
        __scale = self.shapeSize.getValue()
        __text = self.fontBox.shapeLabel.text()
        __font = self.fontBox.getFont()
        self.tabWidget.createShape(
            style=__style,
            scale=__scale,
            color=shapeColor,
            text=__text,
            font=__font
        )
        self.update()

    def autoCreateShape(self):
        shapeColor = QColor(Qt.lightGray)
        if self.editWidget:
            r, g, b = self.editWidget.getColor()
            shapeColor = QBrush(QColor(r, g, b))
        __style = self.shapeStyle.currentText()
        __scale = self.shapeSize.getValue()
        __text = self.fontBox.shapeLabel.text()
        __font = self.fontBox.getFont()
        self.tabWidget.autoCreateShape(
            style=__style,
            scale=__scale,
            color=shapeColor,
            text=__text,
            font=__font
        )

    def getFont(self):
        return self.fontBox.getFont()


def getUserImage():
    username = os.environ.get('user')
    local_path = '/'.join(['D:', username])
    if not os.path.isdir(local_path):
        local_path = 'D:/'
    path = QFileDialog.getOpenFileName(
        None,
        'Select an image',
        local_path,
        'Image File (*.png)',
        '*.png'
    )
    if path:
        return path[0]
    return None


class CaptureSection(QWidget):
    def __init__(
        self,
        tabWidget=None,
        createWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.tabWidget = tabWidget
        self.createWidget = createWidget

        baseLayout = QVBoxLayout()
        baseLayout.setContentsMargins(0, 0, 0, 0)
        baseLayout.setSpacing(0)
        self.setLayout(baseLayout)

        gbox, lay, = customWidgets.groupWidget(
            label='Capture Functions', layoutType=1
        )
        baseLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        createBtn = QPushButton('Create')
        lay.addWidget(createBtn)
        createBtn.clicked.connect(self.screenShot)

        createBtn = QPushButton('Import')
        lay.addWidget(createBtn)
        createBtn.clicked.connect(self.importImage)

    def screenShot(self):
        workpath = self.createWidget.workpath
        if not workpath:
            QMessageBox.warning(
                None,
                'Workpath was not found.',
                'Please make a workpath.',
                QMessageBox.Close
            )
            return
        self.tabWidget.screenShot(workpath=workpath)

    def importImage(self):
        path = getUserImage()
        self.tabWidget.importImage(path=path)


class MainClass(QWidget):
    def __init__(
        self,
        tabWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.createWid = CreateSection(tabWidget=tabWidget)
        mainLayout.addWidget(self.createWid)

        ssWid = CaptureSection(
            tabWidget=tabWidget,
            createWidget=self.createWid
        )
        mainLayout.addWidget(ssWid)

    # def openPickerData(self, option=''):
    #     self.createWid.openPickerData(option=option)

    def savePickerData(self, workpath=''):
        self.createWid.savePickerData(workpath=workpath)

    def saveOverridePickerData(self):
        self.savePickerData(workpath=self.createWid.workpath)

    def getFont(self):
        return self.createWid.getFont()

    def setEditWidget(self, widget=None):
        self.editWidget = widget
        self.createWid.editWidget = self.editWidget
