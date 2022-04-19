# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  EasyBleakScanner.py

@brief Provides an easy to use BLE devices scanner 

@section Requirements \n

- bleak \n
\n
Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html
"""

import asyncio
from typing import Union
from uuid import UUID
import bleak
#import dbusFunction
from bleak import BleakScanner #, BleakClient, exc
#from bleak.backends.characteristic import BleakGATTCharacteristic

# from dbus_next.message import Message
# from bleak.backends.bluezdbus import defs
# from dbus_next.signature import Variant
# from bleak.backends.bluezdbus.utils import assert_reply

class EasyBleakScanner(BleakScanner):
    def detection_callback(self, device, advertisement_data):
        # print("Notification of ", device.address, " ", device.name)
        return

    def __init__(self):
        super().__init__()
        self.register_detection_callback(self.detection_callback)
       
    async def as_scan(self):
        # await self.discover()
        await self.start()
        await asyncio.sleep(5)
        await self.stop()
        #async with self as _:
        #   await asyncio.sleep(5)
        
    def scan(self):
        print("Scanning BLE for 5 s ...")
        asyncio.run(self.as_scan())
        print("Discovered devices:")
        for d in self.discovered_devices:
            print(d)
        print("Scanning BLE finished")
       

if __name__ == '__main__':
    scann = EasyBleakScanner()
    scanner.scan()
