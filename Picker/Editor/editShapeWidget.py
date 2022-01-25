# -*- coding: utf-8 -*-
import sys
from pprint import pprint

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

from Picker import customWidgets
from Picker import config
from Picker.Editor import colorPickerWidget
from Picker.Editor import fontboxWidget
reload(customWidgets)
reload(config)
reload(colorPickerWidget)
reload(fontboxWidget)

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

        gbox, mainLayout = customWidgets.groupWidget(label='Edit Shape')
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        baseLayout.addWidget(gbox)

        gbox, lay = customWidgets.groupWidget(label='Item Name')
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        mainLayout.addWidget(gbox)

        self.itemNameField = QLineEdit()
        lay.addWidget(self.itemNameField)
        self.itemNameField.returnPressed.connect(self.setItemName)

        gbox, lay = customWidgets.groupWidget(label='Current Style')
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        mainLayout.addWidget(gbox)

        self.itemStyleName = QLineEdit()
        self.itemStyleName.setEnabled(False)
        lay.addWidget(self.itemStyleName)

        gbox, lay = customWidgets.groupWidget(label='Position')
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        lay.setAlignment(Qt.AlignRight)

        self.posXField = customWidgets.DoubleFieldGrp(
            text='X ',
            minimum=-1000000,
            maximum=1000000,
            precision=2
        )
        self.posXField.setFixedWidth(100)
        lay.addWidget(self.posXField)

        self.posYField = customWidgets.DoubleFieldGrp(
            text='Y ',
            minimum=-1000000,
            maximum=1000000,
            precision=2
        )
        self.posYField.setFixedWidth(100)
        lay.addWidget(self.posYField)

        self.posXField.field.returnPressed.connect(self.setX)
        self.posYField.field.returnPressed.connect(self.setY)

        gbox, lay = customWidgets.groupWidget(label='Groups Rect')
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        lay.setAlignment(Qt.AlignRight)

        self.gRectW = customWidgets.DoubleFieldGrp(
            text='Width ',
            minimum=-1000000,
            maximum=1000000,
            precision=2
        )
        self.gRectW.setFixedWidth(100)
        lay.addWidget(self.gRectW)

        self.gRectH = customWidgets.DoubleFieldGrp(
            text='Height ',
            minimum=-1000000,
            maximum=1000000,
            precision=2
        )
        self.gRectH.setFixedWidth(100)
        lay.addWidget(self.gRectH)

        self.gRectW.field.returnPressed.connect(self.setGroupRectW)
        self.gRectH.field.returnPressed.connect(self.setGroupRectH)

        gbox, lay = customWidgets.groupWidget(
            label='Scale'
        )
        mainLayout.addWidget(gbox)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.scaleXField = customWidgets.DoubleFieldGrp(
            text='',
            minimum=1,
            maximum=999,
            precision=0
        )
        self.scaleXField.setFixedWidth(100)
        self.scaleXField.field.setText('1')
        self.scaleXField.field.returnPressed.connect(self.setScale)
        lay.addWidget(self.scaleXField)

        gbox, lay = customWidgets.groupWidget(
            label='Style',
            layoutType=1
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.shapeStyle = customWidgets.ComboBox()
        self.shapeStyle.addItems(config.itemStyle)
        lay.addWidget(self.shapeStyle)
        editBtn = QPushButton('Edit')
        lay.addWidget(editBtn)
        editBtn.clicked.connect(self.editStyle)

        gbox, lay = customWidgets.groupWidget(
            label='Label'
        )
        mainLayout.addWidget(gbox)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.fontWidget = fontboxWidget.MainClass()
        lay.addWidget(self.fontWidget)
        self.fontWidget.shapeLabel.returnPressed.connect(self.editText)
        self.fontWidget.btn1.clicked.connect(self.capitalizeFirstLetter)

        self.colorPicker = colorPickerWidget.ColorWidget(
            pickerWidget=self.pickerWidget
        )
        mainLayout.addWidget(self.colorPicker)

        # self.installEventFilter(self)

    # def eventFilter(self, object, event):
    #     if event.type() is QEvent.Type.Enter:
    #         self.updateField()
    #     return super(self.__class__, self).eventFilter(object, event)

    def setItemName(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        if isinstance(items, list):
            items = items[-1]
        items.itemName = self.itemNameField.text()
        self.updateScene()

    def setX(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        x = float(self.posXField.getValue())
        for item in items:
            item.setX(x)
        self.posXField.field.selectAll()
        self.updateScene()

    def setY(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        y = float(self.posYField.getValue())
        y *= -1.
        for item in items:
            item.setY(y)
        self.posYField.field.selectAll()
        self.updateScene()

    def setGroupRectW(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        v = float(self.gRectW.getValue())
        for item in items:
            __size = item.groupsRectSize
            item.groupsRectSize = [v, __size[1]]
        self.gRectW.field.selectAll()
        self.updateScene()

    def setGroupRectH(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        v = float(self.gRectH.getValue())
        for item in items:
            __size = item.groupsRectSize
            item.groupsRectSize = [__size[0], v]
        self.gRectH.field.selectAll()
        self.updateScene()

    def editStyle(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        style = self.shapeStyle.currentText()
        for item in items:
            item_type = item.getType()
            if item_type not in ['SimpleShapeItem']:
                continue
            item.editShapeStyle(style=style)
        self.updateScene()

    def setScale(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        scale = int(self.scaleXField.getValue())
        for item in items:
            item.setScale(scale)
            item._scale = float(scale)
            setSelectedFunc = getattr(item, 'setSelectedFunc', None)
            if setSelectedFunc:
                item.setSelectedFunc(value=True)
        self.scaleXField.field.selectAll()
        self.updateScene()

    def editText(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        if isinstance(items, list):
            items = items[0]
        label = self.fontWidget.shapeLabel.text()
        edit_font = self.fontWidget.getFont()
        item_type = items.getType()
        if item_type not in ['SimpleShapeItem']:
            return
        if label is not None:
            items.text = label
        if edit_font:
            items.font = edit_font
        self.fontWidget.shapeLabel.selectAll()
        self.updateScene()

    def capitalizeFirstLetter(self):
        self.fontWidget.capitalizeFirstLetter()
        self.editText()

    def getColor(self):
        color = self.colorPicker.getColor()
        return color

    def updateField(self):
        items = self.pickerWidget.getSelectedItems()
        if items:
            if isinstance(items, list):
                items = items[-1]
            status = items.getStatus()
            self.itemNameField.setText(status.get('itemName', ''))
            self.itemStyleName.setText(status.get('style', ''))
            # Position.
            x = str(round(status.get('x'), 2))
            y = str(round(status.get('y'), 2))
            self.posXField.field.setText(x)
            self.posYField.field.setText(y)

            groupsRectSize = status.get('groupsRectSize', [1.0, 1.0])
            self.gRectW.field.setText(str(groupsRectSize[0]))
            self.gRectH.field.setText(str(groupsRectSize[1]))
            # Scale.
            self.scaleXField.field.setText(
                str(status.get('scale'))
            )

            text = getattr(items, 'text', None)
            if text:
                self.fontWidget.shapeLabel.setText(text)

    def updateScene(self):
        self.pickerWidget.updateView()
