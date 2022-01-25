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


class ColorSliderField(QWidget):
    valueChangedSignal = Signal(str)
    __valueChanged = False

    def __init__(
        self,
        text='',
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignRight)
        self.label = QLabel(text)
        self.label.setFixedWidth(10)
        self.slider = customWidgets.Slider(Qt.Horizontal)
        self.field = customWidgets.SpinBox()
        self.field.setFixedWidth(50)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.field)

        self.slider.valueChanged.connect(self.changedSliderValue)
        self.field.valueChanged.connect(self.changedSpinboxValue)

    def setText(self, text):
        self.label.setText(text)

    def setRange(self, in_value=0, out_value=255):
        self.slider.setRange(in_value, out_value)
        self.field.setRange(in_value, out_value)

    def setValue(self, value):
        self.slider.setValue(value)
        self.field.setValue(value)

    def value(self):
        return self.field.value()

    def changedSliderValue(self, value):
        self.field.setValue(value)

    def changedSpinboxValue(self, value):
        self.slider.setValue(value)
        if self.__valueChanged is False:
            self.__valueChanged = True
            self.valueChangedSignal.emit(value)
        else:
            self.__valueChanged = False


class ColorWidget(QWidget):
    def __init__(
        self,
        pickerWidget=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.pickerWidget = pickerWidget
        baseLayout = QVBoxLayout()
        self.setLayout(baseLayout)

        gbox, lay = customWidgets.groupWidget(label='Coloring')
        baseLayout.addWidget(gbox)

        self.colorDisplay = QPushButton()
        self.colorDisplay.setFixedSize(32, 32)
        lay.addWidget(self.colorDisplay)
        self.colorDisplay.clicked.connect(self.showColorDialogBox)

        data = [
            ('R', 0, 255, 128),
            ('G', 0, 255, 128),
            ('B', 0, 255, 128),
        ]
        self.sliders = []
        for (i, d) in enumerate(data):
            text, in_value, out_value, value = d
            if not text:
                continue
            colorSliderField = ColorSliderField(
                text=text,
                parent=self
            )
            colorSliderField.setRange(
                in_value=in_value,
                out_value=out_value
            )
            colorSliderField.setValue(value)
            lay.addWidget(colorSliderField)
            self.sliders.append(colorSliderField)
            colorSliderField.valueChangedSignal.connect(self.valueChange)

        self.editBtn = QPushButton('Edit Color')
        lay.addWidget(self.editBtn)
        self.editBtn.clicked.connect(self.editColor)

        self.valueChange()

    def editColor(self):
        items = self.pickerWidget.getSelectedItems()
        if not items:
            return
        r, g, b = self.getColor()
        for item in items:
            item.setBrush(QBrush(QColor(r, g, b)))

    def updateDisplayColor(self, color):
        self.colorDisplay.setStyleSheet(
            'QWidget {background-color: %s}' % color.name()
        )

    def setRGBColor(self, color=QColor(0, 0, 0)):
        r, g, b = color.red(), color.green(), color.blue()
        self.setSliderValue([r, g, b])

    def setSliderValue(self, values):
        for i in range(3):
            if self.sliders[i].value() != values[i]:
                self.sliders[i].setValue(values[i])

    def getColor(self):
        values = []
        for i in range(3):
            values.append(self.sliders[i].value())
        return tuple(values)

    def valueChange(self):
        r, g, b = self.getColor()
        color = QColor(r, g, b)
        self.updateDisplayColor(color=color)

    def showColorDialogBox(self):
        colorDialog = QColorDialog()
        r, g, b = self.getColor()
        __color = QColor(r, g, b)
        result = colorDialog.getColor(__color)
        if result.isValid():
            self.setRGBColor(result)
        self.valueChange()
