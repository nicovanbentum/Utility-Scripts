# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import random
import mplwidget
import wave
from scipy import signal as sp


class MatplotlibWidget(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        loadUi("untitled.ui", self)

        self.setWindowTitle("Wave Filterer")

        # button connections
        self.load_button.clicked.connect(self.file_dialog)
        self.filter_time_button.clicked.connect(self.on_filter_time)

        self.filter_freq_button.clicked.connect(self.on_filter_frequency)
        self.reset_button.clicked.connect(self.reset)

        self.taps_input.setValue(6)
        self.cutoff_input.setValue(0.1)

        print(self.filter_box.currentText())

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        self.wavFile = None
        self.timeData = None
        self.freqData = None

    #moving average filter using cummulative summing as described by: https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html
    def moving_average(self, a, n=3):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret / n

    # file dialog for opening wav files
    def file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "", "Wave Files (*.wav)", options=options)

        try:
            self.wavFile = wave.open(file_path, 'r')
        except:
            print("invalid file (not 16bit signed WAV")
            return

        self.timeData = np.frombuffer(
            self.wavFile.readframes(self.wavFile.getnframes()), dtype=np.int16)
        self.timeData = self.timeData[0::2]
        self.freqData = abs(np.fft.rfft(self.timeData))

        self.plot_and_update()

    # perform time data filtering and update the canvas
    def on_filter_time(self):
        if self.timeData is None:
            return
        s = self.filter_box.currentText()
        filteredData = self.get_filtered_data(self.timeData, self.filter_box.currentText())
        self.MplWidget.canvas.axes[0].plot(np.arange(self.wavFile.getnframes()) / self.wavFile.getframerate(), filteredData)

        if self.reflect_freq_box.isChecked():
            filteredFreqData = abs(np.fft.rfft(filteredData))
            self.MplWidget.canvas.axes[1].plot(filteredFreqData)

        self.MplWidget.canvas.draw()

    # filters a 1D data array based on the method selected in the qt5 gui
    def get_filtered_data(self, data, method):
        if method == 'Median':
            k = self.median_filter_slider.value() // 2 * 2 + 1
            return sp.medfilt(data, k)
        elif method == 'Moving average':
            k = self.moving_average_slider.value()
            return self.moving_average(data, k)
        elif method == 'FIR':
            print(self.cutoff_input.value()) 
            print(self.taps_input.value())
            b = sp.firwin(self.taps_input.value(), self.cutoff_input.value())
            return sp.lfilter(b, [1.0], data)
        else:
            return None

    # perform frequency data filtering and update the canvas
    def on_filter_frequency(self):
        if self.freqData is None: 
            return
        s = self.filter_box.currentText()
        filteredData = self.get_filtered_data(self.freqData, self.filter_box.currentText())
        self.MplWidget.canvas.axes[1].plot(filteredData)

        if self.reflect_time_box.isChecked():
            filteredTimeData = np.fft.irfft(filteredData, len(self.timeData))
            self.MplWidget.canvas.axes[0].plot(np.arange(self.wavFile.getnframes()) /
                                               self.wavFile.getframerate(), filteredTimeData)

        self.MplWidget.canvas.draw()

    # plot original data to both graphs
    def plot_and_update(self):
        self.MplWidget.canvas.axes[0].plot(np.arange(self.wavFile.getnframes()) /
                                           self.wavFile.getframerate(), self.timeData)
        self.MplWidget.canvas.axes[1].plot(self.freqData)

        self.MplWidget.canvas.draw()

    # start over with original data
    def reset(self):
        self.MplWidget.clear_axes()
        self.MplWidget.init_axes()

        if self.timeData is not None and self.freqData is not None:
            self.plot_and_update()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
