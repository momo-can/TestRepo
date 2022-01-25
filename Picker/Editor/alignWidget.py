# -*- coding: utf-8 -*-
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class MainClass(QGroupBox):
    def __init__(
        self,
        pickerWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.pickerWidget = pickerWidget

        self.setTitle('Align Position')

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        btn = QPushButton(u'Left')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.setAlignLeft)
        btn = QPushButton(u'Top')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.setAlignTop)
        btn = QPushButton(u'Right')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.setAlignRight)
        btn = QPushButton(u'Bottom')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.setAlignBottom)

    def editPosition(self, alignX=None, alignY=None):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return

        posX = []
        posY = []
        for item in items:
            x = item.x()
            y = item.y()
            posX.append(x)
            posY.append(y)
        posX.sort()
        posY.sort()

        if alignX is not None:
            for item in items:
                item.setX(posX[alignX])

        if alignY is not None:
            for item in items:
                item.setY(posY[alignY])

    def setAlignLeft(self):
        self.editPosition(alignX=0)

    def setAlignTop(self):
        self.editPosition(alignY=0)

    def setAlignRight(self):
        self.editPosition(alignX=-1)

    def setAlignBottom(self):
        self.editPosition(alignY=-1)
