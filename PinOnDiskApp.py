import sys, os
from threading import Lock, Thread, Event
import serial
from math import pi
import json
import csv
import queue
import time
from PyQt5 import QtCore, QtGui, QtWidgets

from views.PinOnDiskMain import Ui_MainWindow
from controller import serial_tools
from controller.experiment import Ensayo

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.figure import Figure
import random
import numpy as np

ICON_RED_LED = '.\\views\\icons\\led-red-on.png'
ICON_GREEN_LED = '.\\views\\icons\\green-led-on.png'

class PinOnDiskApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        #Create main window
        self.ui = Ui_MainWindow()

        #Load configs
        with open('configs.json', 'r') as f:
            self.configs = json.loads(f.read())

        self.dialogs = list()           
        #Setup the ui
        self.ui.setupUi(self)
        self.serial_ports = serial_tools.get_serial_ports()
        self.ui.portCombo.addItems(self.serial_ports)
        self.ui.radioCombo.addItems(['5','6','7'])
        self.ui.labelNotConnected.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.ui.labelNotConnected.show()
        self.ui.labelConnected.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.ui.labelConnected.hide()
        self.ui.progressLabel.setVisible(False)
        
        self.validator = QtGui.QIntValidator()
        self.validator.setBottom(0)
        self.ui.distanciaInput.setValidator(self.validator)
        self.ui.cargaInput.setValidator(self.validator)

        #Flow control variables
        self.isConnected = False
        self.ser = serial.Serial()
                
        #Setup logic and signals
        self.ui.conectarBtn.clicked.connect(self.conectarBtn_ClickedEvent)
        self.ui.pathBrowseBtn.clicked.connect(self.pathBrowseBtn_ClickedEvent)
        self.ui.distanciaInput.textChanged.connect(self.onTextChanged)
        self.ui.experimentNameInput.textChanged.connect(self.onTextChanged)
        self.ui.pathInput.textChanged.connect(self.onTextChanged)
        self.ui.cargaInput.textChanged.connect(self.onTextChanged)
        self.ui.startBtn.clicked.connect(self.startBtn_ClickedEvent)
        self.ui.stopBtn.clicked.connect(self.stopBtn_ClickedEvent)
        self.ui.testBtn.clicked.connect(self.testBtn_ClickedEvent)
        
    #Button events
    def conectarBtn_ClickedEvent(self):
        # plot = Plotter()
        # plot.show()
        if not self.isConnected:
            self.isConnected = serial_tools.try_connect(self.ser, self.ui.portCombo.currentText())
        else:
            self.isConnected = serial_tools.close_serial(self.ser) 
        
        if self.isConnected:
            self.ui.groupBox.setEnabled(True)
            self.ui.labelNotConnected.hide()
            self.ui.labelConnected.show()
            self.ui.conectarBtn.setText("Desconectar")

        else:
            self.ui.groupBox.setEnabled(False)
            self.ui.conectarBtn.setEnabled(True)
            self.ui.pauseBtn.setEnabled(False)
            self.ui.stopBtn.setEnabled(False)
            self.ui.testBtn.setEnabled(False)
            self.ui.startBtn.setEnabled(False)
            self.ui.labelNotConnected.show()
            self.ui.labelConnected.hide()
            self.ui.conectarBtn.setText("Conectar")
  
    def pathBrowseBtn_ClickedEvent(self):
        self.ui.pathInput.setText(str(QtWidgets.QFileDialog.getExistingDirectory(self, "Elija una carpeta en donde guardar los datos del experimento")))

    #Chequeo que los inputs no esten vacios antes de habilitar el ensayo
    def onTextChanged(self):
        self.ui.startBtn.setEnabled(bool(self.ui.experimentNameInput.text()) and bool(self.ui.pathInput.text()) and bool(self.ui.distanciaInput.text() and bool(self.ui.cargaInput.text())))
                
    def startBtn_ClickedEvent(self):
        #Creo nuevo ensayo
        self.ensayo = Ensayo(self.ui.experimentNameInput.text(), self.ui.distanciaInput.text(), self.ui.radioCombo.currentText(), self.ui.cargaInput.text(), self.configs['COMPORT_CELDA'], self.ser)
        self.ensayo.setSavePath(self.pathParser())
        self.ui.pauseBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        self.ui.startBtn.setEnabled(False)
        self.ui.experimentNameInput.setEnabled(False)
        self.ui.cargaInput.setEnabled(False)
        self.ui.radioCombo.setEnabled(False)
        self.ui.distanciaInput.setEnabled(False)
        self.ui.pathBrowseBtn.setEnabled(False)
        self.ui.conectarBtn.setEnabled(False)
        self.ui.portCombo.setEnabled(False)
        self.ensayo.empezar()
        self.ensayo.experimentEnd.connect(self.onExperimentEnd)
        self.ui.progressBar.reset()
        self.ui.progressBar.setMaximum(int(self.ensayo.getVueltasTarget()))
        self.progress = ProgressBarUpdater(self.ensayo.progressBarQ)
        self.progress.currentVueltas.connect(self.onVueltasChanged)
        self.ui.progressLabel.setVisible(True)
        self.progress.start()
    
    def stopBtn_ClickedEvent(self):
        confirm = QtWidgets.QMessageBox.question(self,'Detener ensayo', "¿Está seguro que desea detener el experimento?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            self.ensayo.detener()
            self.ui.startBtn.setEnabled(True)
            self.ui.pauseBtn.setEnabled(False)
            self.ui.stopBtn.setEnabled(False)

    def pathParser(self):
        return self.ui.pathInput.text().replace('/', '\\')

    def testBtn_ClickedEvent(self):
        text = self.ui.testBtn.text()
        if text == "Prueba":
            self.ensayo.test()
        else:
            self.ensayo.detener()

    def onVueltasChanged(self, value):
        self.ui.progressBar.setValue(int(value))
        self.ui.progressLabel.setText('{currVueltas} vueltas de {targetVueltas}'.format(currVueltas=int(value), targetVueltas=int(self.ensayo.getVueltasTarget())))

    def onExperimentEnd(self):
        print("hello from end event")
        self.ui.pauseBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(False)
        self.ui.startBtn.setEnabled(True)
        self.ui.experimentNameInput.setEnabled(True)
        self.ui.cargaInput.setEnabled(True)
        self.ui.radioCombo.setEnabled(True)
        self.ui.distanciaInput.setEnabled(True)
        self.ui.pathBrowseBtn.setEnabled(True)
        self.ui.conectarBtn.setEnabled(True)
        self.ui.portCombo.setEnabled(True)
        self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        self.ui.progressLabel.setText('{targetVueltas} vueltas de {targetVueltas}'.format(targetVueltas=int(self.ensayo.getVueltasTarget())))
        self.ui.progressBar.killThread = True
        #Rutina de limpieza para volver a empezar nuevo experimento
        #Agregar señal en start button y conectarla con este método
        #Emitir señal desde experiment.py
        

class ProgressBarUpdater(QtCore.QThread):
    currentVueltas = QtCore.pyqtSignal(float)
    killThread = False
    def __init__(self,Q, parent=None):
        super(QtCore.QThread, self).__init__()
        self.vueltasQueue = Q
    
    def run(self):
        while True:
            if (self.killThread):
                break
            vueltas = self.vueltasQueue.get()
            self.currentVueltas.emit(int(vueltas))
            

class Plotter(QtWidgets.QDialog):
    def __init__(self, ensayo = None, parent=None):
        super(Plotter, self).__init__(parent)
        self.setWindowFlags((self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint) | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowTitle("Ensayo")
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        self.canvas = FigureCanvas(Figure(figsize=(10,6)))
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setVisible(False)
        self._dynamic_ax = self.canvas.figure.subplots()
        self._dynamic_ax.grid()
        self._dynamic_ax.set_title('Ensayo: Agos genia', pad=15)
        self._dynamic_ax.set_xlabel('Distancia [m]', labelpad=15)
        self._dynamic_ax.set_ylabel('Fuerza de rozamiento [kg]', labelpad=20)
        self._dynamic_ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        t = Thread(target=self._update_canvas, daemon=True)
        t.start()

    def _update_canvas(self):
        
        f = open('data\\test1.csv', 'r')
        cs = csv.reader(f)
        lines = next(f).split(',')
        
        self._dynamic_ax.plot(float(lines[1]), float(lines[0]))
        self._dynamic_ax.figure.canvas.draw()
        line = self._dynamic_ax.get_lines()[0]
        for row in cs:
            line.set_xdata(np.append(line.get_xdata(),(float(row[1]))))
            line.set_ydata(np.append(line.get_ydata(),(float(row[0]))))
            self._dynamic_ax.set_ylim(0,np.max(line.get_ydata()))
            self._dynamic_ax.set_xlim(0,np.max(line.get_xdata()))
            self._dynamic_ax.figure.canvas.draw()
            time.sleep(0.4)
        f.close()
        
        
        # while True:
        #     data = self.ensayo.plotterQ.get()
        #     if data == 'end':
        #         break
        #     else:
        #         self._dynamic_ax.set
        #self._dynamic_ax.grid()
        #t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        #self._dynamic_ax.plot(t, np.sin(t + time.time()))
        #self._dynamic_ax.set_xlim(left=0)
        #self._dynamic_ax.figure.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = PinOnDiskApp()
    win.show()
    sys.exit(app.exec_())
