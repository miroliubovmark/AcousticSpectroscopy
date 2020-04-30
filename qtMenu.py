from PyQt5 import QtWidgets, uic


class CMenu(QtWidgets.QMainWindow):
    def __init__(self, name, Core):
        super(CMenu, self).__init__()
        self.Core = Core

        self.setWindowTitle(name)

        self.quitButton = QtWidgets.QPushButton("quit", self)
        self.recordButton = QtWidgets.QPushButton("Record", self)
        self.soundButton = QtWidgets.QPushButton("On/Off sound", self)

        self.textDuration = QtWidgets.QLabel("label")
        self.textDuration.setFrameStyle(QtWidgets.QLabel.Box)

        self.quitButton.clicked.connect(self.handle_quitButton)
        self.recordButton.clicked.connect(self.handle_recordButton)
        self.soundButton.clicked.connect(self.handle_soundButton)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.quitButton)
        self.layout.addWidget(self.recordButton)
        self.layout.addWidget(self.soundButton)
        self.layout.addWidget(self.textDuration)

        self.quitButton.resize(200, 50)
        self.recordButton.resize(200, 50)
        self.soundButton.resize(200, 50)

        # self.textDuration.resize(200, 50)
        # self.textDuration.setAlignment(Qt)

        self.quitButton.move(0, 0)
        self.recordButton.move(0, 60)
        self.soundButton.move(0, 120)

        # self.textDuration.move(0, 180)

        self.quitButton.setStyleSheet("QPushButton {background-color: grey; color: white;}")
        self.soundButton.setStyleSheet("QPushButton {background-color: grey; color: white;}")

        if self.Core.dump:
            self.color_recordButton = "green"
        else:
            self.color_recordButton = "red"
        self.recordButton.setStyleSheet("QPushButton {background-color: " + self.color_recordButton + "; color: white;}")

        if self.Core.PlaySound:
            self.color_soundButton = "green"
        else:
            self.color_soundButton = "red"

        self.soundButton.setStyleSheet("QPushButton {background-color: " + self.color_soundButton + "; color: white;}")

    @staticmethod
    def handle_quitButton():
        QtWidgets.QApplication.quit()

    def handle_recordButton(self):
        self.Core.changeState_record()

        if self.Core.dump:
            self.color_recordButton = "green"
        else:
            self.color_recordButton = "red"

        self.recordButton.setStyleSheet("QPushButton {background-color: " + self.color_recordButton + "; color: white;}")

    def handle_soundButton(self):
        self.Core.changeState_PlaySound()

        if self.Core.PlaySound:
            self.color_soundButton = "green"
        else:
            self.color_soundButton = "red"

        self.soundButton.setStyleSheet("QPushButton {background-color: " + self.color_soundButton + "; color: white;}")

