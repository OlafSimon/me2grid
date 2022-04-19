"""!
@file  EQ3.py

@brief Bluetooth client for the EQ3 valve

@section Description

This Library provides objects to communication to smart home devices such as sensors and actuators as well as
more complex machines. It is part of the me2grid open source project. Library objects care for communication to devices, organizing devices to groups and
manage device to device communication.

It might happen, the EQ3 doesn't answer the 'get target temperature' request (0x03). Although it answers to 'number plate request' 0x00.
Reset the device through the menu to bring it back working.

https://github.com/Heckie75/eQ-3-radiator-thermostat/blob/master/eq-3-radiator-thermostat-api.md

@section Requirements

- bleak \n
\n
Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html \n
\n

Hints for further programming:
text = "{'00:00': 17, '06:00': 23, '10:00': 17, '14:30': 27, '18:00': 17}"
import ast
temp_dict = ast.literal_eval(text)
print (temp_dict)

"""

# import asyncio
import binascii
import math
import bleak

from enum import IntEnum
from typing import Union
from uuid import UUID
from bleak.backends.characteristic import BleakGATTCharacteristic
from datetime import datetime, timedelta
from EasyBleakClient import EasyBleakClient

class CC_RT_BLE(EasyBleakClient):
    """! @brief Bluetooth client for the EQ3 valve """
    
    charUUID_ReadWriteRequest  = "3fa4585a-ce4a-3bad-db4b-b8df8179ea09" # handle 0x0411
    charUUID_ReadWriteResponse = "d0e8434d-cd29-0996-af41-6c90f4e0eb2a" # handle 0x0421
    #handle: 0x0110, char properties: 0x02, char value handle: 0x0111, uuid: 00002a00-0000-1000-8000-00805f9b34fb
    #handle: 0x0120, char properties: 0x02, char value handle: 0x0121, uuid: 00002a01-0000-1000-8000-00805f9b34fb
    #handle: 0x0130, char properties: 0x02, char value handle: 0x0131, uuid: 00002a02-0000-1000-8000-00805f9b34fb
    #handle: 0x0140, char properties: 0x08, char value handle: 0x0141, uuid: 00002a03-0000-1000-8000-00805f9b34fb
    #handle: 0x0150, char properties: 0x02, char value handle: 0x0151, uuid: 00002a04-0000-1000-8000-00805f9b34fb
    #handle: 0xff01, char properties: 0x38, char value handle: 0xff02, uuid: e3dd50bf-f7a7-4e99-838e-570a086c666b
    #handle: 0xff04, char properties: 0x08, char value handle: 0xff05, uuid: 92e86c7a-d961-4091-b74f-2409e72efe36
    #handle: 0xff06, char properties: 0x02, char value handle: 0xff07, uuid: 347f7608-2e2d-47eb-913b-75d4edc4de3b

    class Mode(IntEnum):
        INVALID = 0xFF
        AUTO = 0xFE
        MANUAL = 0x1
        VACATION = 0x2
        BOOST = 0x4
        DST = 0x8
        OPENWINDOW = 0x10
        LOCKED = 0x20
        UNKNOWN = 0x40
        LOWBATTERY = 0x80

    class Day(IntEnum):
        ALL = 0xFF
        SATURDAY = 0x0
        SUNDAY = 0x1
        MONDAY = 0x2
        TUESDAY = 0x3
        WEDNESDAY = 0x4
        THURSDAY = 0x5
        FRIDAY = 0x6
        
    def __init__(self, mac):
        super().__init__(mac)
        self.requestNotifycationResult = None
        self.modes = []
        self.targetTemperature = None
        self.setting = None
        self.isOpenWindow = False
        self.openWindowPreviousAutomatic = False
        self.openWindowPreviousTemperature = 18
        self.openWindowTemperature = 8;
        
    def decodeModes(self, data: int):
        modes = []
        if data & int(self.Mode.MANUAL):
            modes.append(self.Mode.MANUAL)
        else:
            modes.append(self.Mode.AUTO)
        if data & int(self.Mode.VACATION):
            modes.append(self.Mode.VACATION)
        if data & int(self.Mode.BOOST):
            modes.append(self.Mode.BOOST)
        if data & int(self.Mode.DST):
            modes.append(self.Mode.DST)
        if data & int(self.Mode.OPENWINDOW):
            modes.append(self.Mode.OPENWINDOW)
        if data & int(self.Mode.LOWBATTERY):
            modes.append(self.Mode.LOWBATTERY)              
        return modes

