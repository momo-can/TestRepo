# -*- coding: utf-8 -*-
import tempfile
import sys
import os

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class OverrideCheckDialogBox(QDialog):
    def __init__(self, text='', parent=None, *args, **kwargs):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle('Warning')
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        label = QLabel('File exists...Overwrite it ? "{0}"'.format(text))
        layout.addWidget(label)
        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        layout.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)


class ScreenGrabber(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(self.__class__, self).__init__(parent=parent, *args, **kwargs)

        self._cancel = False
        self._opacity = 1
        self._click_pos = None
        self._capture_rect = QRect()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.CustomizeWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

        desktop = QApplication.desktop()
        desktop.resized.connect(self._fitScreenGeometry)
        desktop.screenCountChanged.connect(self._fitScreenGeometry)

    @property
    def captureRect(self):
        return self._capture_rect

    def paintEvent(self, event):
        # Convert click and current mouse positions to local space.
        mouse_pos = self.mapFromGlobal(QCursor.pos())
        click_pos = None
        if self._click_pos is not None:
            click_pos = self.mapFromGlobal(self._click_pos)

        painter = QPainter(self)

        # Draw background. Aside from aesthetics, this makes the full
        # tool region accept mouse events.
        painter.setBrush(
            QColor(
                0,
                0,
                0,
                self._opacity
            )
        )
        painter.setPen(Qt.NoPen)
        painter.drawRect(event.rect())

        # Clear the capture area
        if click_pos is not None:
            capture_rect = QRect(
                click_pos,
                mouse_pos
            )
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawRect(capture_rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        pen = QPen(
            QColor(
                255,
                255,
                255,
                100
            ),
            1,
            # Qt.DashDotDotLine
        )
        painter.setPen(pen)

        # Draw cropping markers at click position
        if click_pos is not None:
            painter.drawLine(
                event.rect().left(),
                click_pos.y(),
                event.rect().right(),
                click_pos.y()
            )
            painter.drawLine(
                click_pos.x(),
                event.rect().top(),
                click_pos.x(),
                event.rect().bottom()
            )

        # Draw cropping markers at current mouse position
        painter.drawLine(
            event.rect().left(),
            mouse_pos.y(),
            event.rect().right(),
            mouse_pos.y()
        )
        painter.drawLine(
            mouse_pos.x(),
            event.rect().top(),
            mouse_pos.x(),
            event.rect().bottom()
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            print('Cancel')
        super(self.__class__, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        # modifier = QApplication.keyboardModifiers()
        if event.button() == Qt.LeftButton:
            self._click_pos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self._cancel = True
            self.close()
        super(self.__class__, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.repaint()
        super(self.__class__, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and \
                self._click_pos is not None:
            self._capture_rect = QRect(
                self._click_pos,
                event.globalPos()
            ).normalized()
            self._click_pos = None
        self.close()
        super(self.__class__, self).mouseReleaseEvent(event)

    def showEvent(self, event):
        self._fitScreenGeometry()
        fade_anim = QPropertyAnimation(
            self,
            "_opacity_anim_prop",
            self
        )
        fade_anim.setStartValue(self._opacity)
        fade_anim.setEndValue(150)
        fade_anim.setDuration(1)
        fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        fade_anim.start(QAbstractAnimation.DeleteWhenStopped)

    def _setOpacity(self, value):
        self._opacity = value
        self.repaint()

    def _getOpacity(self):
        return self._opacity

    _opacity_anim_prop = Property(int, _getOpacity, _setOpacity)

    def _fitScreenGeometry(self):
        desktop = QApplication.desktop()
        workspace_rect = QRect()
        for i in range(desktop.screenCount()):
            workspace_rect = workspace_rect.united(desktop.screenGeometry(i))
        self.setGeometry(workspace_rect)

    @classmethod
    def capture(cls):
        tool = ScreenGrabber()
        tool.exec_()
        if tool._cancel:
            return None
        return getDesktopPixmap(tool.captureRect)


def getDesktopPixmap(rect):
    desktop = QApplication.desktop()
    return QPixmap.grabWindow(
        desktop.winId(),
        rect.x(),
        rect.y(),
        rect.width(),
        rect.height()
    )


def screenCapture(workpath=None):
    screen_capture = ScreenGrabber.capture
    pixmap = screen_capture()
    if not pixmap:
        return None
    if workpath is None:
        workpath = tempfile.NamedTemporaryFile(
            suffix=".png",
            prefix="screencapture_",
            delete=False
        ).name
    else:
        dialog = QInputDialog()
        filename, res = dialog.getText(
            None,
            'Infomation',
            'Input your screenshot name.'
        )
        if res:
            workpath = '/'.join([
                workpath.replace(os.sep, '/'),
                '{0}.png'.format(filename)
            ])
        if os.path.isfile(workpath):
            dialog = OverrideCheckDialogBox(
                text='{0}.png'.format(filename)
            )
            if dialog.exec_() != QDialog.Accepted:
                return
    pixmap.save(workpath)
    # Dev
    return workpath


# screen_capture_file()
