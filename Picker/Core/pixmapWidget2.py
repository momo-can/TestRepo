# -*- coding: utf-8 -*-
import os
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class SimpleImgItem(QGraphicsPixmapItem):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

        self.item_image = None
        self.image_path = ''
        self._locked = False
        self.object_type = None

    def setImage(self, path=''):
        self.image_path = path.replace(os.sep, '/')
        self.item_image = QPixmap(self.image_path)
        self.setPixmap(self.item_image)

        x, y = self.getImageSize()
        offset_x = x / 2. * -1.
        offset_y = y / 2. * -1.
        self.setOffset(offset_x, offset_y)

    def getImageSize(self):
        if not self.item_image:
            tmp = QSize()
            tmp.setWidth(10)
            tmp.setHeight(10)
            return (tmp.width(), tmp.height())
        return (
            self.item_image.width(),
            self.item_image.height()
        )

    def getType(self):
        return 'ImageItem'

    def select_item(self, namespace='', value=False, select_type=''):
        pass

    def editShapeStyle(self, style=''):
        pass

    def getStatus(self):
        imagename = os.path.basename(self.image_path)
        return {
            'x': self.x(),
            'y': self.y(),
            'shapeType': self.getType(),
            'scale': self.scale(),
            'locked': self._locked,
            'image_path': imagename.encode('shift_jis')
        }
