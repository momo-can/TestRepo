# -*- coding: utf-8 -*-
import re
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class MainClass(QGroupBox):
    def __init__(self, pickerWidget=None, parent=None, *args, **kwargs):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.pickerWidget = pickerWidget

        self.setTitle('Mirror Position')
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.isTypes = QButtonGroup()
        lay = QHBoxLayout()
        rad = QRadioButton('?_')
        rad.setChecked(True)
        lay.addWidget(rad)
        self.isTypes.addButton(rad, 0)
        rad = QRadioButton('_?_')
        lay.addWidget(rad)
        self.isTypes.addButton(rad, 1)
        rad = QRadioButton('_?')
        lay.addWidget(rad)
        self.isTypes.addButton(rad, 2)
        mainLayout.addLayout(lay)

        self.isResource = QButtonGroup()
        lay = QHBoxLayout()
        rad = QRadioButton('L')
        rad.setChecked(True)
        lay.addWidget(rad)
        self.isResource.addButton(rad, 0)
        rad = QRadioButton('R')
        lay.addWidget(rad)
        self.isResource.addButton(rad, 1)
        mainLayout.addLayout(lay)

        self.isCaps = QButtonGroup()
        lay = QHBoxLayout()
        rad = QRadioButton('Large')
        rad.setChecked(True)
        lay.addWidget(rad)
        self.isCaps.addButton(rad, 0)
        rad = QRadioButton('Small')
        lay.addWidget(rad)
        self.isCaps.addButton(rad, 1)
        mainLayout.addLayout(lay)

        btn = QPushButton('Mirror')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.editPosition)

    def editPosition(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        type_index = self.isTypes.checkedId()
        mirror_types = ['^{0}_', '_{0}_', '_{0}$']
        replace_types = ['{0}_', '_{0}_', '_{0}']
        dst = 'L'
        src = 'R'
        if self.isResource.checkedId() == 1:
            dst = 'R'
            src = 'L'
        if self.isCaps.checkedId() == 1:
            dst = dst.lower()
            src = src.lower()

        search_filter = mirror_types[type_index].format(dst)
        replace_filter = replace_types[type_index].format(src)

        reference_position = {}
        for item in items:
            mirror_name = ''
            name = item.text
            if not name:
                continue
            if re.search(search_filter, name):
                mirror_name = re.sub(
                    search_filter,
                    replace_filter,
                    name
                )
            if not mirror_name:
                continue
            pos = item.pos()
            reference_position[mirror_name] = pos

        allItems = self.pickerWidget.getSceneItem()
        for item in allItems:
            item_name = item.text
            item_pos = reference_position.get(item_name, None)
            if not item_pos:
                continue
            x = item_pos.x() * -1.
            y = item_pos.y()
            item.setX(x)
            item.setY(y)
