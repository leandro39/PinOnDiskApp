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
import numpy as np

ICON_RED_LED = '.\\views\\icons\\led-red-on.png'
ICON_GREEN_LED = '.\\views\\icons\\green-led-on.png'

#Load configs
with open('configs.json', 'r') as f:
    configs = json.loads(f.read())
    TEST_ENV = configs['TEST_ENV']
    BUFFER_SIZE = configs['BUFFER_SIZE']
    COMPORT_CELDA = configs['COMPORT_CELDA']

class PinOnDiskApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        #Create main window
        self.ui = Ui_MainWindow()
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

        if not self.isConnected:
            self.isConnected = serial_tools.try_connect(self.ser, self.ui.portCombo.currentText())
        else:
            self.isConnected = serial_tools.close_serial(self.ser) 
        
        if self.isConnected:
            self.ui.groupBox.setEnabled(True)
            self.ui.testBtn.setEnabled(True)
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
        self.ensayo = Ensayo(self.ui.experimentNameInput.text(), self.ui.distanciaInput.text(), self.ui.radioCombo.currentText(), self.ui.cargaInput.text(), COMPORT_CELDA, self.ser, TEST_ENV)
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
        self.ui.testBtn.setEnabled(False)
        self.ensayo.empezar()
        self.ensayo.experimentEnd.connect(self.onExperimentEnd)
        
        # Plotter setup
        self.plot = Plotter(ensayo = self.ensayo, test = self.ui.experimentNameInput.text(), r = self.ui.radioCombo.currentText(), d = self.ui.distanciaInput.text(), c = self.ui.cargaInput.text())
        self.plot.show()

        # Progress bar setup
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
        testing = Ensayo.test(self.ser, TEST_ENV)
        if (testing):
            # Test started
            self.ui.testBtn.setText('Detener prueba')
        else:
            self.ui.testBtn.setText('Prueba')
        

    def onVueltasChanged(self, value):
        self.ui.progressBar.setValue(int(value))
        self.ui.progressLabel.setText('{currVueltas} vueltas de {targetVueltas}'.format(currVueltas=int(value), targetVueltas=int(self.ensayo.getVueltasTarget())))

    def onExperimentEnd(self):
         #Rutina de limpieza para volver a empezar nuevo experimento

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
        self.ui.testBtn.setEnabled(True)
        self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        self.ui.progressLabel.setText('{targetVueltas} vueltas de {targetVueltas}'.format(targetVueltas=int(self.ensayo.getVueltasTarget())))
        self.progress.killThread = True
        self.ser.flushInput()
        self.ser.flushOutput()
        
        
        # ONLY DEBUG
        # time.sleep(6)
        # print(f'Celda thread is alive: {self.ensayo.t1.is_alive()}')
        # print(f'Controller thread is alive: {self.ensayo.t2.is_alive()}')
        # print(f'Data writer thread: {self.ensayo.t3.is_alive()}')
        # print(f'Temp y humedad thread is alive : {self.ensayo.t6.is_alive()}')
        # print(f'Plotter thread is alive: {self.plot.t.is_alive()}')
        # print(f'Progress bar updater thread is alive: {self.progress.isRunning()}')


class ProgressBarUpdater(QtCore.QThread):
    currentVueltas = QtCore.pyqtSignal(float)
    
    def __init__(self,Q, parent=None):
        super(QtCore.QThread, self).__init__()
        self.vueltasQueue = Q
        self.killThread = False
    
    def run(self):
        while True:
            try:
                if (self.killThread):
                    break
                vueltas = self.vueltasQueue.get(timeout=1.5)
                self.currentVueltas.emit(int(vueltas))
            except queue.Empty:
                pass

class Plotter(QtWidgets.QDialog):
    def __init__(self, r, d, c, ensayo = None, test = 'Experimento', parent=None):
        super(Plotter, self).__init__(parent)
        self.setWindowFlags((self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint) | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowTitle("Ensayo")
        self.setStyleSheet("QWidget { background-color: #ffffff; }")
        self.canvas = FigureCanvas(Figure(figsize=(10,6)))
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setVisible(True)
        self._dynamic_ax = self.canvas.figure.subplots()
        self._dynamic_ax.grid()
        self._dynamic_ax.set_title('Ensayo: {name} - Radio: {radio}mm - Distancia: {dist}m - Carga: {carga}N'.format(name=test, radio=r, dist=d, carga=c), pad=15)
        self._dynamic_ax.set_xlabel('Distancia [m]', labelpad=15)
        self._dynamic_ax.set_ylabel('Fuerza de rozamiento [kg]', labelpad=20)
        self._dynamic_ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ensayo = ensayo
        self.t = Thread(target=self._update_canvas, daemon=True)
        self.t.start()

    def _update_canvas(self):
        
        # f = open('data\\test1.csv', 'r')
        # cs = csv.reader(f)
        # lines = next(f).split(',')
        
        # self._dynamic_ax.plot(float(lines[1]), float(lines[0]))
        # self._dynamic_ax.figure.canvas.draw()
        # line = self._dynamic_ax.get_lines()[0]
        # for row in cs:
        #     line.set_xdata(np.append(line.get_xdata(),(float(row[1]))))
        #     line.set_ydata(np.append(line.get_ydata(),(float(row[0]))))
        #     self._dynamic_ax.set_ylim(0,np.max(line.get_ydata()))
        #     self._dynamic_ax.set_xlim(0,np.max(line.get_xdata()))
        #     self._dynamic_ax.figure.canvas.draw()
        #     time.sleep(0.4)
        # f.close()

        
        data = self.ensayo.plotterQ.get()
        self._dynamic_ax.plot(float(data[1]), float(data[0]))
        self._dynamic_ax.figure.canvas.draw()
        line = self._dynamic_ax.get_lines()[0]
        while True:
            try:     
                data = self.ensayo.plotterQ.get(timeout=1.5)
                if data == 'end':
                    break
                else:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    if (line.get_xdata().size >= BUFFER_SIZE):

                        # Left shift array to move x axis once BUFFER_SIZE is reached
                        line.set_xdata(np.append(xdata, float(data[1]))[1:])
                        line.set_ydata(np.append(ydata, float(data[0]))[1:])
                    else:
                        line.set_xdata(np.append(xdata, float(data[1])))
                        line.set_ydata(np.append(ydata, float(data[0])))
                    
                    self._dynamic_ax.set_ylim(np.min(line.get_ydata())*0.9,np.max(line.get_ydata())*1.1)
                    self._dynamic_ax.set_xlim(np.min(line.get_xdata()),np.max(line.get_xdata()))
                    self._dynamic_ax.figure.canvas.draw()
        
            except queue.Empty:
                pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = PinOnDiskApp()
    win.show()
    sys.exit(app.exec_())
