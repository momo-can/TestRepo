# -*- coding: utf-8 -*-
import sys
import os
import imp
import re

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

from customQtLibs import windowUtils
from DeadlineSubmitter import customWidgets
reload(windowUtils)
reload(customWidgets)

sys.dont_write_bytecode = True


def importMod(name=''):
    dirname = os.path.dirname(__file__)
    dirname = dirname.replace(os.sep, '/')
    __name = '.'.join([name, 'py'])
    __plugin = '/'.join([
        dirname,
        __name
    ])
    plugin = imp.load_source(
        'mod_{}'.format(name),
        __plugin
    )
    print('> Module')
    print(dirname)
    print(name)
    print('')
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
        self.fileParams = {}
        self.interfaceFnc = importMod(
            name='interfaceFunction'
        )
        self.getFileParameters()

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

        group, gLayout = customWidgets.groupWidget(
            label='Job Description'
        )
        group.setFlat(True)
        gLayout.setContentsMargins(1, 10, 1, 10)
        gLayout.setSpacing(0)
        mainLayout.addWidget(group)

        group, _gLayout = customWidgets.groupWidget(
            label='Job Name',
            layoutType=1,
            noBorder=True
        )
        gLayout.addWidget(group)

        self.jobName = QLineEdit()
        _gLayout.addWidget(self.jobName)
        text = self.fileParams.get('filename', '')
        self.jobName.setText(text)

        button = QPushButton('<')
        _gLayout.addWidget(button)
        button.clicked.connect(self.setFileName)

        group, _gLayout = customWidgets.groupWidget(
            label='Comment',
            noBorder=True
        )
        gLayout.addWidget(group)

        self.comment = QLineEdit()
        _gLayout.addWidget(self.comment)
        self.comment.setText('')

        group, _gLayout = customWidgets.groupWidget(
            label='Department',
            noBorder=True
        )
        gLayout.addWidget(group)

        self.departmentField = QLineEdit()
        _gLayout.addWidget(self.departmentField)
        self.departmentField.setText(self.department)

        group, _gLayout = customWidgets.groupWidget(
            label='User Name',
            noBorder=True
        )
        gLayout.addWidget(group)

        self.username = QLineEdit()
        _gLayout.addWidget(self.username)
        self.username.setText(self.interfaceFnc.getUsername())

    def setFileName(self):
        self.getFileParameters()
        self.jobName.setText(
            self.fileParams.get('filename', '')
        )

    def getFileParameters(self):
        self.fileParams = self.interfaceFnc.getFileParameters()

    def getJobParameters(self):
        return {
            'jobName': self.jobName.text(),
            'comment': self.comment.text(),
            'department': self.departmentField.text(),
            'username': self.username.text()
        }
