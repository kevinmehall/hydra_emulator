import serial
from sys import argv
from multiprocessing import Process, Queue
from math import *
import scipy.integrate as integrate
from visual import *
import numpy as np
import time
import crc
import struct

from hydraserial import HydraSerial


def dyn(state,t,params):
    Idem = params[0]
    Vbatt = params[1]
    Km = params[2]
    R  = params[3]
    Im = params[4]
    Kf = params[5]

    omega = state[0]
    theta = state[1]

    V = Km*omega + Idem*R
    if V > Vbatt:
        V = Vbatt
    if V < -Vbatt:
        V = -Vbatt
    I = (V-Km*omega)/R

    return [(Km*I-Kf*omega)/Im, omega]

def motorSim(rxq, txq):
    scene.range = 1
    scene.forward = (cos(radians(20)),-sin(radians(20)),0)
    motor = cylinder(pos=(0.,0.,0.), axis=(0.,.22,0.), up=(1,0,0), radius=.63, material=materials.rough)

    params = [0.0, 16.8, 0.308, 10.0, 0.00001, 0.00005]
    state = np.array([0.0, 0.0])
    dt = 1./50.
    x = np.linspace(0.,dt,1000.*dt)
    while True:
        frameStart = time.time()
        y = integrate.odeint(dyn,state,x,(params,))
        state = y[-1]
        state[1] = state[1]%(2*pi)
        motor.up = (sin(state[1]),0,cos(state[1]))
        txq.put(state[1],False)
        while not rxq.empty():
            params[0]=rxq.get(False)
        frameEnd = time.time()
        sleepTime = max(dt-(frameEnd-frameStart),0)
        time.sleep(sleepTime)


txq = Queue()
rxq = Queue()
p = Process(target=motorSim, args=(txq, rxq))
p.start();

ser = HydraSerial(argv[1],115200)

def msg_recv(msg_id, payload):
    if msg_id == 0x01:
        curr_dem = struct.unpack("h", payload)[0] * 0.01/32767.
        txq.put(curr_dem)
        print "demanded current: %f" % (curr_dem)

while True:
    if not rxq.empty():
        while not rxq.empty():
            theta = rxq.get()
        theta = struct.pack('<H', int(theta*65536./(2.*pi)))
        ser.write(0x02, theta)
    ser.read(msg_recv)
