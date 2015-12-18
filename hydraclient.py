from hydraserial import HydraSerial
from sys import argv
from math import *
import struct
import time

ser = HydraSerial(argv[1],115200)

def motor_enable():
    ser.write(0x03, [0x01])

def set_iq(val):
    if val > 0x7fff:
        val = 0x7fff
    if val < -0x7fff:
        val = -0x7fff
    ser.write(0x01, struct.pack( "<h", val))
    
def set_id(val):
    ser.write(0x04, struct.pack( "<h", val))

position = 0

def msg_recv(msg_id, payload):
    if msg_id == 0x02:
        position = (payload[0] | payload[1] << 8)
        print "Position:", position
    else:
        print msg_id, str(payload).encode("hex")
        

last_err = 0
i_err = 0

motor_enable()


while True:
    set_iq(int(argv[2]))
    set_id(int(argv[3]))  
    ser.read(msg_recv)
    time.sleep(0.001)
