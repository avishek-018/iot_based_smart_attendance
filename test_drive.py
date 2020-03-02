from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication,QWidget, QVBoxLayout, QPushButton, QFileDialog , QLabel, QTextEdit
import sys

from PyQt5.QtGui import QPixmap







class Window(QWidget):
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
        #self.btn1.clicked.connect(self.getImage)
        vbox.addWidget(self.btn1)


        


        self.setLayout(vbox)

        self.show()

    def getImage(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            '/home/avishek/Documents/Python tasks/face_recognition/', "Image files (*.jpg *.gif)")
        imagePath = fname[0]
        pixmap = QPixmap(imagePath)
        self.label.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())



App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())