#     def _request_notification_handler_(self, sender, data):
#         """Simple notification handler which stores the data received."""
#         self.requestNotifycationResult = data
#         print("EQ3 _request_notification_handler_ from {0}: {1}".format(sender, data))
#         
#     def request(self, charUUID_NotificationResponse: Union[BleakGATTCharacteristic, int, str, UUID], charUUID_NotificationRequest: Union[BleakGATTCharacteristic, int, str, UUID], data: bytearray, timeOut: float = 1.0) -> Union[bytearray, None]:
#         """! @brief Requests data from a BLE device using the notification response procedure
#              Some BLE devices use a command characeristic. Writing e.g. a read request command coded
#              within the data bytearry, specific to the vendor of the device, will force a notification
#              response containing the answer with the requested infromation content, also specifically coded
#              by the vendor.
#         """
#         print("-> EQ Special request")
#         self.requestNotifycationResult = None
#         done = False
#         while not done:
#             try:
#                 self.start_notify(charUUID_NotificationResponse, self._request_notification_handler_)
#                 self.write(charUUID_NotificationRequest, data)
#                 done = True
#             except Exception as e:
#                 if not done:
#                     # Sometimes, especially in case there hasn't been communication for longer time (few minutes),
#                     # the EQ3 hangs up and refuses sending notifications any more. It disconnects with receiving the 'start_notify' command.
#                     # Just reconnecting doesn't help. An additional single write command is necessary to bring the EQ3 back to normal operation. 
#                     print("-> Running refused notifications workaround")
#                     self.connect()
#                     self.write(charUUID_NotificationRequest, b'\x00')
#                     done = True # don't run the exception handling a second time
#                 else:
#                     raise e
#         timeOutCnt = timeOut*10
#         while timeOutCnt>0 and self.requestNotifycationResult==None:
#             print("-> Check time out")
#             timeOutCnt = timeOutCnt - 1
#             self.getNotifications(0.1)
#         self.stop_notify(charUUID_NotificationResponse)
#         if (timeOutCnt==0):
#             raise bleak.exc.BleakError("Request procedure failed with time out of {}s while waiting for the notification response!".format(timeOut))
#         return self.requestNotifycationResult

    def writeTime(self, time = None):
        """ \brief Sets the time of the valve from a given datetime object
            If no time is given as an argument the current time is used.
        """
        if time is None:
            time = datetime.now()
        
        data = bytearray(7)
        data[0] = 0x03
        data[1] = time.year % 100
        data[2] = time.month
        data[3] = time.day
        data[4] = time.hour
        data[5] = time.minute
        data[6] = time.second

        result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
        
        if result is not None and len(result) >= 5:
            self.modes = self.decodeModes(result[2])
            self.setting = result[3]
            self.targetTemperature = result[5]
            #print(binascii.hexlify(result))
        return

    def readTargetTemperature(self):
        """! @brief Retreives the currently active target temperature value within °C
        """
        result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x03')
        
        #print("Get temperature: ", binascii.hexlify(result))

        if result is not None and len(result) >= 5:
            self.modes = self.decodeModes(result[2])
            self.setting = result[3]
            self.targetTemperature = float(result[5] / 2)
            return self.targetTemperature
        return None

    def writeTargetTemperature(self, temperature):
        """! @brief Sets the currently active target temperature value to the given value in °C
        """
        result = None
        if temperature == 'comfort':
            result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x43')
        elif temperature == 'eco':
            self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x44')
        else:
            if type(temperature) == str:
                return None, None
            data = bytearray(b'\x41\x00')
            data[1] = int(temperature*2)           
            result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
            
        if result is not None and len(result) >= 5:
            modes = self.decodeModes(result[2])
            self.setting = result[3]
            self.targetTemperature = float(result[5] / 2)
        return
                       
    def readModes(self):
        """! @brief Retrieves the current operation modes (e.g. manual or auto)
        @returns A list of \ref Modes
        """
        # result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
        if self.readTargetTemperature() is not None:
            return self.modes
        return []
    
    def writeModes(self, modes, unset: bool = False, setall: bool = False, vacationDate: datetime = None, temperatureVacation = 10, timeOpenWindowMinutes = 30, temperatureOpenWindow = 10):
        """! @brief Sets a list of operation modes
        """
        if type(modes) is not type([]):
            modes = [modes]
        try:
            modes.index(self.Mode.AUTO)
            if not unset:
                self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x00')  
            else:
                self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x40')              
        except ValueError:
            try:
                modes.index(self.Mode.MANUAL)
                if not unset:
                    self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x40')  
                else:
                    self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x00')              
            except ValueError:
                if setall:
                    if not unset:
                        self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x00')              
                    else:
                        self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, b'\x40\x40')              
        try:
            modes.index(self.Mode.VACATION)
            if not unset and date is not None:
                data = b'\x40\x00\x00\x00\x00\x00'
                data[1] = byte(temperature*2+128)
                data[2] = byte(vacationDate.day)
                data[3] = byte(vacationDate.year%100)
                data[4] = byte(vacationDate.hour*2)
                data[5] = byte(vacationDate.month)
                self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
        except ValueError:
            pass
        data = None
        try:
            modes.index(self.Mode.OPENWINDOW)
            print('OpenWindow mode')
            data = bytearray(b'\x14\x00\x00')
            if not unset:
                data[1] = int(temperatureOpenWindow * 2)
                data[2] = int(timeOpenWindowMinutes / 5)
            else: 
                data[1] = int(temperatureOpenWindow * 2)
                data[2] = 0
        except:
            if setall:
                data = bytearray(b'\x14\x00\x00')
                if not unset:
                    data[1] = int(temperatureOpenWindow * 2)
                    data[2] = int(timeOpenWindowMinutes / 5)
                else: 
                    data[1] = int(temperatureOpenWindow * 2)
                    data[2] = 0
        if data is not None:
            res = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
            #if res is not None:
            #    print(binascii.hexlify(res))
            #else:
            #    print(res)
                
    def writeTimer(self, day, list):
        """! @brief Sets the timer values for automatic mode for a single day of the week.
            The timer events and temperature values are given as a dictionary of time and
            temperature. The temperature will be active after the given time event. Up to
            eight events may be set. The first time event must be 00:00. In case less than
            eight events are set, the last event must be 24:00 with with 0 as temperature value.
        """
        data = bytearray(16)
        for x in data:
            data
        data[0] = 0x10
        data[1] = day
        timeFormat = '%H:%M'
        i=0
        for t in list:
            #print(t)
            if i is 8:
                print ('Error: List is too long')
                break;
            time = datetime.strptime(t, timeFormat) - datetime.strptime('00:00', timeFormat)
            minutes = time.seconds // 60
            #print(minutes)
            if i is 0 and minutes is not 0:
                print ('Error: First time is not 00:00. Time is changed to 00:00')
                minutes = 0
            if i is 0:
                data[2 * i + 2]=list[t]*2
            elif i is 7:
                data[2 * i + 1] = 24 * 6
            else:
                data[2 * i + 1] = minutes // 10
                data[2 * i + 2] = list[t]*2
            i = i + 1
        if i < 7:
            data[2 * i + 1] = 24 * 6
            
        #print(binascii.hexlify(data))

        result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)
            
        #print(binascii.hexlify(result))
        return

    def readTimer(self, day):
        """! @brief Gets the timer values for automatic mode for a single day of the week.
            The timer events and temperature values are returned as a dictionary of time and
            temperature. The temperature will be active after the given time event. An event
            at 24:00 indicates the end of the list.
        """
        data = bytearray(b'\x20\x00')
        data[1] = day           
        
        result = self.request(self.charUUID_ReadWriteResponse, self.charUUID_ReadWriteRequest, data)    
        #print(binascii.hexlify(result))
        
        timeFormat = '%H:%M'
        timeBase = datetime.strptime('00:00', timeFormat)
        list = {}
        i=2
        end = False
        while not end and i<14:
            if i is 2:
                list[timeBase.strftime(timeFormat)]=result[i]/2
                i = i + 1
            else:
                if result[i] < 0x90:
                    timeDiff = timedelta(minutes=result[i]*10)
                    timeLocal = timeBase + timeDiff
                    list[timeLocal.strftime(timeFormat)]=result[i+1]/2
                    i = i + 2
                else:
                    end = True                
        return list
    
    def isMode(self, requestedMode, modes=None) -> bool:
        if modes is None:
            modes = self.modes
        try:
            modes.index(requestedMode)
            return True
        except:
            return False
            
    def writeOpenWindow(self, on: bool):
        """ Sets the valve into open window mode by bluetooth.
            As the valve internal open window mode can not be activated
            through bluetooth this method stores the active mode, enters
            manual mode and sets the temperature to a low value.
        """
        if on and not self.isOpenWindow:
            print("Writing open window\nReading temperature and modes")
            self.readTargetTemperature()
            if self.isMode(self.Mode.AUTO):
                self.isOpenWindow = True
                self.openWindowPreviousAutomatic = True
                print("Writing manual mode")
                self.writeModes(self.Mode.MANUAL)
            else:
                self.isOpenWindow = True
                self.openWindowPreviousAutomatic = False
                self.openWindowPreviousTemperature = self.targetTemperature
            print("Writing open window temperature")
            self.writeTargetTemperature(self.openWindowTemperature)
        if not on and self.isOpenWindow:                
            print("Writing to unsett open window")
            self.isOpenWindow=False
            if self.openWindowPreviousAutomatic:
                print("Writing to reset to automatic mode")
                self.writeModes(self.Mode.AUTO)
            else:
                print("Writing to reset to room temperature")
                self.writeTargetTemperature(self.openWindowPreviousTemperature)
        print("OpenWindow ready")
        return

if __name__ == '__main__':

    valve = EQ3_CC_RT_BLE_EQ("00:1A:22:12:0F:87")
    print("Connecting")
    valve.connect()
    print("Reading values")
    valve.readModes()
    print(valve.modes)
    print(str(valve.readTargetTemperature()) + " °C")
    print("Disconnecting")
    valve.disconnect()
    print("Ready")
