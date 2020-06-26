import serial
import argparse
import time
import csv
from threading import Thread

def main():
    with open('celda.csv') as out:
        ser = serial.Serial(port)
        csv_reader = csv.reader(out)
        for row in csv_reader:
            time.sleep(0.4)
            ser.write((row[0] + "\n").encode())

parser = argparse.ArgumentParser(description="Simula stream de datos de celda de carga por puerto serial")
parser.add_argument('--port', action='store', help='Puerto al cual va a streamear', required=True, dest='port')
port = parser.parse_args().port
print(type(port))
t1 = Thread(target=main, daemon=True)
t1.start()
while True:
    time.sleep(0.1)
t1.join()
