from hydraserial import HydraSerial
from sys import argv
from math import *
import struct
import time

ser = HydraSerial(argv[1],115200)

def msg_recv(msg_id, payload):
    if msg_id == 0x02:
        print "theta: %f" % (degrees(struct.unpack("H", payload)[0] *(2.*pi)/65536.))
        ser.write(0x01, struct.pack('<h', 2000*sin(time.time())))

while True:
    ser.read(msg_recv)
