# -*- coding: utf-8 -*-
import sys
from pprint import pprint

try:
    from importlib import reload
except Exception:
    pass

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


def groupWidget(
    label='Sample Name',
    layoutType=0,
    noBorder=False
):
    groupBox = QGroupBox(label)
    layout = None
    if layoutType == 0:
        layout = QVBoxLayout()
    elif layoutType == 1:
        layout = QHBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)
    # layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    groupBox.setLayout(layout)
    if noBorder:
        groupBox.setStyleSheet('QGroupBox{border: 0px;}')
    return [groupBox, layout]


class DoubleSlider(QSlider):
    def __init__(
        self,
        precision=2,
        minimum=0,
        maximum=1,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.precision = precision
        self.sub = int('1' + '0'.zfill(self.precision))
        if self.precision == 0:
            self.sub = 1
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def value(self):
        value = float(super(self.__class__, self).value()) / self.sub
        if self.precision == 0:
            value = int(value)
        return value

    def setValue(self, value):
        super(self.__class__, self).setValue(int(value))


class DoubleField(QLineEdit):
    def __init__(
        self,
        precision=2,
        minimum=-100000,
        maximum=100000,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.precision = precision
        self.minimum = minimum
        self.maximum = maximum
        self.mag = 10 ** self.precision

    def text(self):
        value = float(super(self.__class__, self).text()) * self.mag
        if self.minimum < value:
            self.minimum = self.minimum
        if value > self.maximum:
            value = self.maximum
        if self.precision == 0:
            value = int(value)
        return str(value)

    def getValue(self):
        value = float(self.text())
        if self.mag != 0:
            value = value / self.mag
        if self.precision == 0:
            value = int(value)
        return str(value)


class DoubleFieldGrp(QWidget):
    def __init__(
        self,
        text='',
        minimum=0,
        maximum=1,
        precision=2
    ):
        super(self.__class__, self).__init__()

        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(1)
        self.mainLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        if text:
            self.label = QLabel(' %s' % text)
            self.label.setAlignment(Qt.AlignRight)
            self.mainLayout.addWidget(self.label)
        self.field = DoubleField(
            precision=precision, minimum=minimum, maximum=maximum
        )
        self.mainLayout.addWidget(self.field)
        value = '0.0'
        if precision == 0:
            value = '0'
        self.field.setText(value)

    def getValue(self):
        return self.field.getValue()


class DoubleSliderFieldGrp(QWidget):
    def __init__(
        self,
        text='',
        defaultValue='0.5',
        precision=2,
        minimum=0,
        maximum=1
    ):
        super(self.__class__, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(1)
        self.mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if text:
            self.label = QLabel(' %s' % text)
            self.label.setFixedWidth(110)
            self.label.setAlignment(Qt.AlignLeft)
            self.mainLayout.addWidget(self.label)
        self.field = DoubleField(
            precision=precision, minimum=minimum, maximum=maximum
        )
        self.mainLayout.addWidget(self.field)
        self.field.returnPressed.connect(self.setTextChange)

        self.slider = DoubleSlider(
            precision=precision, minimum=minimum, maximum=maximum
        )
        self.mainLayout.addWidget(self.slider)
        self.slider.valueChanged.connect(self.setValueChange)
        self.setValueChange()

        self.field.setText(defaultValue)
        self.setTextChange()

    def setTextChange(self):
        value = self.field.text()
        self.slider.setValue(value=value)

    def setValueChange(self):
        value = self.slider.value()
        self.field.setText(str(value))

    def getValue(self):
        return self.field.getValue()


class DoubleSliderFieldButtonGrp(QWidget):
    def __init__(
        self,
        label='',
        text='',
        columnWidth=[],
        defaultValue='0.5',
        precision=2,
        minimum=0,
        maximum=1
    ):
        super(self.__class__, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(1)
        self.mainLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        if label:
            self.label = QLabel(' %s' % label)
            self.label.setAlignment(Qt.AlignRight)
            self.mainLayout.addWidget(self.label)
        self.field = DoubleField(
            precision=precision, minimum=minimum, maximum=maximum
        )
        self.mainLayout.addWidget(self.field)
        self.field.returnPressed.connect(self.setTextChange)

        self.slider = DoubleSlider(
            precision=precision, minimum=minimum, maximum=maximum
        )
        self.mainLayout.addWidget(self.slider)
        self.slider.valueChanged.connect(self.setValueChange)

        self.button = QPushButton(text)
        self.mainLayout.addWidget(self.button)

        if len(columnWidth) == 2:
            self.field.setFixedWidth(columnWidth[0])
            self.button.setFixedWidth(columnWidth[1])

        self.field.setText(defaultValue)
        self.setTextChange()

    def setTextChange(self):
        value = self.field.text()
        self.slider.setValue(value=value)

    def setValueChange(self):
        value = self.slider.value()
        self.field.setText(str(value))

    def getValue(self):
        return self.field.getValue()


class RadioButtonWidget(QWidget):
    def __init__(
        self,
        flags={},
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(1, 1, 1, 1)
        self.mainLayout.setSpacing(1)
        self.mainLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        self.labels = flags.get('labels', [])
        if not self.labels:
            return
        self.buttonGrp = QButtonGroup(self)
        self.radioButtons = []
        for label in self.labels:
            radioButton = QRadioButton(label)
            self.buttonGrp.addButton(radioButton)
            self.mainLayout.addWidget(radioButton)
            self.radioButtons.append(radioButton)
        self.radioButtons[0].setChecked(True)

    def getSelected(self):
        for i, n in enumerate(self.radioButtons):
            if n.isChecked():
                return [i, self.labels[i]]

    def setSelectedFromText(self, text=''):
        for i, n in enumerate(self.labels):
            if n in [text]:
                self.radioButtons[i].setChecked(True)
                return


class ComboBox(QComboBox):
    def __init__(
        self,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        event.ignore()
        # super(self.__class__, self).wheelEvent(event)


class SpinBox(QSpinBox):
    def __init__(
        self,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)

    def wheelEvent(self, event):
        event.ignore()
        # super(self.__class__, self).wheelEvent(event)


class Slider(QSlider):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)

    def wheelEvent(self, event):
        event.ignore()
        # super(self.__class__, self).wheelEvent(event)


class ListWidgetItem(QListWidgetItem):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class ListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def restoreItem(self, names=[]):
        if not names:
            return
        allItems = self.getItems()
        if not allItems:
            return
        for i, item in enumerate(allItems):
            if not item.text() in names:
                continue
            item.setSelected(True)

    def getItemText(self):
        items = self.selectedItems()
        if not items:
            return ''
        return items[0].text()

    def getItemsText(self):
        results = []
        items = self.selectedItems()
        if not items:
            return results
        results = [item.text() for item in items]
        return results

    def getAllItemsText(self):
        count = self.count()
        if not count:
            return []
        return [self.item(i).text() for i in xrange(count)]

    def getItems(self):
        count = self.count()
        if not count:
            return []
        return [self.item(i) for i in xrange(count)]

    def getRowFromText(self, text=''):
        items = self.getItems()
        index = 0
        if not items:
            return index
        for item in items:
            if not text == item.text():
                continue
            index = self.row(item)
            break
        return index
