import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
import os
import datetime
import sounddevice as sd
from Spectre import CSpectre
import plotly.graph_objects as go


class CSound:
    def __init__(self, InputSampleRate, OutputSampleRate, InputDevice, OutputDevice, InputBlockSize=100):
        self.InputSampleRate = InputSampleRate
        self.OutputSampleRate = OutputSampleRate

        self.InputDevice = InputDevice
        self.OutputDevice = OutputDevice

        self.InputBlockSize = InputBlockSize

        self.recording = []      # Recorded data from microphone
        self.inp_stream = sd.InputStream(samplerate=self.InputSampleRate, device=self.InputDevice, callback=self.callback, blocksize=self.InputBlockSize)

    def setZeros(self):
        self.recording.clear()

    def generateSineSound(self, OutputFrequency, Duration, amplitude=10):
        t = np.arange(self.OutputSampleRate * Duration) / self.OutputSampleRate
        signal = np.sin(t * 2 * np.pi * OutputFrequency) * amplitude

        return signal

    def generateSmoothScanningSound(self, MinFrequency, MaxFrequency, Duration, amplitude=1, straightOrder=True):
        t = np.arange(self.OutputSampleRate * Duration) / self.OutputSampleRate
        delta = (MaxFrequency - MinFrequency) / len(t)

        signal = []

        for i in range(len(t)):
            omega = (MinFrequency + delta * i) * 2 * np.pi
            value = np.sin(omega * t[i]) * amplitude
            signal.append(value)

        if not straightOrder:
            signal.reverse()

        return signal

    def generateEqualWavelengthSound(self, MinFrequency, MaxFrequency, Duration, amplitude=1):
        t = np.arange(self.OutputSampleRate * Duration) / self.OutputSampleRate
        print(t)
        signal = []

        for i in range(len(t)):
            omega = 2 ** t[i] * 2 * np.pi
            value = np.sin(omega * t[i]) * amplitude
            signal.append(value)

        return signal

    def playAudio(self, sound):
        print(type(sound))
        sd.play(sound, self.OutputSampleRate, device=self.OutputDevice)
        sd.wait()  # Wait until all data are played back

    def callback(self, indata, frames, time, status):
        self.recording.extend([item[0] for item in indata])

    def stream_start_record(self):
        self.inp_stream.start()

    def stream_stop_record(self, dump=True, parameters=None):
        self.inp_stream.stop()

        if dump:
            index = self.saveAsWavFile(parameters=parameters)
            return index

        return None

    def getRecording(self):
        return self.recording

    def drawPlot(self):
        print(len(self.recording))
        x = np.linspace(0, len(self.recording) - 1, num=len(self.recording))

        plt.plot(x / 48, self.recording)
        # plt.plot(x, self.recording, 'r.', markersize=2.5)
        # plt.figure()
        plt.savefig("plot.png")

    def saveAsWavFile(self, filename=None, parameters=None):
        GlobalPath = '/home/mark/PycharmProjects/Audio/Recordings/'
        LocalDirName = str(datetime.date.today())
        GlobalDirName = GlobalPath + LocalDirName + '/'

        tree = os.walk(GlobalPath)

        isCreated = False
        for root, dirs, files in tree:
            for directory in dirs:
                if directory == LocalDirName:
                    isCreated = True
                    break

        if not isCreated:
            os.mkdir(GlobalDirName)

        npRecording = np.array(self.recording)

        if filename is not None:
            self.save(npRecording, self.InputSampleRate, filename + '.wav')
            return None

        else:
            FileIndex = CSound.getLastFile(GlobalDirName)

            if FileIndex is None:
                FileIndex = 0

            newFileIndex = GlobalDirName + str(FileIndex + 1) + '.wav'

            Name_Last = '/home/mark/PycharmProjects/Audio/Recordings/last/last'

            print(newFileIndex)
            self.save(npRecording, self.InputSampleRate, newFileIndex)
            self.save(npRecording, self.InputSampleRate, Name_Last)

            # Save parameters file
            if parameters is not None:
                with open(GlobalDirName + str(FileIndex + 1) + "_parameters_.txt", "w") as file:
                    for item in parameters:
                        file.write(item)
                        file.write("\n")

            return FileIndex

    @staticmethod
    def plotSmoothSound_Recording(sound, MinFrequency, MaxFrequency):
        x = np.linspace(MinFrequency, MaxFrequency, len(sound))
        y = sound

        # plot = PyGnuplot.plot(x, y)

    @staticmethod
    def getFilename(file):
        pos = file.find('.wav')

        if pos == -1:
            return None
        else:
            filename = file[0: pos]

        try:
            index = int(filename)
            return index

        except Exception:
            return None

    @staticmethod
    def getLastFile(path):
        for root, dirs, files in os.walk(path):

            if len(files) == 0:
                return None

            maxIndex = -1
            for file in files:
                index = CSound.getFilename(file)

                if index is None:
                    continue

                if index > maxIndex:
                    maxIndex = index

            if maxIndex == -1:
                return None

            return maxIndex

    @staticmethod
    def printIODevices():
        print(sd.query_devices())

    @staticmethod
    def save(arr, samplerate, name):
        wavfile.write(name, rate=samplerate, data=arr)

    @staticmethod
    def fastFourierTransform(sound, samplerate=48000):
        frequencies = np.abs(np.fft.rfft(sound))
        Spectre = CSpectre(frequencies, samplerate=samplerate)

        return Spectre

    @staticmethod
    def calculateAbsAverageValue(arr):
        AbsSum = 0
        for item in arr:
            AbsSum += abs(item)

        return AbsSum / len(arr)

    @staticmethod
    def findEndOfSegment(beg, delta, NoiseThreshold, sound):
        pos = beg
        while pos < len(sound):
            AvgOnSegment = CSound.calculateAbsAverageValue(sound[pos: pos + delta])
            if AvgOnSegment < NoiseThreshold:
                return pos

            pos += delta

        return len(sound)

    @staticmethod
    def parseSerialSound(sound, SampleRate):
        x = np.linspace(0, len(sound) - 1, num=len(sound))

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=x / 48000, y=sound))
        fig1.show()

        # plt.plot(x, sound)
        # plt.savefig('tmp.png')

        frequencies = []
        delta = 200

        average = CSound.calculateAbsAverageValue(sound[0:1000])

        NoiseThreshold = average * 5
        print('NoiseThreshold =', NoiseThreshold)

        offset = 0
        while offset < len(sound):
            AvgOnSegment = CSound.calculateAbsAverageValue(sound[offset: offset + delta])

            flag = True

            if AvgOnSegment > NoiseThreshold:
                beg = offset
                end = CSound.findEndOfSegment(offset, delta, NoiseThreshold, sound)

                # print('end - beg =', end - beg)
                if (end - beg) > 5000:
                    flag = False
                    offset = end

                    beg += 1500
                    end -= 1500

                    CurrentSpectre = CSound.fastFourierTransform(sound[beg: end])
                    frequencies.append(CurrentSpectre)

            if flag:
                offset += delta

        return frequencies

    @staticmethod
    def findBegOfSignal(sound, delta=200):
        AverageNoiseValue = CSound.calculateAbsAverageValue(sound[0:1000])

        NoiseThreshold = AverageNoiseValue * 5

        offset = 1000
        beg = None
        while beg is None:
            AvgOnSegment = CSound.calculateAbsAverageValue(sound[offset: offset + delta])

            if AvgOnSegment > NoiseThreshold:
                beg = offset + delta

            offset += delta

        return beg

    @staticmethod
    def parseSmoothScanningSound(sound, Samplerate=48000, parsingDelta=4800):
        spectres = []

        leftBorder = 0
        rightBorder = parsingDelta

        while rightBorder < len(sound):
            CurrentSpectre = CSound.fastFourierTransform(sound[leftBorder: rightBorder], samplerate=Samplerate)

            spectres.append(CurrentSpectre)

            leftBorder += parsingDelta // 16
            rightBorder += parsingDelta // 16

        return spectres

    @staticmethod
    def hilbert(signal):
        spectre = (np.fft.rfft(signal))

        res = np.fft.ifft(spectre)

        # amplitudes = np.imag(np.fft.irfft(spectre))

        return np.imag(res)

    @staticmethod
    def readWavFile(filename):
        """
        The function returns list of 2 elements
            0 - samplerate
            1 - data
        """
        return wavfile.read(filename)
