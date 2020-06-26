import csv
import queue
import sys
import time
from math import pi
from threading import Event, Lock, Thread
import serial
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

class Ensayo(QtCore.QObject):
    
    experimentEnd = QtCore.pyqtSignal()

    def __init__(self, name, dist, radio, carga, puertoCelda, serialArduino, TEST_ENV, parent=None):
        super(self.__class__, self).__init__(parent)
        
        self._name = name
        self._distancia = int(dist)
        self._radio = int(radio)
        self._vueltasTarget = int((self._distancia*1000)/(2*pi*self._radio))
        self._cargaExperimento = int(carga)
        self._puertoCelda = puertoCelda
        self._serialArduino = serialArduino
        self._serialCelda = serial.Serial()
        self.isRunning = False
        self._stopThreads = False
        self.TEST_ENV = TEST_ENV
        

    def getDistancia(self):
        return self._distancia
    
    def setSavePath(self, path):
        self._path = path
    
    def getRadio(self):
        return self._radio

    def getVueltasTarget(self):
        return self._vueltasTarget
        
    def empezar(self):
        try:
            if not (self._serialCelda.is_open):
                self._serialCelda.baudrate = 9600
                self._serialCelda.port = self._puertoCelda
                self._serialCelda.timeout = 1.0
                self._serialCelda.open()

            if not (self._serialCelda.is_open):
                raise Exception('Error en puerto serial de celda de carga')

            #Init variables de experimento
            self.data = []
            self.tempHumedad = (0,0)
            self.plotterQ = queue.Queue()
            self.progressBarQ = queue.Queue()
            self._celdaQ = queue.Queue()
            self._distQ = queue.Queue()
            self._tyhQ = queue.Queue()
            self._dataEvent = Event()
            self._dataReady = Event()
            self._stopExperiment = False
            self._lock = Lock()
            
            #Empty buffers
            self._serialArduino.reset_input_buffer()
            self._serialArduino.reset_output_buffer()
            
            if (self.TEST_ENV):
                self._serialArduino.write(('<STAR,{radio},{vueltasTarget}>\n'.format(radio=self._radio, vueltasTarget=self._vueltasTarget)).encode())
            else:
                self._serialArduino.write(('<STAR,{radio},{vueltasTarget}>'.format(radio=self._radio, vueltasTarget=self._vueltasTarget)).encode())
            
            response = self._serialArduino.readline().decode('ascii').strip()
            print(response)
            
            if not (response == "0"):
                raise Exception('Error en comunicacion con controlador')
            self.isRunning = True
            self._t0 = time.time()  #Timestamp de comienzo de experimento
            
            #Listeners de puerto serial y producers de queues
            self.t1 = Thread(target=self.__celdaListener, daemon=True)
            self.t2 = Thread(target=self.__controllerListener, daemon=True)
            self.t6 = Thread(target=self.__requestTemperatureAndHumidity, daemon=True)
            
            #Consumer de queues y data writer
            self.t3 = Thread(target=self.__dataWriter, daemon=True)
            self.t6.start()
            self.t1.start()
            self.t2.start()
            self.t3.start()

        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()

    def pausar(self):
        pass

    def detener(self):
        self._stopExperiment = True #Raise flag to stop experiment in a clean way
    
    @staticmethod
    def test(port, TEST_ENV):
        try:
            if (TEST_ENV):
                port.write(b'<TEST>\n')
            else:    
                port.write(b'<TEST>')
            
            answer = port.readline().decode('ascii').strip()
            print(answer)
            if (answer == '0'):
                return 1
            
            elif (answer == '-1'):
                return 0    
            else:
                raise Exception('Error de comunicacion')
            
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()
    
    
    def __stopExperiment(self):
        try:
            if (self.isRunning):
                self._lock.acquire()
                if (self.TEST_ENV):
                    self._serialArduino.write(b'<STOP>\n')
                else:
                    self._serialArduino.write(b'<STOP>')
                answer = self._serialArduino.readline().decode('ascii').strip()
                print(answer)
                self._lock.release()
                if (answer == "-1"):
                    print(answer)
                    self._lock.acquire()
                    self._stopThreads = True
                    self._lock.release()
                    self.isRunning = False
        
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()
  
    def __celdaListener(self):
        try:
            while True:
                if self._stopThreads:
                    self._serialCelda.close()
                    break
                celda = self._serialCelda.readline()
                if not (celda == b""):
                    if (self.TEST_ENV):
                        celda = celda.decode('ascii').strip()[8:13]
                    else:
                        celda = celda.decode('ascii').strip()[4:9]  #Parse poco prolijo para test
                    print('Celda: ' + celda)
                    self._celdaQ.put(celda)  
                    self._dataEvent.set()
        
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()

    def __controllerListener(self):
        try:
            while True:
                if self._stopThreads:
                    self.experimentEnd.emit()
                    break
                self._dataEvent.wait(1.5)
                if (self._dataEvent.isSet() and not self._celdaQ.empty()):
                    self._lock.acquire()
                    if (self.TEST_ENV):
                        self._serialArduino.write(b'<SEND>\n')
                    else:
                        self._serialArduino.write(b'<SEND>')
                    answer = self._serialArduino.readline().decode('ascii').strip()
                    print('Arduino: ' + answer)
                    self._lock.release()
                    if (answer == "-1"):
                        self._stopThreads = True
                        self._dataEvent.clear()
                        self.isRunning = False
                        self.experimentEnd.emit()
                        break
                    else:
                        vueltas = float(answer)
                        self.progressBarQ.put(vueltas)
                        self._distQ.put("{:10.2f}".format(vueltas*2*pi*self._radio*0.001).strip())
                        self._dataEvent.clear()
                        self._dataReady.set()
                    
                    if (self._stopExperiment == True):
                        self.__stopExperiment()
        
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()

    def __dataWriter(self):
        try:
            # Create output file
            self._out = open(self._path + '\\' + self._name + '.txt', 'w', newline='')
            csv_out = csv.writer(self._out, delimiter='\t')
            
            # Write metada

            localtime = time.localtime()
            today = time.strftime('%d/%m/%y', localtime)
            now = time.strftime('%H:%M:%S', localtime)
            csv_out.writerow(['Fecha', today, now])
            csv_out.writerow(['Operador', 'Test'])
            csv_out.writerow(['Probeta', 'Test'])
            csv_out.writerow(['Material', 'Test'])
            csv_out.writerow(['Dureza', 'Test'])
            csv_out.writerow(['Tratamiento', 'Test'])
            csv_out.writerow(['Radio', self._radio])
            csv_out.writerow(['Distancia', self._distancia])
            csv_out.writerow(['Carga', self._cargaExperimento])
            csv_out.writerow(['Bolilla', 'Test'])
            csv_out.writerow(['Diametro bolilla', 'Test'])
            csv_out.writerow(['fuerza[kg]','distancia[m]', 'tiempo[s]', 'temperatura[°C]', 'humedad[%]'])
            self._out.flush()

            while True:
                try:
                    if self._stopThreads:
                        self.plotterQ.put('end')   
                        break     
                    self._dataReady.wait(1.5)
                    if (self._dataReady.isSet() and not (self._celdaQ.empty() and self._distQ.empty())):
                        timestamp = time.time()-self._t0
                        self._dataReady.clear()
                        celda = self._celdaQ.get(timeout=1.5)
                        distancia = self._distQ.get(timeout=1.5)
                        self.plotterQ.put((celda, distancia))
                        if(self._tyhQ.empty()):
                            csv_out.writerow([celda, distancia,'{:10.2f}'.format(timestamp).strip(),self.tempHumedad[0], self.tempHumedad[1]])
                        else:
                            self.tempHumedad = self._tyhQ.get()
                            csv_out.writerow([self._celdaQ.get(),self._distQ.get(),"{:10.2f}".format(timestamp).strip(),self.tempHumedad[0], self.tempHumedad[1]])
                        self._out.flush()
                except Exception as e:
                    if (type(e) == queue.Empty):
                        pass
                    else:
                        msgBox = QMessageBox()
                        msgBox.setIcon(QMessageBox.Critical)
                        msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
                        msgBox.setWindowTitle('Error')
                        msgBox.exec_()
                    
        finally:
            self._out.flush()
            self._out.close()

    
    def __requestTemperatureAndHumidity(self):
        try:
            timer = 60
            while True:
                if self._stopThreads:
                    
                    break
                if (timer == 60):
                    self._lock.acquire()
                    if (self.TEST_ENV):
                        self._serialArduino.write(b'<TMHM>\n')
                    else:
                        self._serialArduino.write(b'<TMHM>')
                    
                    humedad = self._serialArduino.readline().decode('ascii').strip()
                    temperatura = self._serialArduino.readline().decode('ascii').strip()
                    self._lock.release()
                    self._tyhQ.put((temperatura, humedad))
                    print('Temperatura: ' + temperatura)
                    print('Humedad: ' + humedad)
                    timer = 0
                time.sleep(1)
                timer += 1
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText('Error: ' + str(type(e)) + '\n'  + str(e))
            msgBox.setWindowTitle('Error')
            msgBox.exec_()

