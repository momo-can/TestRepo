# -*- coding: utf-8 -*-
#
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

from customQtLibs import windowUtils
import customWidgets
from DeadlineSubmitter import baseWidget
from DeadlineSubmitter import windowPrefs
reload(windowUtils)
reload(customWidgets)
reload(baseWidget)
reload(windowPrefs)

sys.dont_write_bytecode = True


class Interface(QMainWindow):
    def __init__(
        self,
        objectName=None,
        windowTitle='Window1',
        department=None,
        parent=None
    ):
        super(self.__class__, self).__init__(parent=parent)
        # Set attributes.
        self.setObjectName(objectName)
        self.setWindowTitle(windowTitle)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setProperty('saveWindowPref', True)
        self.department = department

        self.build()

        self.toolSettings = windowPrefs.getWindowPrefs()

        try:
            geometry = self.toolSettings.value('geometry', '')
            self.restoreGeometry(geometry)
            # v = self.toolSettings.value('Options_Output', '')
            # widget = self.optionWidget.outputList.radioButtons
            # widget[int(v)].setChecked(True)
            # v = self.toolSettings.value('Display', '')
            # self.optionWidget.displayGroup.setChecked(v)
        except Exception as e:
            print(e.message)
            print(e.args)

    def saveWindowPreference(self):
        geometry = self.saveGeometry()
        self.toolSettings.setValue('geometry', geometry)
        # # Output "Options: Output"
        # widget = self.optionWidget.outputList.radioButtons
        # v = None
        # for i, w in enumerate(widget):
        #     if w.isChecked():
        #         v = i
        #         break
        # self.toolSettings.setValue('Options_Output', v)
        # # GroupBox "Display"
        # widget = self.optionWidget.displayGroup
        # v = widget.isChecked()
        # self.toolSettings.setValue('Display', v)

    def closeEvent(self, event):
        self.saveWindowPreference()
        self.removeEventFilter(self)
        super(self.__class__, self).closeEvent(event)

    def build(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(1, 1, 1, 1)
        self.mainLayout.setSpacing(1)
        self.mainLayout.setAlignment(Qt.AlignTop)
        centralWidget.setLayout(self.mainLayout)

        widget = baseWidget.Widget(department=self.department)
        self.mainLayout.addWidget(widget)
        # gLayout.addWidget(self.cameraListWidget)

        css = '''
                QGroupBox {
                    padding: 10px 1px 1px 1px;
                    border: 1px solid #ccc;
                }

                QWidget {
                    font-size: 10pt;
                }
            '''
        self.setStyleSheet(css)
        # self.installEventFilter(self)

    # def eventFilter(self, object, event):
    #     if event.type() == QEvent.Type.WindowDeactivate:
    #         self.cameraListWidget.setCamera()
    #     elif event.type() == QEvent.Type.WindowActivate:
    #         self.cameraListWidget.setCamera()
    #     return super(self.__class__, self).eventFilter(object, event)


def main(filters='', department=''):
    windowName = 'deadlineSubmitterWindow'
    windowUtils.deleteWidget(objectName=windowName)
    parentWidget = windowUtils.getToplevelWidget(filters=filters)
    window = Interface(
        objectName=windowName,
        windowTitle='Deadline Submitter - {}'.format(department),
        department=department,
        parent=parentWidget
    )
    window.show()
