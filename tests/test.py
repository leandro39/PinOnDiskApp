import argparse

parser = argparse.ArgumentParser(description="Simula stream de datos de celda de carga por puerto serial")
parser.add_argument('--port', action='store', help='Puerto al cual va a streamear', required=True, dest='port')
args = parser.parse_args()
print(type(args.port))
