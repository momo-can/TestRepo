# -*- coding: utf-8 -*-
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

try:
    from importlib import reload
except Exception:
    pass

from customQtLibs import windowUtils
from Picker.Editor import editShapeWidget
from Picker.Editor import editPositionWidget
from Picker.Editor import alignWidget
from Picker.Editor import mirrorPositionWidget
from Picker.Editor import scalePositionWidget
from Picker.Editor import createWidget
from Picker.Editor import functionWidget
reload(windowUtils)
reload(editShapeWidget)
reload(editPositionWidget)
reload(alignWidget)
reload(mirrorPositionWidget)
reload(scalePositionWidget)
reload(createWidget)
reload(functionWidget)

sys.dont_write_bytecode = True


class Widget(QWidget):
    def __init__(
        self,
        tabWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.tabWidget = tabWidget
        #
        # Right contents...
        #
        self.setFixedWidth(350)
        __layout = QVBoxLayout()
        __layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        __layout.setContentsMargins(10, 0, 10, 0)
        __layout.setSpacing(0)
        self.setLayout(__layout)
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        __layout.addWidget(scrollArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        scrollArea.setWidget(widget)

        # Create widgets.
        self.createWid = createWidget.MainClass(tabWidget=self.tabWidget)
        layout.addWidget(self.createWid)

        # Edit shape.
        self.editShapeWid = editShapeWidget.MainClass(
            pickerWidget=self.tabWidget
        )
        layout.addWidget(self.editShapeWid)

        # Edit position tool.
        self.editPosWid = editPositionWidget.MainClass(
            pickerWidget=self.tabWidget)
        layout.addWidget(self.editPosWid)

        # Align tool.
        self.alignWid = alignWidget.MainClass(pickerWidget=self.tabWidget)
        layout.addWidget(self.alignWid)

        # Mirror tool.
        self.mirrroWid = mirrorPositionWidget.MainClass(
            pickerWidget=self.tabWidget)
        layout.addWidget(self.mirrroWid)

        # Scale Position tool.
        self.scaleWid = scalePositionWidget.MainClass(
            pickerWidget=self.tabWidget)
        layout.addWidget(self.scaleWid)

        # Create tool.
        self.funcWid = functionWidget.MainClass()
        layout.addWidget(self.funcWid)

        self.createWid.setEditWidget(widget=self.editShapeWid)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() is QEvent.Type.Enter:
            self.editShapeWid.updateField()
            self.funcWid.updateField()
        return super(self.__class__, self).eventFilter(object, event)

