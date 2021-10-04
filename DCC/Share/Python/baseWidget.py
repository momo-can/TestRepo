# -*- coding: utf-8 -*-
import sys
import os
import imp

from pprint import pprint

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

from customQtLibs import windowUtils
import customWidgets
import windowPrefs
reload(windowUtils)
reload(customWidgets)
reload(windowPrefs)

sys.dont_write_bytecode = True


def importInterface(department='', name=''):
    dirs = [department, 'Common']
    importPath = None
    for d in dirs:
        dirname = os.path.dirname(__file__)
        pluginPath = '/'.join([
            dirname,
            'Interface',
            d
        ])
        __name = '.'.join([name, 'py'])
        importPath = '/'.join([
            pluginPath,
            __name
        ])
        if not os.path.isfile(importPath):
            continue
        print('> Found: {}'.format(d))
        break

    if not importPath:
        return None

    plugin = imp.load_source(
        'mod_{}'.format(name),
        importPath
    )
    print('> Template Module: {}'.format(name))
    return plugin


class Widget(QWidget):
    def __init__(
        self,
        department='',
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent)
        self.department = department

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

        m = importInterface(
            department=self.department,
            name='jobDescriptionWidget'
        )
        if m:
            self.jobDescripiton = m.Widget(department=self.department)
            mainLayout.addWidget(self.jobDescripiton)

        m = importInterface(
            department=self.department,
            name='jobSchedulingWidget'
        )
        if m:
            self.jobScheduling = m.Widget(department=self.department)
            mainLayout.addWidget(self.jobScheduling)

        m = importInterface(
            department=self.department,
            name='renderOptionsWidget'
        )
        if m:
            self.renderOptions = m.Widget(department=self.department)
            mainLayout.addWidget(self.renderOptions)

        m = importInterface(
            department=self.department,
            name='submitWidget'
        )
        if m:
            self.submitWidget = m.Widget(department=self.department)
            mainLayout.addWidget(self.submitWidget)
            self.submitWidget.submitButton.clicked.connect(
                self.submit
            )

    def submit(self):
        params = {}
        params.update(self.jobScheduling.getJobParameters())
        params.update(self.renderOptions.getJobParameters())
        params.update(self.jobDescripiton.getJobParameters())
        self.submitWidget.submit(params=params)
