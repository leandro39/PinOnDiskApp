import serial
import time

ser = serial.Serial('COM11')
dataArray = []
while True:
    ser.write(('<SEND>'+'\n').encode())
    data = ser.readline().decode('ascii').strip()
    dataArray.append(data)
    print(dataArray)
    time.sleep(1)
