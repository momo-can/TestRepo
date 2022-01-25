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

from customQtLibs import windowUtils
from Picker import namespaceWidget
from Picker.CoreDebug import tabWidget2 as tabWidget
from Picker.Editor import pickerEditorRightContents
from Picker import pickerInterfaceCoreDebug as pickerInterfaceCore
reload(windowUtils)
reload(namespaceWidget)
reload(tabWidget)
reload(pickerEditorRightContents)
reload(pickerInterfaceCore)

sys.dont_write_bytecode = True


class Interface(QMainWindow):
    def __init__(
        self,
        windowTitle='',
        objectName='',
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.currentMenus = []
        self.labels = []
        self.itemInfo = {}
        self.dirPath = os.path.dirname(__file__)
        self.assetName = None

        # self.createPreDefines()

        self.setWindowTitle(windowTitle)
        self.setObjectName(objectName)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setProperty('saveWindowPref', True)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QHBoxLayout()
        centralWidget.setLayout(self.mainLayout)

        self.mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        #
        # Left contents...
        #
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(0)
        self.mainLayout.addLayout(leftLayout)

        # Namespace
        self.namespaceWid = namespaceWidget.MainClass()
        leftLayout.addWidget(self.namespaceWid)

        # Picker View
        self.tabWidget = tabWidget.TabWidget(
            namespaceWidget=self.namespaceWid,
            pickerInterfaceCore=pickerInterfaceCore
        )
        leftLayout.addWidget(self.tabWidget)
        self.tabWidget.build()

        #
        # Right contents...
        #
        self.rightWidget = pickerEditorRightContents.Widget(
            tabWidget=self.tabWidget
        )
        self.rightWidget.funcWid.setTab(widget=self.tabWidget)
        self.mainLayout.addWidget(self.rightWidget)

        self.createMenu()

    def createMenu(self):
        menuBar = self.menuBar()

        menu = QMenu('File')
        menuBar.addMenu(menu)

        action = menu.addAction('Open Project')
        action.setShortcut('Ctrl+o')
        action.triggered.connect(self.openProject)

        action = menu.addAction('Create Project')
        action.setShortcut('Ctrl+Shift+s')
        action.triggered.connect(self.createProject)

        menu.addSeparator()

        action = menu.addAction('Save')
        action.setShortcut('Ctrl+s')
        action.triggered.connect(self.saveOverridePickerData)

        menu.addSeparator()

        action = menu.addAction('Import Project')
        action.setShortcut('Ctrl+i')
        action.triggered.connect(self.importProject)

        menu.addSeparator()

        action = menu.addAction('Delete Tab')
        action.triggered.connect(self.deleteTab)

        menu.addSeparator()

        action = menu.addAction('Capture')
        action.triggered.connect(self.screenCapture)

    def openProject(self):
        workpath = self.tabWidget.openPickerData()
        self.rightWidget.createWid.workpath = workpath
        self.workpath = workpath

    def importProject(self):
        self.tabWidget.openPickerData(option='import')

    def deleteTab(self):
        self.tabWidget.removeAllTab()

    def createProject(self):
        self.rightWidget.createWid.workpath = self.tabWidget.savePickerData()

    def saveOverridePickerData(self):
        self.tabWidget.savePickerData(
            workpath=self.workpath
        )

    def screenCapture(self):
        self.tabWidget.screenShot(workpath=self.workpath)

    # def createPreDefines(self):
    #     self.userName = os.environ.get('user')
    #     self.projectName = os.environ.get('PROJECT_NAME')


def main(filters=''):
    windowTitle = 'Picker Editor'
    windowName = 'PickerEditorWindow'
    windowUtils.deleteWidget(objectName=windowName)
    parent = windowUtils.getToplevelWidget(filters=filters)
    w = Interface(
        windowTitle=windowTitle,
        objectName=windowName,
        parent=parent
    )
    w.show()

    dirname = os.path.dirname(__file__)
    dirname = dirname.replace(os.sep, '/')
    n = os.path.basename(dirname)
    dirname = dirname.replace(n, '')
    path = '/'.join([
        dirname,
        'stylesheet.qss'
    ])
    if os.path.isfile(path):
        fileId = open(path, 'r')
        styleSheet = fileId.read()
        fileId.close()
        w.setStyleSheet(styleSheet)
    return w
