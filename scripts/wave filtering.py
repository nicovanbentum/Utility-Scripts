"""
This program takes the frequency waves in a stereo wave file.
It showcases multiple filtering techniques and shows what they do to the signal.
"""
import io as io
import numpy as np
import math as math
import wave as wave
from PIL import ImageTk, Image
from scipy import signal as sp
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

plt.rcParams.update({'figure.autolayout': True})


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret / n


class Application:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Wave Filterer")
        self.window.protocol("WM_DELETE_WINDOW", exit)
        self.window.columnconfigure(0, weight=4)
        self.window.rowconfigure(0, weight=4)

        # init title bar
        self.window.config(menu=self.init_menu())

        # init result figure
        self.fig, self.ax = plt.subplots(nrows=2, ncols=1)
        # time domain
        r = 2**16/16
        self.ax[0].set_ylim([-r, r])
        self.ax[0].set_xlabel('time [s]')
        self.ax[0].set_ylabel('sample value [-]')

        # frequency domain
        self.ax[1].set_xscale('log')
        self.ax[1].set_xlabel('frequency [Hz]')
        self.ax[1].set_ylabel('|amplitude|')

        self.wavFile = None
        self.timeData = None
        self.freqData = None

        # init frames
        kernel_med_size = tk.StringVar()
        self.median_slider = tk.Scale(
            self.window, from_=3, to=103, variable=kernel_med_size, orient=tk.HORIZONTAL, label="Median Kernel")
        self.median_slider.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N))

        kernel_ma_size = tk.StringVar()
        self.move_ave_slider = tk.Scale(self.window, from_=3, to=103, variable=kernel_ma_size, orient=tk.HORIZONTAL, label="Moving Average Kernel")
        self.move_ave_slider.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N))

        self.current_combo_item = tk.StringVar()
        self.current_combo_item.set('Median')
        self.filter_combo_box = tk.OptionMenu(self.window, self.current_combo_item, 'Median', 'Moving average')
        self.filter_combo_box.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.filter_btn = tk.Button(self.window, text="filter",
                                    command=self.onFilter, padx=2, pady=2)
        self.filter_btn.grid(
            row=3, column=0, columnspan=1, sticky=(tk.W, tk.E))

        self.reset_btn = tk.Button(self.window, text="reset",
                                   command=self.reset, padx=2, pady=2)
        self.reset_btn.grid(row=3, column=1, columnspan=1, sticky=(tk.W, tk.E))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=3)

        frame = tk.Frame(self.window)
        frame.grid(row=3, column=2)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()

    def init_menu(self):
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.askWavFileDialog)
        menubar.add_cascade(label="File", menu=filemenu)
        return menubar

    
    def filterFrequency(self):
        if self.freqData is None:
            return


    def onFilter(self):
        if self.timeData is None or self.freqData is None:
            return

        filteredTimeData = None
        filteredFreqData = None

        odd_kernel_size = self.median_slider.get() // 2 * 2 + 1

        if self.current_combo_item.get() == 'Median':
            filteredTimeData = sp.medfilt(self.timeData, odd_kernel_size)
            filteredFreqData = sp.medfilt(self.freqData, odd_kernel_size)
            self.median_slider.set(odd_kernel_size)

        elif self.current_combo_item.get() == 'Moving average':
            filteredTimeData = moving_average(self.timeData, self.move_ave_slider.get())
            filteredFreqData = self.freqData = abs(np.fft.rfft(filteredTimeData))
        else:
            return

        self.ax[0].plot(np.arange(self.wavFile.getnframes()) /
                        self.wavFile.getframerate(), filteredTimeData)
        self.ax[1].plot(filteredFreqData)
        self.canvas.draw()
        self.toolbar.update()

    def reset(self):
        self.ax[0].cla()
        self.ax[1].cla()

        r = 2**16/16
        self.ax[0].set_ylim([-r, r])
        self.ax[0].set_xlabel('time [s]')
        self.ax[0].set_ylabel('sample value [-]')

        self.ax[1].set_xscale('log')
        self.ax[1].set_xlabel('frequency [Hz]')
        self.ax[1].set_ylabel('|amplitude|')

        if self.timeData is not None and self.freqData is not None:
            self.ax[0].plot(np.arange(self.wavFile.getnframes()) /
                            self.wavFile.getframerate(), self.timeData)
            self.ax[1].plot(self.freqData)
            self.canvas.draw()
            self.toolbar.update()

    def askWavFileDialog(self):
        """ asks the user for a wave file to open """
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("Wave files", "*.wav")])

        try:
            self.wavFile = wave.open(file_path, 'r')
        except:
            print("invalid file (not 16bit signed WAV")
            return

        self.timeData = np.frombuffer(
            self.wavFile.readframes(self.wavFile.getnframes()), dtype=np.int16)
        self.timeData = self.timeData[0::2]
        self.freqData = abs(np.fft.rfft(self.timeData))

        self.ax[0].plot(np.arange(self.wavFile.getnframes()) /
                        self.wavFile.getframerate(), self.timeData)
        self.ax[1].plot(self.freqData)

        self.canvas.draw()
        self.toolbar.update()

    def run(self):
        self.window.mainloop()


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
