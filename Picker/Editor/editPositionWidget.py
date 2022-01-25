# -*- coding: utf-8 -*-
import sys
from functools import partial

from pprint import pprint

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

from Picker import customWidgets
reload(customWidgets)

sys.dont_write_bytecode = True


class MainClass(QWidget):
    def __init__(
        self,
        pickerWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.pickerWidget = pickerWidget
        baseLayout = QVBoxLayout()
        self.setLayout(baseLayout)
        baseLayout.setContentsMargins(0, 0, 0, 0)
        baseLayout.setSpacing(0)

        gbox, mainLayout = customWidgets.groupWidget(label='Offset Position')
        baseLayout.addWidget(gbox)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(5)

        self.valueField = customWidgets.DoubleField(
            minimum=-1000000,
            maximum=1000000,
            precision=2
        )
        self.valueField.setAlignment(Qt.AlignRight)
        self.valueField.setText('1.0')
        mainLayout.addWidget(self.valueField)

        btnLayout = QHBoxLayout()
        mainLayout.addLayout(btnLayout)

        btn = QPushButton(u'←')
        btnLayout.addWidget(btn)
        btn.clicked.connect(partial(self.editPosition, 1, None))
        btn = QPushButton(u'↑')
        btnLayout.addWidget(btn)
        btn.clicked.connect(partial(self.editPosition, None, 1))
        btn = QPushButton(u'→')
        btnLayout.addWidget(btn)
        btn.clicked.connect(partial(self.editPosition, -1, None))
        btn = QPushButton(u'↓')
        btnLayout.addWidget(btn)
        btn.clicked.connect(partial(self.editPosition, None, -1))

    def editPosition(self, value_x=None, value_y=None):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        value = float(self.valueField.getValue())
        if value_x is not None:
            for item in items:
                pos = item.pos()
                item.setX(pos.x() + value * -value_x)
        if value_y is not None:
            for item in items:
                pos = item.pos()
                item.setY(pos.y() + value * -value_y)
        self.pickerWidget.updateView()
