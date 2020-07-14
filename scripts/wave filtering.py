"""
This program takes the frequency waves in a stereo wave file.
It showcases multiple filtering techniques and shows what they do to the signal.
"""
import io as io
import numpy as np
import wave as wave
from PIL import ImageTk, Image
from scipy import signal as sp
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

plt.rcParams.update({'figure.autolayout': True})

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img.copy()


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

        self.timeData = None
        self.freqData = None
    
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        frame = tk.Frame(self.window)
        frame.grid(row=1, column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()

        # init frames
        self.median_kernel_size = tk.Scale(self.window, from_=3, to=103, variable=3, orient=tk.HORIZONTAL, label="Median Kernel Size")
        self.median_kernel_size.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))

        self.current_combo_item = tk.StringVar()
        self.filter_combo_box = ttk.Combobox(
            self.window, width=27, textvariable=self.current_combo_item)
        self.filter_combo_box['values'] = ('Median', 'Low-pass', 'High-pass')
        self.filter_combo_box.current(0)
        self.filter_combo_box.grid(row=1, column=1, columnspan=2)

        self.filter_btn = tk.Button(self.window, text="filter",
                                    command=self.onFilter, padx=2, pady=2)
        self.filter_btn.grid(row=2, column=1, columnspan=1, sticky=(tk.W, tk.E))

        self.reset_btn = tk.Button(self.window, text="reset",
                                   command=self.reset, padx=2, pady=2)
        self.reset_btn.grid(row=2, column=2, columnspan=1, sticky=(tk.W, tk.E))

    def init_menu(self):
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.askWavFileDialog)
        menubar.add_cascade(label="File", menu=filemenu)
        return menubar

    def onFilter(self):
        if self.timeData is None or self.freqData is None:
            return

        filteredTimeData = None
        filteredFreqData = None
        if self.filter_combo_box.get() == 'Median':
            odd_kernel_size = self.median_kernel_size.get() // 2 * 2 + 1
            filteredTimeData = sp.medfilt(self.timeData, odd_kernel_size)
            filteredFreqData = sp.medfilt(self.freqData, odd_kernel_size)
            self.median_kernel_size.set(odd_kernel_size)

        else:
            return

        self.ax[0].plot(np.arange(44100)/44100, filteredTimeData)
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
            self.ax[0].plot(np.arange(44100)/44100, self.timeData)
            self.ax[1].plot(self.freqData)
            self.canvas.draw()
            self.toolbar.update()

    def askWavFileDialog(self):
        """ asks the user for a wave file to open """
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("Wave files", "*.wav")])

        try:
            activeWaveFile = wave.open(file_path, 'r')
        except:
            print("invalid file (not 16bit signed WAV")
            return

        sz = 44100
        self.timeData = np.frombuffer(
            activeWaveFile.readframes(sz), dtype=np.int16)
        self.timeData = self.timeData[0::2]
        self.freqData = abs(np.fft.rfft(self.timeData))

        self.ax[0].plot(np.arange(44100)/44100, self.timeData)
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
