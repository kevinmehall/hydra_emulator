import serial
import struct
from collections import deque
import crc

class HydraSerial:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.ser = serial.Serial(self.port, self.baud, timeout=0)
        self.buf = deque()

    def read(self, msg_cb=None):
        self.buf.extend(self.ser.read(32768))
        self._check_for_msg(msg_cb)

    def write(self, msg_id, payload):
        self.ser.write(self._pack_msg(msg_id,payload))
        self.ser.flush()

    def _pack_msg(self, msg_id, payload):
        msg = struct.pack("<HBB%uB" % (len(payload)), (0x94<<8)|0x11, len(payload), msg_id, *bytearray(payload))
        msg += struct.pack("<B", crc.crc8(msg))
        return msg

    def _check_for_msg(self, msg_cb):
        while len(self.buf):
            # messages must start with 0x11 0x94
            while True:
                if len(self.buf) > 1 and (ord(self.buf[0]) != 0x11 or ord(self.buf[1]) != 0x94):
                    self.buf.popleft()
                elif len(self.buf) > 0 and ord(self.buf[0]) != 0x11:
                    self.buf.popleft()
                else:
                    break

            # messages are at least 5 bytes long
            if len(self.buf) < 5:
                # out of bytes, break
                break

            # payload length is specified in protocol
            payload_len = ord(self.buf[2])
            msg_len = 5+payload_len
            if len(self.buf) < msg_len:
                # out of bytes, break
                break

            msg_str = bytearray(self.buf)[0:msg_len]

            msg_struct_fmt = "<HBB%uBB" % (payload_len)
            msg_struct = struct.unpack(msg_struct_fmt, msg_str)

            msg_crc = msg_struct[-1]
            expected_crc = crc.crc8(bytes(msg_str[0:-1]))

            if msg_crc == expected_crc:
                msg_id = msg_struct[2]
                payload = bytearray(msg_struct[3:3+payload_len])
                if msg_cb is not None:
                    msg_cb(msg_id,payload)
            else:
                print "failed crc"

            # remove this message from the queue
            for i in range(msg_len):
                self.buf.popleft()
