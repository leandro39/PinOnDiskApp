from math import pi
import serial
import sys
import time
import csv
from threading import Thread, Event, Lock

class Experimento:
    def __init__(self, dist, radio, carga, puertoCelda, puertoArduino):
        self._distancia = dist
        self._radio = radio
        self._vueltasTarget = int(dist/(2*pi*radio))
        self._cargaExperimento = carga
        self._puertoCelda = puertoCelda
        self._puertoArduino = puertoArduino
        self._serialArduino = serial.Serial()
        self._serialCelda = serial.Serial()
        self.isConnected = False
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

    def getPuerto(self):
        return (self._puertoCelda, self._puertoArduino)
        
    def empezar(self):
        try:
            self._serialCelda.baudrate = 9600
            self._serialCelda.port = self._puertoCelda
            self._serialCelda.timeout = None
            self._serialCelda.open()

            if not (self._serialCelda.is_open):
                raise Exception('Error en puerto serial de celda de arga')
            if not (self.isConnected):
                raise Exception('Error en puerto serial de controlador')

            #Init variables de experimento
            self.data = []
            self._celdaQ = queue.Queue()
            self._distQ = queue.Queue()
            self._dataEvent = Event()
            self._dataReady = Event()

            self._serialArduino.write(b'<STAR,{radio},{vueltasTarget}>'.format(radio=self._radio, vueltasTarget = self._vueltasTarget))
            
            if not (self._serialArduino.readline().decode('ascii').strip() == "0"):
                raise Exception('Error en comunicacion con controlador')
            self.isRunning = True
            self._t0 = time.time()  #Timestamp de comienzo de experimento
            
            #Listeners de puerto serial y producers de queues
            t1 = Thread(target=self.__celdaListener)
            t2 = Thread(target=self.__controllerListener)
            #Consumer de queues y almacenador
            t3 = Thread(target=self.__dataWriter)
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
        if (self.isRunning):
            try:
                self._serialArduino.write(b'<STOP>')
                if (self._serialArduino.readline().decode('ascii').strip() == "1"):
                    self._stopThreads = True
                    self.isRunning = False



            except Exception as e:
                print(type (e))
                print(e.args)
                print(e)

    def conectar(self):
        try:
            self._serialArduino.baudrate = 9600 
            self._serialArduino.port = self._puertoArduino
            self._serialArduino.timeout = timeout = None
            self._serialArduino.open()

            if (self._serialArduino.is_open): 
                self._serialArduino.write(b'<CONN>\n')
                read = self._serialArduino.readline().decode('ascii').strip()

                if (read == '0'):
                    self.isConnected = True
                    return True
                else:
                    return False

        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)

    def desconectar(self):
        try:
            self._serialArduino.write(b'<DCON>\n')
            self._serialArduino.close()
        except Exception as e:
            print("Exception occurred " + e.args[0])    
        
    def __celdaListener(self):
        while True:
            if self._stopThreads:
                break
            celda = self._serialCelda.readline()
            if not (celda == b""):
                celda = celda.decode('ascii').strip()[8:13]  #Parse poco prolijo para test
                self._celdaQ.put(celda)  
                self._dataEvent.set()
            

    def __controllerListener(self):
        while True:
            if self._stopThreads:
                break
            self._dataEvent.wait(1.5)
            if (self._dataEvent.isSet() and not self._celdaQ.empty()):
                self._serialArduino.write(b'<SEND>\n')
                answer = self._serialArduino.readline().decode('ascii').strip()
                if (answer == "-1"):
                    self._stopThreads = True
                    dataEvent.clear()
                    print("Experimento terminado")
                    break
                else:
                    vueltas = float(answer)
                    self._distQ.put(vueltas*2*pi*self._radio)
                    self._dataEvent.clear()
                    self._dataReady.set()
                              
    
    def __dataWriter(self):
        while True:
            if self._stopThreads:   
                break     
            self._dataReady.wait(1.5)
            if (self._dataReady.isSet() and not (self._celdaQ.empty() and self._distQ.empty())):
                t1 = time.time()
                timestamp = time.time()-self._t0
                self._dataReady.clear()
                self.data.append((self._celdaQ.get(),self._distQ.get(),timestamp))
                   
        if not ((len(self.data) == 0) or (len(self._path) == 0)):
            self.__storeData() 

    def __storeData(self):
        with open(self._path, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['carga','distancia', 'tiempo'])
            for row in self.data:
                csv_out.writerow(row)


        
