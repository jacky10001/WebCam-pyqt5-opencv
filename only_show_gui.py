import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_main import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())