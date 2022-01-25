# -*- coding: utf-8 -*-
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class GraphicsItem(QGraphicsItem):
    def __init__(
        self,
        style='box',
        scale=1.,
        text='Sample',
        font=None,
        itemName='',
        *args,
        **kwargs
    ):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable
        )

        self.style = style
        self.text = text
        self.font = font
        self.itemName = itemName
        # self.function_data = ''
        self.pickItemData = ''
        self.pickItemShowHide = {}
        self.pickItemType = 'Select'
        self.setScale(int(scale))
        self.defaultRect = QRectF(
            -0.5,
            -0.5,
            1.0,
            1.0
        )
        self.rect = self.defaultRect
        self._brush = QBrush(Qt.lightGray)
        self._locked = False
        self._offset_x = 0.0
        self._offset_y = 0.0
        self.view_text = False
        self.groupsRectSize = [1, 1]

        self._pen = QPen(
            QColor(.0, .0, .0), .0
        )
        self.pen_user = QPen(
            QColor(.0, .0, .0), .0
        )
        self.pen_selected = QPen(
            QColor(255, 255, 255),
            0.5,
            Qt.DashLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )

    def boundingRect(self):
        return self.rect

    def setBrush(self, brush):
        self._brush = brush
        self.update()

    def setPen(self, pen):
        self._pen = pen
        self.update()

    def paint(self, painter, option, widget):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        __font = QFont('Noto Mono')
        __font.setPointSize(1)
        __font.setWeight(5)
        __font.setWordSpacing(0)
        painter.setFont(__font)
        fontMetrics = QFontMetrics(__font)
        fontWidth = fontMetrics.width(self.text)
        fontHeight = fontMetrics.height()

        textOpt = QTextOption()
        textOpt.setAlignment(Qt.AlignCenter)
        textOpt.setFlags(QTextOption.IncludeTrailingSpaces)
        textOpt.setWrapMode(QTextOption.NoWrap)

        if self.style == 'Square':
            drawData = QRectF(
                -1.0 / 2,
                -1.0 / 2,
                1.0,
                1.0
            )
            painter.drawRect(drawData)
            self.rect = drawData
        elif self.style == 'Rectangle':
            drawData = QRectF(
                -0.5,
                -0.35,
                1.0,
                0.35
            )
            painter.drawRect(drawData)
            self.rect = drawData
        elif self.style == 'Circle':
            drawData = QRectF(
                -0.5,
                -0.5,
                1.0,
                1.0
            )
            painter.drawEllipse(drawData)
            self.rect = drawData
        elif self.style == 'Triangle':
            drawData = QPolygonF()
            drawData.append(QPointF(-0.5, 0.5))
            drawData.append(QPointF(.0, -0.5))
            drawData.append(QPointF(0.5, 0.5))
            drawData.append(QPointF(-0.5, 0.5))
            painter.drawPolygon(drawData)
            self.rect = drawData.boundingRect()
        elif self.style == 'Cross':
            drawData = QPolygonF()
            drawData.append(QPointF(-0.13, -0.5))
            drawData.append(QPointF(0.13, -0.5))
            drawData.append(QPointF(0.13, -0.13))
            drawData.append(QPointF(0.5, -0.13))
            drawData.append(QPointF(0.5, 0.13))
            drawData.append(QPointF(0.13, 0.13))
            drawData.append(QPointF(0.13, 0.5))
            drawData.append(QPointF(-0.13, 0.5))
            drawData.append(QPointF(-0.13, 0.13))
            drawData.append(QPointF(-0.5, 0.13))
            drawData.append(QPointF(-0.5, -0.13))
            drawData.append(QPointF(-0.13, -0.13))
            painter.drawPolygon(drawData)
            self.rect = drawData.boundingRect()
        elif self.style == 'Groups':
            __brushColor = self._brush.color()
            r = __brushColor.redF()
            g = __brushColor.greenF()
            b = __brushColor.blueF()
            c = QColor()
            c.setRedF(r)
            c.setGreenF(g)
            c.setBlueF(b)
            c.setAlphaF(0.1)
            self._brush = QBrush(c)
            painter.setBrush(self._brush)
            w = self.groupsRectSize[0]
            h = self.groupsRectSize[1]
            __template = [
                [-0.5, -0.5],
                [0.5, -0.5],
                [0.5, 0.5],
                [-0.5, 0.5]
            ]
            drawData = QPolygonF()
            for t in __template:
                drawData.append(
                    QPointF(
                        t[0] * w,
                        t[1] * h
                    )
                )
            painter.drawPolygon(drawData)
            __size = self.groupsRectSize
            __size = [abs(s) for s in __size]
            # print(__size)
            self.rect = drawData.boundingRect()
            self.setZValue(0)

        if self.view_text:
            painter.setPen(QColor(255, 255, 255))
            # painter.drawText(
            #     QRectF(
            #         fontWidth / 2.0,
            #         -(self.rect.y() + fontHeight),
            #         -fontWidth,
            #         fontHeight
            #     ),
            #     self.text,
            #     textOpt
            # )
            left = self.rect.width()
            top = -fontHeight * 0.85
            width = fontWidth
            height = fontHeight
            if self.style == 'Groups':
                left = -self.groupsRectSize[0] / 2
                top = -self.groupsRectSize[1] / 2
            painter.drawText(
                QRectF(left, top, width, height),
                self.text,
                textOpt
            )

    def editShapeStyle(self, style=''):
        self.style = style

    def getType(self):
        return 'SimpleShapeItem'

    def getStatus(self):
        __color = self._brush.color().toTuple()
        font = 'Tahoma,1,0,0,0,0,0,0,0,0'
        try:
            font = self.font.toString()
        except Exception:
            pass
        return {
            'x': self.x(),
            'y': self.y() * -1.0,
            'text': self.text.encode('shift_jis'),
            'font': font.encode('shift_jis'),
            'shapeType': self.getType(),
            # 'rect': self.rect,
            'color': list(__color),
            'scale': int(self.scale()),
            'style': self.style.encode('shift_jis'),
            'locked': self._locked,
            'pickItemType': self.pickItemType,
            'pickItemData': self.pickItemData.encode('shift_jis'),
            'pickItemShowHide': self.pickItemShowHide,
            'view_text': self.view_text,
            'itemName': self.itemName,
            'groupsRectSize': self.groupsRectSize
        }

    def setSelectedFunc(self, value=False):
        self.pen_user = QPen(
            QColor(.0, .0, .0), .0
        )
        line_size = 1.0 / float(self.scale())
        self.pen_selected = QPen(
            QColor(255, 255, 255),
            line_size,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )

        self.setPen(pen=self.pen_user)
        self.setSelected(False)
        if value:
            self.setPen(pen=self.pen_selected)
            self.setSelected(True)
        self.update()
