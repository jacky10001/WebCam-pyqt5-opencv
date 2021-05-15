"""   
    @update: 2021.05.14
"""

import cv2
import sys, time, os
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_main import Ui_MainWindow


class Camera(QtCore.QThread):
    rawdata = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.cam is None or not self.cam.isOpened():
            self.connect = False
            self.running = False
        else:
            self.connect = True
            self.running = False

    def run(self):
        while self.running and self.connect:
            ret, img = self.cam.read()
            if ret:
                self.rawdata.emit(img)
            else:
                print("Warning!!!")
                self.connect = False
    
    def open(self):
        if self.connect:
            self.running = True

    def stop(self):
        if self.connect:
            self.running = False

    def close(self):
        if self.connect:
            self.running = False
            time.sleep(1)
            self.cam.release()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.viewData.setScaledContents(True)
        
        self.view_x = self.view.horizontalScrollBar()
        self.view_y = self.view.verticalScrollBar()
        self.view.installEventFilter(self)
        self.last_move_x = 0
        self.last_move_y = 0

        self.frame_num = 0
        
        self.ProcessCam = Camera()
        if self.ProcessCam.connect:
            self.debugBar('Connection!!!')
            self.ProcessCam.rawdata.connect(self.getRaw)
        else:
            self.debugBar('Disconnection!!!')
        
        self.camBtn_open.clicked.connect(self.openCam)
        self.camBtn_stop.clicked.connect(self.stopCam)
        
    def getRaw(self, data):
        self.showData(data)
        
    def openCam(self):
        if self.ProcessCam.connect:
            self.ProcessCam.open()
            self.ProcessCam.start()
            self.camBtn_open.setEnabled(False)
            self.camBtn_stop.setEnabled(True)
            self.viewCbo_roi.setEnabled(True)

    def stopCam(self):
        if self.ProcessCam.connect:
            self.ProcessCam.stop()
            self.camBtn_open.setEnabled(True)
            self.camBtn_stop.setEnabled(False)
            self.viewCbo_roi.setEnabled(False)

    def showData(self, img):
        self.Ny, self.Nx, _ = img.shape

        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)
        qimg = QtGui.QImage(img.data, self.Nx, self.Ny, QtGui.QImage.Format_RGB888)
        self.viewData.setScaledContents(True)
        self.viewData.setPixmap(QtGui.QPixmap.fromImage(qimg))
        if self.viewCbo_roi.currentIndex() == 0: roi_rate = 0.5
        elif self.viewCbo_roi.currentIndex() == 1: roi_rate = 0.75
        elif self.viewCbo_roi.currentIndex() == 2: roi_rate = 1
        elif self.viewCbo_roi.currentIndex() == 3: roi_rate = 1.25
        elif self.viewCbo_roi.currentIndex() == 4: roi_rate = 1.5
        else: pass
        self.viewForm.setMinimumSize(self.Nx*roi_rate, self.Ny*roi_rate)
        self.viewForm.setMaximumSize(self.Nx*roi_rate, self.Ny*roi_rate)
        self.viewData.setMinimumSize(self.Nx*roi_rate, self.Ny*roi_rate)
        self.viewData.setMaximumSize(self.Nx*roi_rate, self.Ny*roi_rate)
        
        if self.frame_num == 0:
            self.time_start = time.time()
        if self.frame_num >= 0:
            self.frame_num += 1
            self.t_total = time.time() - self.time_start
            if self.frame_num % 100 == 0:
                self.frame_rate = float(self.frame_num) / self.t_total
                self.debugBar('FPS: %0.3f frames/sec' % self.frame_rate)

    def eventFilter(self, source, event):
        if source == self.view:
            if event.type() == QtCore.QEvent.MouseMove:
                if self.last_move_x == 0 or self.last_move_y == 0:
                    self.last_move_x = event.pos().x()
                    self.last_move_y = event.pos().y()
                distance_x = self.last_move_x - event.pos().x()
                distance_y = self.last_move_y - event.pos().y()
                self.view_x.setValue(self.view_x.value() + distance_x)
                self.view_y.setValue(self.view_y.value() + distance_y)
                self.last_move_x = event.pos().x()
                self.last_move_y = event.pos().y()
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                self.last_move_x = 0
                self.last_move_y = 0
            return QtWidgets.QWidget.eventFilter(self, source, event)
    
    def closeEvent(self, event):
        if self.ProcessCam.running:
            self.ProcessCam.close()
            self.ProcessCam.terminate()
        QtWidgets.QApplication.closeAllWindows()
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            if self.ProcessCam.running:
                self.ProcessCam.close()
                time.sleep(1)
                self.ProcessCam.terminate()
            QtWidgets.QApplication.closeAllWindows()

    def debugBar(self, msg):
        self.statusBar.showMessage(str(msg), 5000)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
