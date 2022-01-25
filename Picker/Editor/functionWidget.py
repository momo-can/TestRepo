# -*- coding: utf-8 -*-
import sys
import json
import ast

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
reload(customWidgets)
reload(config)

sys.dont_write_bytecode = True


class Highlighter(QSyntaxHighlighter):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)

        charFormat = QTextCharFormat()
        __color = QColor('#f9e79f')
        charFormat.setForeground(__color)
        charFormat.setFontWeight(QFont.Bold)

        __patterns = ['exec', 'print']
        self.highlightingRules = [
            (QRegExp(r'\b%s\b' % ptn), charFormat) for ptn in __patterns
        ]

        charFormat = QTextCharFormat()
        __color = QColor('#ec7063')
        charFormat.setForeground(__color)
        charFormat.setFontWeight(QFont.Bold)

        __patterns = [
            'break', 'assert', 'continue',
            'del', 'elif', 'else', 'except', 'finally',
            'for', 'from', 'if', 'import',
            'pass',
            'raise', 'return', 'try', 'while', 'yield',
        ]

        self.highlightingRules += [
            (QRegExp(r'\b%s\b' % ptn), charFormat) for ptn in __patterns
        ]

        charFormat = QTextCharFormat()
        __color = QColor('#3498db')
        charFormat.setForeground(__color)
        charFormat.setFontWeight(QFont.Bold)

        __patterns = [
            'and', 'class', 'def',
            'None', 'True', 'False',
        ]

        self.highlightingRules += [
            (QRegExp(r'\b%s\b' % ptn), charFormat) for ptn in __patterns
        ]

        classFormat = QTextCharFormat()
        __color = QColor('red')
        classFormat.setForeground(__color)
        classFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append(
            (QRegExp('\\bQ[A-Za-z]+\\b'), classFormat)
        )

        singleLineCommentFormat = QTextCharFormat()
        __color = QColor('#138d75')
        singleLineCommentFormat.setForeground(__color)
        self.highlightingRules.append(
            (QRegExp('//[^\n]*'), singleLineCommentFormat)
        )
        self.highlightingRules.append(
            (QRegExp('#[^\n]*'), singleLineCommentFormat)
        )

        self.multiLineCommentFormat = QTextCharFormat()
        __color = QColor('#138d75')
        self.multiLineCommentFormat.setForeground(__color)

        quotationFormat = QTextCharFormat()
        __color = QColor('#dc7633')
        quotationFormat.setForeground(__color)
        self.highlightingRules.append(
            (QRegExp('\".*\"'), quotationFormat)
        )
        self.highlightingRules.append(
            (QRegExp('\'.*\''), quotationFormat)
        )

        functionFormat = QTextCharFormat()
        __color = QColor('#48c9b0')
        functionFormat.setForeground(__color)
        functionFormat.setFontItalic(True)
        self.highlightingRules.append(
            (QRegExp('\\b[A-Za-z0-9_]+(?=\\()'), functionFormat)
        )

        self.commentStartExpression = QRegExp('/\\*')
        self.commentEndExpression = QRegExp('\\*/')

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + \
                    self.commentEndExpression.matchedLength()

            self.setFormat(
                startIndex,
                commentLength,
                self.multiLineCommentFormat
            )
            startIndex = self.commentStartExpression.indexIn(
                text,
                startIndex + commentLength
            )


class PickItemDataField(QGroupBox):
    def __init__(
        self,
        itemTypeWidget=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.tab = None
        self.itemTypeWidget = itemTypeWidget

        self.setTitle('Item Data')

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        mainLayout.setContentsMargins(3, 3, 3, 3)
        mainLayout.setSpacing(10)

        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QTextEdit()
        self.editor.setFont(font)
        self.editor.setFixedHeight(200)

        self.highlighter = Highlighter(self.editor.document())

        self.editor.setTabStopWidth(12)
        self.editor.setFontPointSize(10)
        mainLayout.addWidget(self.editor)

        self.updateBtn = QPushButton('Update')
        self.updateBtn.clicked.connect(self.updatePickItemData)
        mainLayout.addWidget(self.updateBtn)

    def updatePickItemData(self):
        self.setData()
        self.changeStatus()

    def setData(self):
        items = self.tab.getSelectedItems()
        if not items:
            return
        text = self.editor.toPlainText()
        itemType = self.itemTypeWidget.getSelected()
        for i, item in enumerate(items):
            item.pickItemData = text
            item.pickItemType = itemType[1]
        self.changeStatus()

    def changeStatus(self):
        if not self.tab:
            return
        items = self.tab.getSelectedItems()
        if not items:
            return
        pickItemData = getattr(items[-1], 'pickItemData', None)
        pickItemType = getattr(items[-1], 'pickItemType', 0)
        self.itemTypeWidget.setSelectedFromText(text=pickItemType)
        if pickItemData:
            self.editor.setText(pickItemData)
        else:
            self.editor.setText('')


class ShowHideField(QGroupBox):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.tab = None

        self.setTitle('Show/Hide')

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        mainLayout.setContentsMargins(3, 3, 3, 3)
        mainLayout.setSpacing(10)

        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QTextEdit()
        self.editor.setFont(font)
        self.editor.setFixedHeight(200)

        self.highlighter = Highlighter(self.editor.document())

        self.editor.setTabStopWidth(12)
        self.editor.setFontPointSize(10)
        mainLayout.addWidget(self.editor)

        btn = QPushButton('Update')
        mainLayout.addWidget(btn)
        btn.clicked.connect(self.setData)

    def setData(self):
        items = self.tab.getSelectedItems()
        if not items:
            return
        text = self.editor.toPlainText()
        s = ast.literal_eval(text)
        for i, item in enumerate(items):
            item.pickItemShowHide = s
        self.changeStatus()

    def changeStatus(self):
        if not self.tab:
            return
        items = self.tab.getSelectedItems()
        if not items:
            return
        pickItemShowHide = getattr(items[-1], 'pickItemShowHide', {})
        __text = json.dumps(pickItemShowHide)
        if pickItemShowHide:
            self.editor.setText(__text)
        else:
            self.editor.setText('')


class MainClass(QWidget):
    def __init__(
        self,
        pickerWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.tab = None
        self.pickerWidget = pickerWidget

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setContentsMargins(2, 0, 2, 0)
        mainLayout.setSpacing(0)

        gbox, glay = customWidgets.groupWidget(label='Gimmick')
        glay.setContentsMargins(2, 0, 2, 0)
        glay.setSpacing(0)
        mainLayout.addWidget(gbox)

        __flags = {'labels': config.gimmick}
        self.itemTypeWidget = customWidgets.RadioButtonWidget(flags=__flags)
        glay.addWidget(self.itemTypeWidget)

        self.pickItemDataField = PickItemDataField(
            itemTypeWidget=self.itemTypeWidget
        )
        glay.addWidget(self.pickItemDataField)

        self.showHideField = ShowHideField()
        glay.addWidget(self.showHideField)

        self.clickFunction()

    def setTab(self, widget=None):
        self.pickItemDataField.tab = widget
        self.showHideField.tab = widget

    def getField(self):
        return [self.pickItemDataField]

    def clickFunction(self):
        self.updateField()

    def updateField(self):
        self.pickItemDataField.changeStatus()
        self.showHideField.changeStatus()
