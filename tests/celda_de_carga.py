#Simular señal de celda de carga que envia lectura cada .4 segundos 

import serial
from random import random
import time
import csv

data = []
with open('..\\data\\celda_sim.csv') as out:
    csv_reader = csv.reader(out)
    data = list(csv_reader)

ser = serial.Serial('COM8')
i = 0
while True:
    ser.write((data[i][0] + "\n").encode())
    i += 1
    time.sleep(0.4)

