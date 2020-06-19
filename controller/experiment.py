import csv
import queue
import sys
import time
from math import pi
from threading import Event, Lock, Thread
import serial
from PyQt5 import QtCore

TEST_ENV = True

class Ensayo(QtCore.QObject):
    
    experimentEnd = QtCore.pyqtSignal()

    def __init__(self, name, dist, radio, carga, puertoCelda, serialArduino, parent=None):
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
            self._lock = Lock()
            
            #Empty buffers
            self._serialArduino.flushInput()
            self._serialArduino.flushOutput()
            #Added \n, delete later
            if (TEST_ENV):
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
            t1 = Thread(target=self.__celdaListener, daemon=True)
            t2 = Thread(target=self.__controllerListener, daemon=True)
            t6 = Thread(target=self.__requestTemperatureAndHumidity, daemon=True)
            #Consumer de queues y almacenador
            t3 = Thread(target=self.__dataWriter, daemon=True)
            t6.start()
            t1.start()
            t2.start()
            t3.start()

        except Exception as e:
            print(type (e))
            print(e.args)
            print(e)

    def pausar(self):
        pass

    def detener(self):
        t5 = Thread(target=self.__stopExperiment, daemon=True)
        t5.start()
    
    def test(self):
        t = Thread(target=self.__test, daemon=True)
        t.start()
    
    def __test(self):
        try:
            self._lock.acquire()
            if (TEST_ENV):
                self._serialArduino.write('<TEST>').encode()
            else:    
                self._serialArduino.write('<TEST>\n').encode()
            answer = self._serialArduino.readline().decode('ascii').strip()
            self._lock.release()
            if (answer == '0'):
                self.isRunning = True
                pass
            else:
                raise Exception('Error de comunicacion')
            
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)
    
    #ADDED \N REMOVE LATER
    def __stopExperiment(self):
        if (self.isRunning):
            self._lock.acquire()
            if (TEST_ENV):
                self._serialArduino.write(b'<STOP>\n')
            else:
                self._serialArduino.write(b'<STOP>')
            answer = self._serialArduino.readline().decode('ascii').strip()
            self._lock.release()
            
            if (answer == "-1"):
                print(answer)
                self._lock.acquire()
                self._stopThreads = True
                self._lock.release()
                self.isRunning = False
  
    def __celdaListener(self):
        while True:
            if self._stopThreads:
                self._serialCelda.close()
                break
            celda = self._serialCelda.readline()
            if not (celda == b""):
                if (TEST_ENV):
                    celda = celda.decode('ascii').strip()[8:13]
                else:
                    celda = celda.decode('ascii').strip()[4:9]  #Parse poco prolijo para test
                self._celdaQ.put(celda)  
                self._dataEvent.set()
            
    def __controllerListener(self):
        while True:
            if self._stopThreads:
                self.experimentEnd.emit()
                break
            self._dataEvent.wait(1.5)
            if (self._dataEvent.isSet() and not self._celdaQ.empty()):
                self._lock.acquire()
                if (TEST_ENV):
                    self._serialArduino.write(b'<SEND>\n')
                else:
                    self._serialArduino.write(b'<SEND>')
                answer = self._serialArduino.readline().decode('ascii').strip()
                print(answer)
                self._lock.release()
                if (answer == "1"):
                    self._stopThreads = True
                    self._dataEvent.clear()
                    self.isRunning = False
                    self.experimentEnd.emit()
                    print("Experimento terminado")
                    break
                else:
                    vueltas = float(answer)
                    self.progressBarQ.put(vueltas)
                    self._distQ.put("{:10.2f}".format(vueltas*2*pi*self._radio*0.001).strip())
                    self._dataEvent.clear()
                    self._dataReady.set()
                              
    def __dataWriter(self):
        try:
            self._out = open(self._path + '\\' + self._name + '.txt', 'w', newline='')
            csv_out = csv.writer(self._out, delimiter='\t')
            
            #Write metada
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
                if self._stopThreads:
                    self.plotterQ.put('end')   
                    break     
                self._dataReady.wait(1.5)
                if (self._dataReady.isSet() and not (self._celdaQ.empty() and self._distQ.empty())):
                    timestamp = time.time()-self._t0
                    self._dataReady.clear()
                    celda = self._celdaQ.get()
                    distancia = self._distQ.get()
                    self.plotterQ.put((celda, distancia))
                    if(self._tyhQ.empty()):
                        csv_out.writerow([celda, distancia,'{:10.2f}'.format(timestamp).strip(),self.tempHumedad[0], self.tempHumedad[1]])
                    else:
                        self.tempHumedad = self._tyhQ.get()
                        csv_out.writerow([self._celdaQ.get(),self._distQ.get(),"{:10.2f}".format(timestamp).strip(),self.tempHumedad[0], self.tempHumedad[1]])
                    self._out.flush()
        
        finally:
            self._out.close()

    
    def __requestTemperatureAndHumidity(self):
        while True:
            if self._stopThreads:
                break
            self._lock.acquire()
            self._serialArduino.write(b'<TMHM>\n')
            humedad = self._serialArduino.readline().decode('ascii').strip()
            temperatura = self._serialArduino.readline().decode('ascii').strip()
            self._lock.release()
            self._tyhQ.put((temperatura, humedad))

            time.sleep(60)

    
    
    #legacy
    def __storeData(self):
        with open(self._path + '\\' + self._name + '.csv', 'w') as out:
            csv_out = csv.writer(out)
            #Write metada
            csv_out.writerow(['#Nombre del experimento: {name}'.format(name=self._name)])
            today = time.strftime('%d/%m/%y - %H:%M:%S', time.gmtime(self._t0))
            csv_out.writerow(['#Fecha del experimento: {time}'.format(time=today)])

            #Write data 
            csv_out.writerow(['carga','distancia', 'tiempo'])
            for row in self.data:
                csv_out.writerow(row)


#ensayo = Ensayo("Experiment", "500", "5", "5", "COM8", serial.Serial())
