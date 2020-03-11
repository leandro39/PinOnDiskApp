import serial.tools.list_ports 
import time

def get_serial_ports():
    return sorted([port.device for port in serial.tools.list_ports.comports()])

def setup_port(ser, port, lock):
    try:
        with lock:
            ser.baudrate = 9600
            ser.port = port
            ser.bytesize = serial.EIGHTBITS
            ser.stopbits = serial.STOPBITS_ONE
            ser.parity = serial.PARITY_NONE
            ser.timeout = 1.0
        
    except Exception as e:
        helper.show_error("Problema inicializando puerto " + port + ".\n\n"
                        "Exception:\n" + str(e))

def open_serial(ser, lock):
    try:
        with lock:
            print('opening')
            ser.open()
            time.sleep(2)

    except Exception as e:
        helper.show_error("No fue posible abrir el puerto " + ser.port + ".\n\n"
                          "Intente con otro puerto\n\n"
                          "Exception:\n" + str(e))
        

def close_serial(ser):
    try:
        if (ser.is_open):
            ser.write(b'<DCON>\n')
            if (ser.readline().decode('ascii').strip() == '0'):    
                ser.close()
                return False
            else:
                return True
            
    except Exception as e:
        helper.show_error("Error desconocido " + ser.port + ".\n\n"
                          "Exception:\n" + str(e) + "\n\n")

def try_connect(ser, port, lock):
    try:
        setup_port(ser,port,lock)
        open_serial(ser, lock)
        if ser.is_open:
            with lock:
                ser.write(b'<CONN>\n')
                read = ser.readline().decode('ascii').strip()
                if (read == '0'):
                    return True
                else:
                    
                    close_serial(ser)
                    helper.show_error("El controlador no responde" +"\n\n" "Intente con otro puerto y verifique que está conectado y encendido")
                    return False
    except Exception as e:
        helper.show_error("Error desconocido " + str(ser.port) + ".\n\n"
                          "Exception:\n" + str(e))