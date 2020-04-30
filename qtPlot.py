from PyQt5 import QtWidgets, uic
import pyqtgraph as pg


class CPlot(QtWidgets.QMainWindow):
    def __init__(self, name, background):
        super(CPlot, self).__init__()

        self.background = background

        self.setWindowTitle(name)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.setBackground(background)

        self.setGeometry(0, 0, 1000, 800)

    def updatePlot(self, x, y, clear=True, pen="b"):
        if clear:
            self.graphWidget.clear()

        self.graphWidget.plot(x, y, pen=pen)
        self.graphWidget.showGrid(x=True, y=True)
