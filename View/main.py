from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QToolBar, QMessageBox, QTextBrowser
from PyQt5.QtGui import QPainter, QIcon, QImage

from Controller.main import ImageWithMouseControl


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
