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
#############for excel##############
import datetime
import time
import pandas as pd

from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 


run_video = True
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
        #####################
        with open('faces_name_enc.pickle', 'rb') as f:
            face_data = pickle.load(f)

        # Create arrays of known face encodings and their names
        known_face_encodings = []
        known_face_names = []

        for fd in face_data:
            known_face_names.append(list(fd.keys())[0])
            known_face_encodings.append(list(fd.values())[0])



        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        

        df = pd.read_csv("StudentDetails"+os.sep+"StudentDetails.csv")
        col_names = ['ID', 'Name', 'Date', 'Time']
        attendance = pd.DataFrame(columns=col_names)



        while run_video:
            ret, image = self.camera.read()
            image = cv2.flip(image,1)
            #height, width, _ = color_swapped_image.shape
            width = 531
            height = 381


            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = 0000

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(image, str(name), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['ID'] == int(name)]['Name'].values
                tt = str(name)+"-"+aa
                print(tt)
                attendance.loc[len(attendance)] = [name, aa, date, timeStamp]
            attendance = attendance.drop_duplicates(subset=['ID'], keep='first')
        
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qt_image = QtGui.QImage(color_swapped_image.data,
                                    width,
                                    height,
                                    color_swapped_image.strides[0],
                                    QtGui.QImage.Format_RGB888)
            
            self.capt = image
            self.VideoSignal.emit(qt_image)



        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        fileName = "Attendance"+os.sep+"Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
        print(fileName)
        attendance.to_csv(fileName, index=False)



 
 
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

    def stopVideo():
        global run_video
        run_video = False
    

    #Button to start the videocapture:
    
    central_widget = QtWidgets.QWidget()
    
    image_viewer = ImageViewer(central_widget)
    image_viewer.setGeometry(QtCore.QRect(30, 40, 531, 381))
    vid.VideoSignal.connect(image_viewer.setImage)
    
    open_cam_btn = QtWidgets.QPushButton(central_widget)
    open_cam_btn.setGeometry(QtCore.QRect(620, 60, 101, 41))
    open_cam_btn.setObjectName("open_cam_btn")
    open_cam_btn.clicked.connect(vid.startVideo)
    open_cam_btn.setText("Open Camera")



    stop_cam_btn = QtWidgets.QPushButton(central_widget)
    stop_cam_btn.setGeometry(QtCore.QRect(620, 240, 101, 41))
    stop_cam_btn.setObjectName("stop_cam_btn")
    stop_cam_btn.clicked.connect(stopVideo)
    stop_cam_btn.setText("Stop Camera")


    main_window = QtWidgets.QMainWindow()
    main_window.setMinimumSize(QSize(800, 480)) 
    main_window.setCentralWidget(central_widget)
    main_window.setWindowTitle("Attendance Interface")
    main_window.setWindowIcon(QIcon("logo.png")) 
    
    main_window.show()

    sys.exit(app.exec_())