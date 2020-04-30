import numpy as np
from scipy.signal import find_peaks


class CSpectre:
    def __init__(self, signal, samplerate=48000, needFFT=True):
        """
        Cast signal from space-time representation into amplitude-frequency representation
        """
        if needFFT:
            self.values = (np.abs(np.fft.rfft(signal)))
        else:
            self.values = (signal)

        self.size = len(self.values)
        self.frequencies = (np.linspace(0, samplerate // 2, num=self.size))

    @staticmethod
    def divideSpectres(spectre1, spectre2):
        result = []

        index = 0

        for i in range(spectre1.size):
            CurrentFrequency = spectre1.frequencies[i]
            MinDelta = 1000000

            while index < len(spectre2.frequencies) - 1:
                ConcernedFrequency = spectre2.frequencies[index]
                delta = abs(ConcernedFrequency - CurrentFrequency)

                if delta < MinDelta:
                    MinDelta = delta
                    index += 1

                else:
                    break

            result.append(spectre1.values[i] / spectre2.values[index])

        spectre = CSpectre(result, needFFT=False)
        return spectre

    def findLocalMaximums(self):
        """
        The function finds maximums, their indexes in arrays, frequencies correlated to the maximums.

        :return: 2-dim array
        findLocalMaximums[i] = [index of i-Max in internal arrays, correlated frequency, the value of maximum]
        """
        maximums = []

        maximum = max(self.values)
        threshold = maximum / 2

        for i in range(1, len(self.values) - 1):
            if self.values[i] > threshold:
                if self.values[i - 1] < self.values[i] and self.values[i] > self.values[i + 1]:
                    maximums.append([i, self.frequencies[i], self.values[i]])

        return maximums

    def findPeaks(self):
        PeaksAndConditions = find_peaks(self.values)
        peaks = PeaksAndConditions[0]

        return peaks
