# -*- coding: utf-8 -*-
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

from Picker import namespaceWidgetFunction as func
reload(func)

sys.dont_write_bytecode = True


class MainClass(QWidget):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        innerLayout = QHBoxLayout(self)
        self.combobox = QComboBox()
        innerLayout.addWidget(self.combobox)
        mainLayout = QVBoxLayout()
        innerLayout.addLayout(mainLayout)
        btn = QPushButton('Update Asset')
        btn.setFixedWidth(200)
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.updateField)

        btn = QPushButton('Select Asset From Node')
        btn.setFixedWidth(200)
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.selectAssetFromNode)

        self.updateField()
        # self.installEventFilter(self)

    # def eventFilter(self, object, event):
    #     if event.type() in [QEvent.Type.Enter, QEvent.Type.Leave]:
    #         self.updateField()
    #     return super(self.__class__, self).eventFilter(object, event)

    def updateField(self):
        self.combobox.clear()
        items = func.getReferenceNamespace()
        self.combobox.addItems(items)

    def getNamespace(self):
        return self.combobox.currentText()

    def selectAssetFromNode(self):
        count = self.combobox.count()
        names = []
        for i in range(count):
            names.append(self.combobox.itemText(i))

        result = func.selectAssetFromNode(names=names)
        if result is None:
            return
        self.combobox.setCurrentIndex(result)
