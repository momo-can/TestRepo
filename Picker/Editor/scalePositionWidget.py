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


def scalePosition(
    tgt_pos=[.0, .0],
    scale_pos=[.0, .0],
    scale_value=[1., 1.]
):
    offset_pos = [tgt_pos[0] - scale_pos[0], tgt_pos[1] - scale_pos[1]]
    if offset_pos == [0.0, 0.0]:
        return tgt_pos

    matA = [
        1, 0, 0,
        0, 1, 0,
        offset_pos[0], offset_pos[1], 1
    ]

    matB = [
        scale_value[0], 0, 0,
        0, scale_value[1], 0,
        scale_pos[0], scale_pos[1], 1
    ]

    res = [
        [
            matA[0] * matB[0] + matA[1] * matB[3] + matA[2] * matB[6],
            matA[0] * matB[1] + matA[1] * matB[4] + matA[2] * matB[7],
            matA[0] * matB[2] + matA[1] * matB[5] + matA[2] * matB[8]
        ],

        [
            matA[3] * matB[0] + matA[4] * matB[3] + matA[5] * matB[6],
            matA[3] * matB[1] + matA[4] * matB[4] + matA[5] * matB[7],
            matA[3] * matB[2] + matA[4] * matB[5] + matA[5] * matB[8]
        ],

        [
            matA[6] * matB[0] + matA[7] * matB[3] + matA[8] * matB[6],
            matA[6] * matB[1] + matA[7] * matB[4] + matA[8] * matB[7],
            matA[6] * matB[2] + matA[7] * matB[5] + matA[8] * matB[8]
        ]
    ]

    return [res[2][0], res[2][1]]


class MainClass(QGroupBox):
    def __init__(
        self,
        pickerWidget=None,
        parent=None,
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.pickerWidget = pickerWidget

        self.setTitle('Scale Position')

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        numGrp = QButtonGroup(self)
        self.scalePositionPivot = []
        labels = [u'┌', u'─', u'┐', u'│', u'+', u'│', u'└', u'─', u'┘']
        label_index = 0
        for r in range(0, 3):
            __layout = QHBoxLayout()
            mainLayout.addLayout(__layout)
            for c in range(0, 3):
                radioBtn = QRadioButton(labels[label_index])
                radioBtn.setObjectName('scapePosition_{0}'.format(label_index))
                self.scalePositionPivot.append(radioBtn)
                numGrp.addButton(radioBtn)
                __layout.addWidget(radioBtn)
                label_index += 1
        self.scalePositionPivot[4].setChecked(True)

        layout = QHBoxLayout()
        mainLayout.addLayout(layout)
        self.valueField = customWidgets.DoubleFieldGrp(
            text='Scale Value ',
            minimum=1,
            maximum=999,
            precision=0
        )
        self.valueField.field.setText('1')
        layout.addWidget(self.valueField)
        scalePositionButton = QPushButton('Apply')
        layout.addWidget(scalePositionButton)
        scalePositionButton.clicked.connect(self.scalePosition)

    def scalePosition(self):
        scale_pos_flag = 0
        for i, rb in enumerate(self.scalePositionPivot):
            if rb.isChecked():
                scale_pos_flag = i
        if not self.pickerWidget:
            return

        items = self.pickerWidget.getSelectedItems()
        if not items:
            return

        pos_x = []
        pos_y = []
        for item in items:
            x = item.x()
            y = item.y()
            pos_x.append(x)
            pos_y.append(y)
        pos_x.sort()
        pos_y.sort()

        half_x = .0
        for v in pos_x:
            half_x += v
        half_x = half_x / len(pos_x)

        half_y = .0
        for v in pos_y:
            half_y += v
        half_y = half_y / len(pos_y)

        bounding_box = [
            [pos_x[0], pos_y[0]],
            [half_x, pos_y[0]],
            [pos_x[-1], pos_y[0]],

            [pos_x[0], half_y],
            [half_x, half_y],
            [pos_x[-1], half_y],

            [pos_x[0], pos_y[-1]],
            [half_x, pos_y[-1]],
            [pos_x[-1], pos_y[-1]]
        ]

        x, y = bounding_box[scale_pos_flag]

        scale_value = int(self.valueField.getValue())
        scale_value = [scale_value, scale_value]
        for item in items:
            item_x = item.x()
            item_y = item.y()

            tgt_pos = [item_x, item_y]
            scale_pos = [x, y]
            scale_x, scale_y = scalePosition(
                tgt_pos=tgt_pos,
                scale_pos=scale_pos,
                scale_value=scale_value
            )
            item.setX(scale_x)
            item.setY(scale_y)
