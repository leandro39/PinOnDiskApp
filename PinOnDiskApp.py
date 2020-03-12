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
            print(self.configs['COMPORT_CELDA'])

        #Setup the ui
        self.ui.setupUi(self)
        self.serial_ports = serial_tools.get_serial_ports()
        self.ui.portCombo.addItems(self.serial_ports)
        self.ui.radioCombo.addItems(['5','6','7'])
        self.ui.labelNotConnected.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        self.ui.labelNotConnected.show()
        self.ui.labelConnected.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        self.ui.labelConnected.hide()
        self.validator = QtGui.QIntValidator()
        self.validator.setBottom(0)
        self.ui.distanciaInput.setValidator(self.validator)
        self.ui.cargaInput.setValidator(self.validator)

        #Flow control variables
        self.isConnected = False
        self.ser = serial.Serial()
        self.lock = Lock()
                
        #Setup logic and signals
        self.ui.conectarBtn.clicked.connect(self.conectarBtn_ClickedEvent)
        self.ui.pathBrowseBtn.clicked.connect(self.pathBrowseBtn_ClickedEvent)
        self.ui.distanciaInput.textChanged.connect(self.onTextChanged)
        self.ui.experimentNameInput.textChanged.connect(self.onTextChanged)
        self.ui.pathInput.textChanged.connect(self.onTextChanged)
        self.ui.cargaInput.textChanged.connect(self.onTextChanged)
        self.ui.startBtn.clicked.connect(self.startBtn_ClickedEvent)

    #Button events
    def conectarBtn_ClickedEvent(self):
        if not self.isConnected:
            self.isConnected = serial_tools.try_connect(self.ser, self.ui.portCombo.currentText(), self.lock)
        else:
            self.isConnected = serial_tools.close_serial(self.ser) 
        
        if self.isConnected:
            self.ui.groupBox.setEnabled(True)
            self.ui.labelNotConnected.hide()
            self.ui.labelConnected.show()
            self.ui.conectarBtn.setText("Desconectar")

        else:
            self.ui.groupBox.setEnabled(False)
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
        self.ensayo.empezar()
        

    def pathParser(self):
        return self.ui.pathInput.text().replace('/', '\\')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = PinOnDiskApp()
    win.show()
    sys.exit(app.exec_())
