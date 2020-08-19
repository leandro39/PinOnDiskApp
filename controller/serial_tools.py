import serial.tools.list_ports 
import time
from controller import helper
import logconfig

logger = logconfig.configLogger('Serial tools')

def get_serial_ports():
    return sorted([port.device for port in serial.tools.list_ports.comports()])

def setup_port(ser, port):
    try:
       
        ser.baudrate = 9600
        ser.port = port
        ser.bytesize = serial.EIGHTBITS
        ser.stopbits = serial.STOPBITS_ONE
        ser.parity = serial.PARITY_NONE
        ser.timeout = 0.5
        
    except Exception as e:
        helper.show_error("Problema inicializando puerto " + port + ".\n\n"
                        "Exception:\n" + str(e))
        logger.exception('Error configurando el puerto seleccionado')

def open_serial(ser):
    try:
        ser.open()
        time.sleep(2)
        logger.debug('Conectado al puerto {}'.format(ser.port))
    except Exception as e:
        helper.show_error("No fue posible abrir el puerto " + ser.port + ".\n\n"
                            "Intente con otro puerto\n\n"
                            "Exception:\n" + str(e))
        logger.exception('Error abriendo el puerto seleccionado')
        
        pass

def close_serial(ser):
    try:
        if (ser.is_open): 
            ser.write(b'<DCON>\n')   
            ser.close()
            logger.debug('Desconectado del puerto {}'.format(ser.port))
            
    except Exception as e:
        helper.show_error("Error desconocido " + ser.port + ".\n\n"
                          "Exception:\n" + str(e) + "\n\n")
        logger.exception('Error cerrando el puerto seleccionado')

def try_connect(ser, port):
    try:
        setup_port(ser,port)
        open_serial(ser)
        
        if ser.is_open:
            ser.write(b'<CONN>\n')
            logger.debug('Intentando establecer conexion con el controlador')
            read = ser.readline().decode('ascii').strip()
            if (read == '0'):
                logger.debug('Controlador conectado')
                return True
            else:
                ser.close()
                helper.show_error("El controlador no responde" +"\n\n" "Intente con otro puerto y verifique que está conectado y encendido")
                return False
    except Exception as e:
        helper.show_error("Error desconocido " + str(ser.port) + ".\n\n"
                          "Exception:\n" + str(e))
        logger.exception('El controlador no responde')
