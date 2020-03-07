#from experiment import Experimento
import serial
from threading import Thread, Event, Lock
import queue
import time

#exp = Experimento(500, 7, 'COM8')
listenerCOM9 = serial.Serial('COM9', timeout=3)
listenerCOM11 = serial.Serial('COM11')
t0 = time.time()
data = []
celdaQ = queue.Queue()
distQ = queue.Queue()
dataEvent = Event()
dataReady = Event()
stop_threads = False


def celdaListener():
    global stop_threads
    while True:
        if stop_threads:
            break
        
        celda = listenerCOM9.readline()
        if not (celda == b""):
            celda = celda.decode('ascii').strip()[8:13]
            celdaQ.put(celda)
            dataEvent.set()

        


def arduinoListener():
    global stop_threads
    while True:
        if stop_threads:
            break        
        dataEvent.wait(1.0)
        if (dataEvent.isSet() and not celdaQ.empty()):
            listenerCOM11.write(b'<SEND>\n')
            answer = listenerCOM11.readline().decode('ascii').strip()
            print(answer)
            if (answer == "-1"):
                stop_threads = True
                dataEvent.clear()
                print("Experimento terminado")
                break
            else:    
                distQ.put(answer)
                dataEvent.clear()
                dataReady.set()



def dataWriter():
    global stop_threads
    while True:
        if stop_threads:
            break
        dataReady.wait(1.0)
        
        if (dataReady.isSet() and not (celdaQ.empty() and distQ.empty())):
            t1 = time.time()
            #timestamp = time.strftime('%H:%M:%S', time.gmtime(time.time()-t0))
            timestamp = time.time() - t0
            dataReady.clear()
            print(celdaQ.get(), distQ.get(), timestamp)



t1 = Thread(target=celdaListener)
t2 = Thread(target=arduinoListener)
t3 = Thread(target=dataWriter)
t1.start()
t2.start()
t3.start()

# time.sleep(20)
# stop_threads = True
