# -*- coding: utf-8 -*-
import sys
import os

try:
    from importlib import reload
except Exception:
    pass

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

from customQtLibs import windowUtils
from Picker import namespaceWidget
from Picker.Core import tabWidget2 as tabWidget
from Picker.Viewer import function as viewerFunc
from Picker import pickerInterfaceCore
reload(windowUtils)
reload(tabWidget)
reload(namespaceWidget)
reload(viewerFunc)
reload(pickerInterfaceCore)

sys.dont_write_bytecode = True


class Interface(QMainWindow):
    def __init__(
        self,
        windowTitle='',
        objectName='',
        parent=None,
        isLocal=False,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.dockWidget = None
        self.currentMenus = []
        self.labels = []
        self.itemInfo = {}
        self.dirPath = os.path.dirname(__file__)
        self.assetName = None
        self.isLocal = isLocal

        # self.createPreDefines()

        self.setWindowTitle(windowTitle)
        self.setObjectName(objectName)
        self.setProperty('saveWindowPref', True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(1, 1, 1, 1)
        self.mainLayout.setSpacing(1)
        self.centralWidget.setLayout(self.mainLayout)

        self.menubarLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.menubarLayout)

        # Namespace
        self.namespaceWid = namespaceWidget.MainClass()
        self.mainLayout.addWidget(self.namespaceWid)
        self.namespaceWid.combobox.currentIndexChanged.connect(
            self.openPickerData
        )

        # Picker View
        self.tabWidget = tabWidget.TabWidget(
            namespaceWidget=self.namespaceWid,
            pickerInterfaceCore=pickerInterfaceCore,
            isEditable=False
        )
        self.mainLayout.addWidget(self.tabWidget)
        self.tabWidget.build()

        self.createMenu()
        self.openPickerData()

    def openPickerData(self):
        name = self.namespaceWid.combobox.currentText()
        path = viewerFunc.getPickerData(
            name=name,
            isLocal=self.isLocal
        )
        self.tabWidget.openPickerData(
            isViewer=True,
            userPath=path
        )

    def openCHTemplate(self):
        name = self.namespaceWid.combobox.currentText()
        path = viewerFunc.getPickerData(
            name=name,
            forceTemplate='chCommon',
            isLocal=self.isLocal
        )
        self.tabWidget.openPickerData(
            isViewer=True,
            userPath=path
        )

    def openVCTemplate(self):
        name = self.namespaceWid.combobox.currentText()
        path = viewerFunc.getPickerData(
            name=name,
            forceTemplate='vcCommon',
            isLocal=self.isLocal
        )
        self.tabWidget.openPickerData(
            isViewer=True,
            userPath=path
        )

    def openPROPTemplate(self):
        name = self.namespaceWid.combobox.currentText()
        path = viewerFunc.getPickerData(
            name=name,
            forceTemplate='propCommon',
            isLocal=self.isLocal
        )
        self.tabWidget.openPickerData(
            isViewer=True,
            userPath=path
        )

    def createMenu(self):
        #
        # Cast2 specifications
        #
        menuBar = self.menuBar()

        #
        # Select Menu
        #
        selectMenu = menuBar.addMenu('Select')

        act = QAction('All controllers', self)
        # act = QAction(QIcon('exit.png'), '&Exit', self)
        # act.setShortcut('Ctrl+Shift+A')
        act.setStatusTip('Select all controllers.')
        act.triggered.connect(self.selectAllController)
        selectMenu.addAction(act)

        selectMenu.addSeparator()

        act = QAction('Mirror target', self)
        act.setStatusTip('Select a symmetric controller.')
        act.triggered.connect(self.selectSymmetricController)
        selectMenu.addAction(act)

        act = QAction('Mirror target (Add)', self)
        act.setStatusTip('Select an additional symmetric controller.')
        act.triggered.connect(self.addSelectSymmetricController)
        selectMenu.addAction(act)

        #
        # Controller Menu
        #
        controllerMenu = menuBar.addMenu('Controller')

        act = QAction('Reset position', self)
        act.setStatusTip('Reset the position of the controller.')
        act.triggered.connect(self.resetControllerPosition)
        controllerMenu.addAction(act)

        #
        # Cast2 Menu
        #
        cast2Menu = menuBar.addMenu('Cast2')

        act = cast2Menu.addAction('')
        act.setDisabled(True)
        # act.setVisible(False)
        # act.setFixedHeight(1)

        separator = cast2Menu.addSeparator()
        separator.setText('Pose')

        act = QAction('Mirror Copy', self)
        act.setStatusTip('Copy the value to symmetry.')
        act.triggered.connect(self.mirrorPoseCopy)
        cast2Menu.addAction(act)

        separator = cast2Menu.addSeparator()
        separator.setText('Tools')

        act = QAction('Bake Simulation Rig', self)
        act.setStatusTip('Bake the simulation rig.')
        act.triggered.connect(self.bakeSimulationRig)
        cast2Menu.addAction(act)

        act = QAction('Convert IK/FK Animation', self)
        act.setStatusTip('Convert "IK" and "FK" animations.')
        act.triggered.connect(self.convertIKFKAnimation)
        cast2Menu.addAction(act)

        act = QAction('Convert IK Rotation', self)
        act.setStatusTip('Switch IK rotation controller.')
        act.triggered.connect(self.convertIkRotation)
        cast2Menu.addAction(act)

        act = QAction('Convert PoleVector', self)
        act.setStatusTip('Convert IK poleVector animations.')
        act.triggered.connect(self.convertPoleVector)
        cast2Menu.addAction(act)

        act = QAction('Switch Controller Parent', self)
        act.setStatusTip('Switch controller parent.')
        act.triggered.connect(self.convertParentSpace)
        cast2Menu.addAction(act)

        #
        # Template Menu
        #
        templateMenu = menuBar.addMenu('CAST2 Template')

        act = QAction('CH', self)
        act.setStatusTip('Open prop template.')
        act.triggered.connect(self.openCHTemplate)
        templateMenu.addAction(act)

        act = QAction('VC', self)
        act.setStatusTip('Open vc template.')
        act.triggered.connect(self.openVCTemplate)
        templateMenu.addAction(act)

        act = QAction('PROP', self)
        act.setStatusTip('Open prop template.')
        act.triggered.connect(self.openPROPTemplate)
        templateMenu.addAction(act)

        #
        # Help Menu
        #
        helpMenu = menuBar.addMenu('Help')

        act = QAction('Document', self)
        act.setStatusTip('Open the picker document.')
        act.triggered.connect(self.openHelp)
        act.setShortcut('F1')
        helpMenu.addAction(act)

    def selectAllController(self):
        namespace = self.namespaceWid.getNamespace()
        result = viewerFunc.selectAllController(namespace=namespace)
        if result[0] is False:
            mb = QMessageBox()
            mb.setIcon(mb.Icon.Information)
            mb.setText('The controller was not found.')
            mb.setWindowTitle("Information")
            mb.exec_()
            return
        self.tabWidget.updateView()

    def resetControllerPosition(self):
        viewerFunc.resetControllerPosition()

    def selectSymmetricController(self):
        viewerFunc.selectSymmetricController()

    def addSelectSymmetricController(self):
        viewerFunc.selectSymmetricController(isAdd=True)

    def mirrorPoseCopy(self):
        viewerFunc.mirrorPoseCopy()

    def bakeSimulationRig(self):
        viewerFunc.bakeSimulationRig()

    def convertIKFKAnimation(self):
        viewerFunc.convertIKFKAnimation()

    def convertIkRotation(self):
        viewerFunc.convertIkRotation()

    def convertPoleVector(self):
        viewerFunc.convertPoleVector()

    def convertParentSpace(self):
        viewerFunc.convertParentSpace()

    def openHelp(self):
        viewerFunc.openHelp()


def main(filters='', isNewWindow=False, isLocal=False):
    windowTitle = 'Picker - Trial Version'
    windowName = 'PickerWindow'
    if isNewWindow:
        count = 1
        while 1:
            windowName = 'PickerWindow{}'.format(count)
            windowTitle = 'Picker{}'.format(count)
            temp = windowUtils.getToplevelWidget(
                filters=windowTitle,
                isSkipWidgetType=True
            )
            if not temp or count > 100:
                break
            count += 1

    if isNewWindow is False:
        windowUtils.deleteWidget(objectName=windowName)
    parent = windowUtils.getToplevelWidget(filters=filters)
    w = Interface(
        windowTitle=windowTitle,
        objectName=windowName,
        isLocal=isLocal,
        parent=parent
    )
    w.show()

    # dirname = os.path.dirname(__file__)
    # dirname = dirname.replace(os.sep, '/')
    # n = os.path.basename(dirname)
    # dirname = dirname.replace(n, '')
    # path = '/'.join([
    #     dirname,
    #     'stylesheet.qss'
    # ])
    # if os.path.isfile(path):
    #     fileId = open(path, 'r')
    #     styleSheet = fileId.read()
    #     fileId.close()
    #     w.setStyleSheet(styleSheet)
    return w
