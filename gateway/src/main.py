import sys
from PyQt5.QtWidgets import QMainWindow, QToolTip, QPushButton, QApplication, QMessageBox, QDesktopWidget, QAction, qApp, QMenuBar
from PyQt5.QtGui import QFont, QIcon


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        # Menu bar
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        #exitAct.triggered.connect(qApp.quit)

        menubar = QMenuBar()
        #menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(exitAct)

        self.setMenuBar(menubar)

        # Status bar
        self.statusBar().showMessage("System ready...")

        # Tool tip
        QToolTip.setFont(QFont('black', 10))
        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Quit', self)
        btn.clicked.connect(QApplication.instance().quit)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Test')
        self.center()
        self.show()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'warning', "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
