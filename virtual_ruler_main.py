import sys
import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QInputDialog, QApplication, QMainWindow, QFileDialog,\
    QAction, QToolBar, QMessageBox, QTextBrowser
from PyQt5.QtGui import QPixmap, QPen, QFont, QPainter, QIcon, QImage
from PyQt5.QtCore import Qt, QRectF


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NJV Virtual Ruler")
        self.imageViewer = ImageWithMouseControl(self)
        self.setCentralWidget(self.imageViewer)

        self.resize(800, 600)  # Set the initial size to 800x600

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        openAction = QAction(QIcon('open_icon.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openImage)
        openAction.setStatusTip('Open Image')
        fileMenu.addAction(openAction)

        saveAction = QAction(QIcon('save_icon.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveImage)
        saveAction.setStatusTip('Save Image')
        fileMenu.addAction(saveAction)

        exitAction = QAction(QIcon('exit_icon.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QApplication.instance().quit)
        exitAction.setStatusTip('Exit Application')
        fileMenu.addAction(exitAction)

        toolbar = QToolBar('Main Toolbar')
        toolbar.addAction(openAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(exitAction)
        self.addToolBar(toolbar)

        self.statusbar = self.statusBar()

        # Add 'About' menu
        helpMenu = self.menuBar().addMenu('Help')
        aboutAction = QAction(QIcon('about_icon.png'), 'About', self)
        aboutAction.triggered.connect(self.showAboutInfo)
        helpMenu.addAction(aboutAction)

        # Add this attribute
        self.aboutBrowser = QTextBrowser()
        self.aboutBrowser.setWindowTitle("About tool: Virtual Ruler")
        self.aboutBrowser.setHtml(
            "This application is forked and extended from an Ozgur Ural's original "
            "repository.<br><br> "

            "<b> Author: Nguyễn Minh Hiếu </b><br>Business Analyst Intern at CEO's Office <br> "
            "Ninja Van Vietnam.<br><br> "

            "For source code, you can visit: <br>"
            "<a href='https://github.com/MinhHieu-Nguyen-dn/njv-virtual-ruler'>"
            "https://github.com/MinhHieu-Nguyen-dn/njv-virtual-ruler"
            "</a>")
        self.aboutBrowser.setOpenExternalLinks(True)
        self.aboutBrowser.resize(400, 200)  # You can adjust the size here

    def showAboutInfo(self):
        self.aboutBrowser.show()

    def openImage(self):
        image_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
                                                    "Image files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)")
        if image_path:
            self.imageViewer.setImage(image_path)
            self.statusbar.showMessage('Image Loaded')
        else:
            QMessageBox.warning(self, 'Error', 'Could not open image')

    def saveImage(self):
        # Create a QImage object with the same dimensions as the scene
        img = QImage(self.imageViewer.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)

        # Create a QPainter object and render the scene into the QImage object
        painter = QPainter(img)
        self.imageViewer.scene.render(painter)
        painter.end()

        # Open a QFileDialog in save file mode and get the selected file path
        saved_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '',
                                                    'PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)')

        if saved_path:
            # Save the QImage object to the selected file
            img.save(saved_path)
            self.statusbar.showMessage('Image Saved')
        else:
            QMessageBox.warning(self, 'Error', 'Could not save image')


def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
