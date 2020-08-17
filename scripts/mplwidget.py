# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

    
class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.subplots(nrows=2, ncols=1)

        self.init_axes()

        self.setLayout(vertical_layout)

    def init_axes(self):
        # time domain
        r = 2**16/16
        self.canvas.axes[0].set_ylim([-r, r])
        self.canvas.axes[0].set_xlabel('time [s]')
        self.canvas.axes[0].set_ylabel('sample value [-]')

        # frequency domain
        self.canvas.axes[1].set_xscale('log')
        self.canvas.axes[1].set_xlabel('frequency [Hz]')
        self.canvas.axes[1].set_ylabel('|amplitude|')

    def clear_axes(self):
        self.canvas.axes[0].cla()
        self.canvas.axes[1].cla()

