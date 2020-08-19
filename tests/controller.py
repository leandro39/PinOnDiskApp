import serial
import argparse
import time
from threading import Thread, Event, Lock
import random

# Argparser
parser = argparse.ArgumentParser(description="Simula controlador de maquina de ensayos pin on disk")
parser.add_argument('--port', action='store', help='Puerto al cual va a streamear', required=True, dest='port')
port = parser.parse_args().port

ser = serial.Serial(port, timeout=None ) # Puerto al que escucha el controlador
ser.write(('Controlador escuchando en puerto ' + port + '\n').encode())
exitEvent = Event()
lock = Lock()
commands = ['SEND', 'STAR', 'CONN', 'DCON', 'TMHM', 'TEST', 'PAUS', 'STOP', 'SPEE']
radios = [5, 6, 7]
vueltasT = 0.0
velocidades = [10.0,12.5,13.2,15.3,9.6,8.6,7.9]
#Comandos
command = ''
radio = 0
vueltas = 0

#Estado default
state = 'WAIT'
isConnected = False
isRunning = False
test = False

def listener():
    global command, radio, vueltas
    while True:
        read = ser.readline().decode().strip()
        if (read[0] == '<' and read[-1] == '>' and read[1:5] in commands):
            if (len(read) == 6):      #Comando regular, sin argumentos
                lock.acquire()
                command = read[1:5]
                lock.release()
                print(command)
            elif (read[1:5] == 'STAR'):
                lock.acquire()
                command = read[1:5]
                radio = int(read.split(',')[1])
                vueltas = int(read.split(',')[2].split('>')[0])
                lock.release()
                print(f'<STAR,{radio},{vueltas}>')
        read = ''    

def resetVars():
    global vueltasT
    vueltasT = 0

def getTemp():
    ser.write('55\n'.encode())
    ser.write('25.5\n'.encode())

def main():
    while True:
        global state, command, vueltasT, isRunning, isConnected, test
        if (state == 'STAR'):
            if (not isRunning):
                resetVars()
                isRunning = True
            if (vueltasT >= vueltas):
                ser.write('-1\n'.encode())
                isRunning = False
                state = 'WAIT'
            if (command == 'PAUS'):
                ser.write('0\n'.encode())
                state = 'PAUS'
            elif (command == 'STOP'):
                state = 'STOP'
            elif (command == 'TMHM'):
                getTemp()
                command = ''
            elif (command == 'SEND'):
                ser.write((str(vueltasT) + '\n').encode())
                command = ''
            elif (command == 'SPEE'):
                ser.write((str(random.choice(velocidades)) + '\n').encode())
                command = ''
            vueltasT += 1.0
        
        elif (state == 'PAUS'):
            if (command == 'STAR'):
                state = 'STAR'
                ser.write('0\n'.encode())
            
            elif (command == 'STOP'):
                state = 'STOP'
        
        elif (state == 'STOP'):
            print('Detenido')
            ser.write('-1\n'.encode())
            isRunning = False
            state = 'WAIT'
        
        elif (state == 'CONN'):
            print('Conectado')
            ser.write('0\n'.encode())
            isConnected = True
            state = 'WAIT'
        
        elif (state == 'DCON'):
            print('Desconectado')
            ser.write('0\n'.encode())
            isConnected = False
            resetVars()
            state = 'WAIT'
        
        elif (state == 'WAIT'):
            
            if (command == 'CONN' and isConnected == False):
                state = 'CONN'
                command = ''
            
            elif (command == 'STAR' and isConnected and (radio in radios) and vueltas > 0):
                state = 'STAR'
                print('Empezando experimento')
                ser.write('0\n'.encode())
                command = ''
            
            elif (command == 'TEST' and isConnected):
                state = 'TEST'
                command = ''
            
            elif (command == 'STOP' and isConnected):
                state = 'STOP'
                command = ''
            
            elif(command == 'DCON' and isConnected):
                state = 'DCON'
                command = ''

        elif (state == 'TEST'):
            test = not test
            if (test):
                print('Comenzando test')
                ser.write('0\n'.encode())
                state = 'WAIT'
            else:
                print('Finalizando test')
                ser.write('-1\n'.encode())
                state = 'WAIT'
        
        time.sleep(0.1)

t1 = Thread(target=listener, daemon=True)
t2 = Thread(target=main, daemon=True)
t1.start()
t2.start()


while True:
    time.sleep(0.1)

t1.join()
t2.join()
print('Cerrando')