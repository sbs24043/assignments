import serial, struct, numpy as np
from PIL import Image  
from serial.tools import list_ports

#Alphabetically lists the ports by name
def comslist():
    ports = []
    for i in list_ports.comports():
        try:
            ser = serial.Serial(i.name)
            ser.close()
        except serial.SerialException as e:
            print(e)
        else:
            ports.append(i.name)
    ports.sort()
    return ports

#Finds the desired port using the name eg COM1
def selectcom(port):
    try :
        ser = serial.Serial(port)
    except serial.SerialException as e:
        print(e)
    else:
        return ser
    
print(comslist())