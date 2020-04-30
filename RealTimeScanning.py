from Sound import CSound
from Spectre import CSpectre
from qtPlot import CPlot
from qtMenu import CMenu

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import numpy as np


class CRealTimeScanning:
    def __init__(self):
        """ Constants initialisation """
        self.InputSampleRate = 48000
        self.OutputSampleRate = 48000

        self.InputDevice = "default"
        self.OutputDevice = "default"

        self.InputBlockSize = 100

        self.duration = 2
        self.PlaySound = False
        self.dump = False

        self.MinFrequency = 100
        self.MaxFrequency = 10000

        self.volume = 0.06

        self.signalPlot_PenColor = "b"
        self.fftPlot_PenColor = "b"
        self.signalPlot_Background = "w"
        self.fftPlot_Background = "w"

        self.app = QtWidgets.QApplication([])  # QApplication
        """ End of constants initialisation """

        self.SoundParameters = ["duration = " + str(self.duration) + "s", "MinFrequency = " + str(self.MinFrequency) + "Hz",
                                "MaxFrequency = " + str(self.MaxFrequency) + "Hz",
                                "Input sample rate = " + str(self.InputSampleRate)]

        self.SilentParameters = ["duration = " + str(self.duration) + "s", "Input sample rate = " + str(self.InputSampleRate)]

        self.SoundProcessor = CSound(self.InputSampleRate, self.OutputSampleRate, self.InputDevice, self.OutputDevice,
                                     self.InputBlockSize)

        self.signalPlot = CPlot("Signal", self.signalPlot_Background)
        self.fftPlot = CPlot("FFT", self.fftPlot_Background)
        self.menu = CMenu("Menu", self)

        self.adjust_signalPlot()
        self.adjust_fftPlot()
        self.adjust_menu()

        self.timerPeriod = self.duration * 1000  # Cast to msec

        self.mainLoop()

    def adjust_signalPlot(self):
        self.signalPlot.setGeometry(0, 0, 1000, 800)
        self.signalPlot.graphWidget.setXRange(0, self.duration)
        self.signalPlot.graphWidget.setYRange(-1, 1)

        self.signalPlot.show()

    def adjust_fftPlot(self):
        self.fftPlot.setGeometry(0, 975, 1000, 800)
        self.fftPlot.graphWidget.setXRange(0, 5000)
        self.fftPlot.graphWidget.setYRange(0, 100)

        self.fftPlot.show()

    def adjust_menu(self):
        self.menu.setGeometry(1175, 0, 400, 800)

        self.menu.show()

    def transformAndPlotUpdate(self):
        spectre = CSpectre(self.SoundProcessor.recording)

        self.signalPlot.updatePlot(np.linspace(0, len(self.SoundProcessor.recording) / self.InputSampleRate,
                                               len(self.SoundProcessor.recording)), self.SoundProcessor.recording)
        self.fftPlot.updatePlot(spectre.frequencies, spectre.values)

    def silentScanning(self):
        self.SoundProcessor.stream_stop_record(dump=self.dump, parameters=self.SilentParameters)

        self.transformAndPlotUpdate()

        self.SoundProcessor.setZeros()
        self.SoundProcessor.stream_start_record()

    def scanning(self):
        sound = self.SoundProcessor.generateSmoothScanningSound(self.MinFrequency, self.MaxFrequency, self.duration,
                                                                amplitude=self.volume)

        self.SoundProcessor.setZeros()
        self.SoundProcessor.stream_start_record()
        self.SoundProcessor.playAudio(sound)
        self.SoundProcessor.stream_stop_record(dump=self.dump, parameters=self.SoundParameters)

        self.transformAndPlotUpdate()

    def mainLoop(self):
        self.SoundProcessor.stream_start_record()

        timer = QTimer()

        timer.timeout.connect(self.timerHandler)

        timer.start(self.timerPeriod)

        self.app.exec()  # Qt event loop

    def timerHandler(self):
        if self.PlaySound:
            self.scanning()
        else:
            self.silentScanning()

    def changeState_record(self):
        if self.dump:
            self.dump = False

        else:
            self.dump = True

        print(self.dump)

    def changeState_PlaySound(self):
        if self.PlaySound:
            self.PlaySound = False
        else:
            self.PlaySound = True


Scanner = CRealTimeScanning()
