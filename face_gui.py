#Importing necessary libraries, mainly the OpenCV, and PyQt libraries
import cv2
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QPushButton
#############for training##############
import face_recognition
import pickle, os

 
class ShowVideo(QtCore.QObject):
    #initiating the built in camera
    camera_port = 0
    camera = cv2.VideoCapture(camera_port)
    VideoSignal = QtCore.pyqtSignal(QtGui.QImage)
    capt = None
 
    def __init__(self, parent = None):
        super(ShowVideo, self).__init__(parent)
    
    
    @QtCore.pyqtSlot()
    def startVideo(self):
        run_video = True
        while run_video:
            ret, image = self.camera.read()
            image = cv2.flip(image,1)
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #height, width, _ = color_swapped_image.shape
            width = 531
            height = 381
            qt_image = QtGui.QImage(color_swapped_image.data,
                                    width,
                                    height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            
            self.capt = image
            self.VideoSignal.emit(qt_image)
            

 
 
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
 
 
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0,0, self.image)
        self.image = QtGui.QImage()
 
    def initUI(self):
        self.setWindowTitle('Test')
 
    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
 
        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()


 
if __name__ == '__main__':
    
    
    app = QtWidgets.QApplication(sys.argv)
    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo()
    vid.moveToThread(thread)

    

    #Button to start the videocapture:
    
    central_widget = QtWidgets.QWidget()

    
    open_cam_btn = QtWidgets.QPushButton(central_widget)
    open_cam_btn.setGeometry(QtCore.QRect(620, 60, 101, 41))
    open_cam_btn.setObjectName("open_cam_btn")
    open_cam_btn.clicked.connect(vid.startVideo)
    open_cam_btn.setText("Open Camera")


    success_stat = QtWidgets.QLabel(central_widget)
    success_stat.setGeometry(QtCore.QRect(590, 160, 181, 41))
    font = QtGui.QFont()
    font.setPointSize(17)
    success_stat.setFont(font)
    success_stat.setText("")
    success_stat.setObjectName("success_stat")


    image_viewer = ImageViewer(central_widget)
    image_viewer.setGeometry(QtCore.QRect(30, 40, 531, 381))
    vid.VideoSignal.connect(image_viewer.setImage)

    label = QtWidgets.QLabel(central_widget)
    label.setGeometry(QtCore.QRect(580, 240, 181, 16))
    font = QtGui.QFont()
    label.setText("Enter ID and Click Capture")

    textEdit = QtWidgets.QTextEdit(central_widget)
    textEdit.setGeometry(QtCore.QRect(580, 270, 181, 51))
    font.setPointSize(20)
    textEdit.setFont(font)
    textEdit.setObjectName("textEdit")

    def captureImage():
        loc = "captured_faces/"
        std_id = textEdit.toPlainText()
        file_name = loc+str(std_id)+".jpg"
        cv2.imwrite(filename = file_name, img = vid.capt)

        # training with the captured photo

        #cap_image = face_recognition.load_image_file(file_name)
        cap_face_encoding = face_recognition.face_encodings(vid.capt)[0]

        id_enc_dict = {}
        id_enc_dict[std_id] = cap_face_encoding


        #the pickle file must have an empty/non-empty list inserted already
        with open('faces_name_enc.pickle', 'rb') as f:
            face_data = pickle.load(f)

        face_data.append(id_enc_dict)

        with open('faces_name_enc.pickle', 'wb') as f:
             pickle.dump(face_data, f, pickle.HIGHEST_PROTOCOL )


        success_stat.setText(std_id+" Added")
    
    capture_btn = QtWidgets.QPushButton(central_widget)
    capture_btn.setGeometry(QtCore.QRect(580, 330, 181, 91))
    font = QtGui.QFont()
    font.setPointSize(20)
    capture_btn.setFont(font)
    capture_btn.setObjectName("capture_btn")
    capture_btn.setText("Capture")
    capture_btn.clicked.connect(captureImage)
    
    main_window = QtWidgets.QMainWindow()
    main_window.setMinimumSize(QSize(800, 480)) 
    main_window.setCentralWidget(central_widget)
    
    main_window.show()

    sys.exit(app.exec_())