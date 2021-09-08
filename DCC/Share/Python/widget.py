# -*- coding: utf-8 -*-
import sys
import os
import re
import glob

import platform

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


def groupWidget(
    label='Sample Name',
    layoutType=0
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
    return [groupBox, layout]


def msgBox(
    title='Infomation',
    message='Are you sure you want to run it?'
):
    qm = QMessageBox
    res = qm.question(
        None,
        title,
        message,
        qm.Ok | qm.Cancel
    )

    result = True
    if res != qm.Ok:
        result = False
    return result


class IntField(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignRight)
        self.returnPressed.connect(lambda: self.setText(self.text()))

    def text(self):
        text = super(self.__class__, self).text()

        try:
            text = float(text)
        except Exception as e:
            print(e.message)
            print(e.args)
            text = 1

        text = int(text)
        if text == 0:
            text = 1
        return text

    def setText(self, *args):
        super(self.__class__, self).setText(str(args[0]))


class ListWidgetItem(QListWidgetItem):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)


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

    def getAllItems(self):
        count = self.count()
        if not count:
            return []
        return [self.item(i) for i in range(count)]

    def getAllItemsText(self):
        count = self.count()
        if not count:
            return []
        return [self.item(i).text() for i in range(count)]

    def getItem(self):
        item = self.selectedItems()
        if not item:
            return []
        return item[0]

    def getItems(self):
        items = self.selectedItems()
        if not items:
            return []
        return items

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


class ComboDelegate(QItemDelegate):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.list = []
        self.platformSystem = platform.system()

    def createEditor(self, parent, option, index):
        row = index.row()
        column = index.column()
        items = self.tableModel.items[row]
        columnCount = self.tableModel.columnCount() - 1
        self.assetType = items[0]
        if self.assetType == 'CAM':
            return None

        referencePath = items[columnCount]
        names = referencePath.split('/')
        temps = []
        __index = 7
        if self.platformSystem in ['Darwin', 'Linux']:
            __index = 8
            if re.search('/Volumes/M', referencePath):
                __index = 9

        for i, n in enumerate(names):
            if i == __index:
                break
            temps.append(n)

        temps = '/'.join(temps)
        files = glob.glob('{}/*'.format(temps))
        lodList = []
        for f in files:
            __name = os.path.basename(f)
            if __name in self.tableModel.hidden:
                continue
            lodList.append(__name)
        lodList.sort()
        lodList.reverse()

        editLOD = items[4]
        if column == 4:
            self.list = lodList
        self.editor = QComboBox(parent)
        self.editor.addItems(self.list)
        self.editor.setCurrentText(editLOD)
        self.editor.currentIndexChanged.connect(self.currentIndexChanged)
        return self.editor

    def setModelData(self, combo, model, index):
        if self.assetType == 'CAM':
            return
        comboIndex = combo.currentIndex()
        text = self.list[comboIndex]
        model.setData(index, text)

    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class TableModel(QAbstractItemModel):
    def __init__(
        self,
        userTemplate='',
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.userTemplate = userTemplate
        self.interfaceConfig = self.userTemplate.get('interface', {})
        self.hidden = self.interfaceConfig.get('hidden', [])
        self.headers = self.interfaceConfig.get('assetHeader', [])
        self.items = []

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, None)

    def parent(self, child):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == Qt.DisplayRole:
            try:
                return self.items[index.row()][index.column()]
            except Exception:
                return

        if not index.isValid():
            return False
        if row > len(self.items):
            return False
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.items[row]
        return

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            column = index.column()
            selection = self.selectionModel.selectedRows()
            for s in selection:
                if self.items[s.row()][0] == 'CAM':
                    continue
                oldValue = self.items[s.row()][column]
                referencePath = self.items[s.row()][-1]
                newPath = referencePath.replace(oldValue, value)
                if not os.path.isfile(newPath):
                    continue
                self.items[s.row()][column] = value
                self.items[s.row()][-1] = newPath
                self.dataChanged.emit(s, s)
            return True
        return False

    def headerData(self, id, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return self.headers[id]

        if orientation == Qt.Vertical:
            return id

    def flags(self, index):
        column = index.column()
        fl = Qt.NoItemFlags
        if index.isValid():
            fl |= Qt.ItemIsEnabled | Qt.ItemIsSelectable
            if column == 4:
                fl |= Qt.ItemIsEditable
        return fl
        # if column != 3:
        #     return Qt.ItemIsSelectable
        # return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def getData(self):
        row = self.rowCount()
        column = self.columnCount()
        rowData = []
        for r in range(row):
            columnData = {}
            for c in range(column):
                columnData[self.headers[c]] = self.data(self.index(r, c))
            rowData.append(columnData)
        return rowData


class TableView(QTableView):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # pprint(dir(self.horizontalHeader()))
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.verticalHeader().setVisible(False)

    def updateData(self):
        model = self.model()
        model.beginResetModel()
        model.endResetModel()

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Return:
    #         selectedRows = self.selectionModel().selectedRows()
    #         if selectedRows:
    #             # selectedIndex = selectedRows[0]
    #             # editableIndex = self._firstEditableIndex(selectedIndex)
    #             # self.setCurrentIndex(editableIndex)
    #             # self.edit(editableIndex)
    #             print(selectedRows)
    #     else:
    #         QTableView.keyPressEvent(self, event)
