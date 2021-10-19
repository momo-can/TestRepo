# -*- coding: utf-8 -*-
import sys
# from pprint import pprint

try:
    from importlib import reload
except Exception:
    pass

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

from customQtLibs import windowUtils
from CustomNamespaceEditor import baseWidget
from CustomNamespaceEditor import customWidgets
from CustomNamespaceEditor import function
reload(windowUtils)
reload(customWidgets)
reload(baseWidget)
reload(function)

sys.dont_write_bytecode = True


class Interface(QMainWindow):
    def __init__(
        self,
        objectName=None,
        windowTitle='Window1',
        # department=None,
        parent=None
    ):
        super(self.__class__, self).__init__(parent=parent)
        # Set attributes.
        self.setObjectName(objectName)
        self.setWindowTitle(windowTitle)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setProperty('saveWindowPref', True)
        # self.department = department

        self.build()

    def build(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)
        mainLayout.setAlignment(Qt.AlignTop)
        centralWidget.setLayout(mainLayout)

        gbox, glay = customWidgets.groupWidget(label='List')
        mainLayout.addWidget(gbox)

        self.baseWidget = baseWidget.Widget()
        mainLayout.addWidget(self.baseWidget)
        glay.addWidget(self.baseWidget)

        btn = QPushButton('Rename')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.rename)

        self.createMenu()

        css = '''
                QGroupBox {
                    padding: 10px 1px 1px 1px;
                    border: 1px solid #ccc;
                }

                QWidget {
                    font-size: 10pt;
                }
            '''
        self.setStyleSheet(css)

    def createMenu(self):
        menuBar = self.menuBar()

        #
        # Display Menu
        #
        selectMenu = menuBar.addMenu('Display')

        act = QAction('Update asset list', self)
        # act = QAction(QIcon('exit.png'), '&Exit', self)
        # act.setShortcut('Ctrl+Shift+A')
        act.setStatusTip('Select all controllers.')
        act.triggered.connect(self.updateAssetList)
        selectMenu.addAction(act)

        #
        # Help Menu
        #
        helpMenu = menuBar.addMenu('Help')

        act = QAction('Document', self)
        act.setStatusTip('Open the picker document.')
        act.triggered.connect(self.openHelp)
        act.setShortcut('F1')
        helpMenu.addAction(act)

    def updateAssetList(self):
        self.baseWidget.updateTable()

    def openHelp(self):
        function.openHelp()

    def rename(self):
        userInputs = self.baseWidget.getTableData()
        function.editReferenceName(userInputs=userInputs)
        self.baseWidget.updateTable()


def main(filters='', department=''):
    windowName = 'NamespaceEditorWindow'
    windowUtils.deleteWidget(objectName=windowName)
    parentWidget = windowUtils.getToplevelWidget(filters=filters)
    window = Interface(
        objectName=windowName,
        windowTitle='Namespace Editor',
        parent=parentWidget
    )
    window.show()
