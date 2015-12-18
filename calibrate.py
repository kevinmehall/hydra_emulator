from hydraserial import HydraSerial
from sys import argv
from math import *
import struct
import time

ser = HydraSerial(argv[1],115200)

CMD_SET_IQ = 0x01
CMD_POS = 0x02
CMD_SET_ID = 0x04
CMD_MSTAT = 0x03
CMD_PING = 0x10
CMD_PONG = 0x11

MSTAT_EN = 1
MSTAT_PARK_OVERRIDE = 2

pos_lpf = 0

def msg_recv(msg_id, payload):
    global pos_lpf
    if msg_id == 0x02:
        pos_lpf = pos_lpf * 0.99 + (payload[0] | payload[1] << 8)*0.01
        print "Position: %5.0f"%pos_lpf
    else:
        print msg_id, str(payload).encode("hex")



while True:
    ser.write(CMD_MSTAT, [MSTAT_EN | MSTAT_PARK_OVERRIDE])
    ser.write(CMD_SET_IQ, [0x00, 0x00])
    ser.write(CMD_SET_ID, [0x00, 0x10])
    ser.read(msg_recv)
    time.sleep(0.001)
    
    
