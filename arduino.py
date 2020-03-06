import serial
import time

ser = serial.Serial('COM10')
dist = 0
while True:
    if (dist == 10):
        ser.write(b"-1\n")
        print('finished')
        break
    if (ser.inWaiting()>0):
        dataStream = ser.readline().decode('ascii').strip()
        if (dataStream == '<SEND>'):
            ser.write((str(dist) + '\n').encode())
            dist += 1    