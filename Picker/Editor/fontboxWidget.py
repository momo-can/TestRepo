# -*- coding: utf-8 -*-
import sys

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
    def __init__(self, parent=None, *args, **kwargs):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.fontdb = QFontDatabase()

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(10)

        gbox, lay, = customWidgets.groupWidget(
            label='Text'
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.shapeLabel = QLineEdit()
        lay.addWidget(self.shapeLabel)

        self.btn1 = QPushButton('Capitalize First Letter')
        mainLayout.addWidget(self.btn1)

        # gbox, lay, = customWidgets.groupWidget(
        #     label='Size', layoutType=1
        # )
        # mainLayout.addWidget(gbox)
        # lay.setContentsMargins(0, 0, 0, 0)
        # lay.setSpacing(0)
        # lay.setAlignment(Qt.AlignRight)

        # self.textSize = customWidgets.DoubleField(
        #     precision=0, minimum=1, maximum=999
        # )
        # self.textSize.setFixedWidth(100)
        # lay.addWidget(self.textSize)
        # self.textSize.setText('1')

    # def getFontFamilies(self):
    #     families = self.fontdb.families()
    #     families.sort()
    #     return families

    # def addFontFamilies(self):
    #     families = self.getFontFamilies()
    #     self.fontFamiliesList.addItems(families)

    # def getFontStyles(self, family=''):
    #     if not family:
    #         return []
    #     return self.fontdb.styles(family)

    # def addFontStyles(self):
    #     item = self.fontFamiliesList.currentItem()
    #     if not item:
    #         return
    #     self.fontStylesList.clear()
    #     family = item.text()
    #     styles = self.getFontStyles(family=family)
    #     self.fontStylesList.addItems(styles)

    def capitalizeFirstLetter(self):
        __str = self.shapeLabel.text()
        result = ''
        for i in xrange(len(__str)):
            if i == 0:
                result += __str[i].capitalize()
            else:
                result += __str[i]
        self.shapeLabel.setText(result)

    def getFont(self):
        # family = self.fontFamiliesList.currentItem()
        # if not family:
        #     return
        # style = self.fontStylesList.currentItem()
        # if not style:
        #     return
        # family_name = family.text()
        # style_name = style.text()
        family_name = 'Tahoma'
        style_name = 'Normal'
        # font_size = self.textSize.getValue()
        font_size = 1
        # if not family_name:
        #     family_name = 'MS UI Gothic'
        # if not style_name:
        #     style_name = 'Normal'
        return self.fontdb.font(
            family_name,
            style_name,
            int(font_size)
        )

# cls = MainClass()
# cls.show()
