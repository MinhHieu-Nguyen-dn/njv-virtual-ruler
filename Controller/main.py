from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QInputDialog
from PyQt5.QtGui import QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QRectF
import numpy as np


class ImageWithMouseControl(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(800, 600)  # set initial size to 800x600
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.points = []
        self.pointPen = QPen(Qt.red, 10)
        self.linePen = QPen(Qt.green, 7)
        self.reference = None
        self.real_world_distance = None
        self.imageItem = None
        self.lastPos = None
        self.currentPos = None
        self.currentLine = None

    def reset(self):
        self.points.clear()
        self.reference = None
        self.real_world_distance = None
        self.scene.clear()
        self.imageItem = None

    def setImage(self, image_path):
        self.reset()
        pixmap = QPixmap(image_path)
        self.imageItem = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))

    def mousePressEvent(self, event):
        if self.imageItem is None:
            return super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            if self.imageItem.contains(pos):
                self.points.append(pos)
                self.drawPoint(pos)
                if len(self.points) == 2:
                    self.drawMeasurement()

    def drawPoint(self, pos):
        self.scene.addEllipse(pos.x(), pos.y(), 10, 10, self.pointPen)

    def drawMeasurement(self):
        point1, point2 = self.points[:2]
        self.scene.addLine(point1.x(), point1.y(), point2.x(), point2.y(), self.linePen)
        distance = np.sqrt((point1.x() - point2.x())**2 + (point1.y() - point2.y())**2)

        if self.reference is None:
            self.reference = distance
            self.real_world_distance, ok = QInputDialog.getDouble(self, 'Real Distance (cm)',
                                                                  'Enter the real distance (centimeter):\n'
                                                                  'For Small DWS: \nWidth = 60(cm)\nLength = 80(cm)\n\n'
                                                                  'For Bulky DWS: \nWidth = 120(cm)\nLength = 140(cm)')
            text = self.scene.addText(str(self.real_world_distance), QFont('Arial', 16))
            text.setDefaultTextColor(Qt.red)
        else:
            real_distance = round((distance / self.reference) * self.real_world_distance, 4)
            text = self.scene.addText(str(real_distance), QFont('Arial', 12))
            text.setDefaultTextColor(Qt.white)

        text.setPos((point1 + point2)/2)
        self.points.clear()

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mouseMoveEvent(self, event):
        if self.imageItem is None:
            return super().mouseMoveEvent(event)

        self.currentPos = self.mapToScene(event.pos())

        if event.buttons() == Qt.RightButton:
            if self.lastPos is not None:
                diff = event.pos() - self.lastPos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            self.lastPos = event.pos()
        elif event.buttons() == Qt.LeftButton:
            self.drawCurrentLine()

    def mouseReleaseEvent(self, event):
        if self.imageItem is None:
            return super().mouseReleaseEvent(event)

        if event.button() == Qt.RightButton:
            self.lastPos = None
        elif event.button() == Qt.LeftButton:
            if self.currentLine is not None and self.currentLine.scene() is not None:
                self.scene.removeItem(self.currentLine)
            self.currentLine = None

    def drawCurrentLine(self):
        if len(self.points) == 1 and self.currentPos:
            if self.currentLine is not None and self.currentLine.scene() is not None:
                self.scene.removeItem(self.currentLine)
            self.currentLine = self.scene.addLine(self.points[0].x(), self.points[0].y(),
                                                  self.currentPos.x(), self.currentPos.y(), self.linePen)
