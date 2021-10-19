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

from CustomNamespaceEditor import customWidgets
from CustomNamespaceEditor import function
reload(customWidgets)
reload(function)

sys.dont_write_bytecode = True


class Widget(QWidget):
    def __init__(
        self,
        department='',
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent)
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.namespaceTable = customWidgets.TableView()
        self.tableModel = customWidgets.TableModel()
        self.namespaceTable.setModel(self.tableModel)
        self.tableModel.selectionModel = self.namespaceTable.selectionModel()
        mainLayout.addWidget(self.namespaceTable)

        namespaceList = function.getReferenceNamespace()
        self.tableModel.items = namespaceList

    def getTableData(self):
        return self.tableModel.items

    def updateTable(self):
        namespaceList = function.getReferenceNamespace()
        self.tableModel.items = namespaceList
        self.tableModel.names = []
        self.namespaceTable.updateData()
