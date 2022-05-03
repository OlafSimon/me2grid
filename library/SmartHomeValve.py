# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-

"""! @file SmartHomeValve.py
    @brief Simple smart home application controlling a radiator valve by an window reed contact
    
    The application controlls a BLE connected radiator valve CC_RT_BLE from EQ-3 by sensing an open window using the reed relai from a
    TI Sensor Tag. This application serves as a first and very simple (but already effectively energy saving) sample program for the direct
    usage of BLE controlled external devices. It does not implement any smart home or smart factory related concept.
"""

from me2grid.devices.texas_instruments import SensorTag
from me2grid.devices.texas_instruments import InputSensor, OutputActor
from me2grid.devices.eq3 import CC_RT_BLE, RequestService
from me2grid.BibPy.HAL.kbhit import KBHit

tag = SensorTag('54:6C:0E:52:C7:84')
eq = CC_RT_BLE("00:1A:22:12:0F:87")

cycle = 0.1
oldReedRelai = None

print("Valve control by window reed contact")

print("Connecting tag")
tag.connect()
print("Connecting valve")
eq.connect()

print("Enter 'x' to quit")

run = True
while run:
    if KBHit.kbhit():
        c = KBHit.getch()
        if c == 'x':
            run = False
            
    tag.getNotifications(cycle)
    
    digIn = tag.getSensorValue(InputSensor)
    if digIn.reedRelai is not oldReedRelai:
        oldReedRelai = digIn.reedRelai
        if digIn.reedRelai:
            eq.writeOpenWindow(True)
        else:
            eq.writeOpenWindow(False)
            
    print("Window " + ("open  " if digIn.reedRelai else "closed"), end="   \r")

print("")
eq.writeOpenWindow(False)
print("Disconnecting valve")
eq.disconnect()
print("Disconnecting tag")
tag.disconnect()
print("Ready")
