from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication,QWidget, QVBoxLayout, QPushButton, QFileDialog , QLabel, QTextEdit
import sys

from PyQt5.QtGui import QPixmap

import face_recognition
import pickle, os

import numpy as np
import cv2

class Window(QWidget):
    imagePath = None
    def __init__(self):
        super().__init__()

        self.title = "PyQt5 Open File"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300


        self.InitWindow()


    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        vbox = QVBoxLayout()

        self.btn1 = QPushButton("Open Image")
        self.btn1.clicked.connect(self.getImage)
        vbox.addWidget(self.btn1)

        self.success_stat = QLabel("TEST STATUS")
        font = QtGui.QFont()
        font.setPointSize(17)
        self.success_stat.setFont(font)
        self.success_stat.setObjectName("success_stat")
        vbox.addWidget(self.success_stat)

        self.label = QLabel("")
        vbox.addWidget(self.label)

        self.btn1 = QPushButton("TEST IMAGE")
        self.btn1.clicked.connect(self.rec)
        vbox.addWidget(self.btn1)


        self.setLayout(vbox)

        self.show()

    def getImage(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            '/home/avishek/Documents/Python tasks/face_recognition/', "Image files (*.jpg *.gif)")
        self.imagePath = fname[0]
        pixmap = QPixmap(self.imagePath)
        self.label.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())

    def rec(self):
        img = face_recognition.load_image_file(self.imagePath)
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        with open('faces_name_enc.pickle', 'rb') as f:
            face_data = pickle.load(f)

        known_face_encodings = []
        known_face_names = []
        face_names = []
        for fd in face_data:
            known_face_names.append(list(fd.keys())[0])
            known_face_encodings.append(list(fd.values())[0])

        for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)
        
        img_name = self.imagePath
        img_name = img_name.split('/')[-1].split('.')[0]
        print("image name: ",img_name)
        print("predicted name: ",name)
        if img_name==name:
            print("Test Status: Matched")
            self.success_stat.setText("Status: Passed")
        else:
            print("Test Status: Match Failed")
            self.success_stat.setText("Status: Failed")

        



App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())