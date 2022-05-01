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

import binascii

from enum import IntEnum
from datetime import datetime, timedelta

try: # Necessary, to run this file directly
    from .easybleak.EasyBleakClient import EasyBleakClient
    from .easybleak.ExtBleakClient import BaseService, CharacteristicType
    from .easybleak.gatt import BLE_UUID, ClassServices
    from .BibPy.mathlib.Vector3 import Vector3
except:
    from me2grid.easybleak.EasyBleakClient import EasyBleakClient
    from me2grid.easybleak.ExtBleakClient import BaseService, CharacteristicType
    from me2grid.easybleak.gatt import BLE_UUID, ClassServices
    from me2grid.BibPy.mathlib.Vector3 import Vector3


class RequestService(BaseService):
    """! @brief Service enumeration of command response data exchange
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    COMMAND  = CharacteristicType("3fa4585a-ce4a-3bad-db4b-b8df8179ea09") # handle 0x0411
    RESPONSE = CharacteristicType("d0e8434d-cd29-0996-af41-6c90f4e0eb2a") # handle 0x0421
    # charUUID_Notification      = "00002a29-0000-1000-8000-00805f9b34fb" # handle 0x0311                 

    @classmethod
    def uuidService(cls) -> str:
        return "3e135142-654f-9090-134a-a6ff5bb77046"

class UnknownService(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    CHAR0 = CharacteristicType("e3dd50bf-f7a7-4e99-838e-570a086c666b")
    CHAR1 = CharacteristicType("92e86c7a-d961-4091-b74f-2409e72efe36")
    CHAR2 = CharacteristicType("347f7608-2e2d-47eb-913b-75d4edc4de3b")

    @classmethod
    def uuidService(cls) -> str:
        return "9e5d1e47-5c13-43a0-8635-82ad38a1386f"

cc_rt_ble_Services = ClassServices({"RequestService": RequestService, "UnknownService": UnknownService})

class CC_RT_BLE(EasyBleakClient):
    """! @brief Bluetooth client for the EQ3 valve """
    __services__ : ClassServices = EasyBleakClient.createAppendedServices(cc_rt_ble_Services)

    offTemperature = 4.5
    
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
        self.requestUsing(RequestService.RESPONSE, RequestService.COMMAND)   # avoiding a _checkConnect_ from @asyncCall
        # Memorized values from readings
        self.modes = []
        self.targetTemperature = None
        self.setting = None
        # ConfiguredConstants
        self.openWindowTemperature = self.offTemperature
        
    def disconnect(self):
        """! brief Disconnect with exception handling
            The valve does automatically disconnect after a certain time (some minutes) of BLE communication inactivity. This disconnect
            is not noticed by the bleak-client. As an exception is thrown in case of calling stop_notification or disconnect at a disconnected
            device such exceptions can be treated as being accepted during normal operation.
        """
        try:
            super().disconnect()
        except:
            pass
        
    def request(self, data: bytearray) -> bytearray:
        """! brief Spezialised 'request' method for the eq3 providing recovery from response time out
            Under some not exactly known conditions, the EQ3 enters a state where request commands will not be answered. This state is entered
            only if the device is in manual mode. Although not delivering a reply, the device does read and execute incoming commands correctly.
            To exit this state it is necessary to switch the device to automatic mode either by a command or manually.  \n
            In case the first request initiated by this method fails, the device will be switched to automatic mode and the previous failed request
            will be repeated. In case the second request fails again the corresponding exception will be thrown.\n
            (It has been observed, the serial number plate request b'\x00' is answered in all condtiontions.)\n
            Some known conditions for outstanding responses are: Switching to manual mode by BLE command. Recovering is possible, if a automatic mode
            is send. There is no issue in case you switch to manual mode manually with the device keys. In case the device is set to vacation mode
            manually. 
        """
        try:
            return super().request(data)
        except Exception as e:
            return None
        
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

    def readSerialNumber(self) -> str:
        """ \brief Sets the time of the valve from a given datetime object
            If no time is given as an argument the current time is used.
        """
        data = bytearray(b'\x00')
        #data[0] = 0
        ans = self.request(data)
        print(ans)
        asc = bytearray([d-0x30 for d in ans[4:14]])
        return asc.decode("utf-8")

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

        result = self.request(data)
        
        if result is not None and len(result) >= 5:
            self.modes = self.decodeModes(result[2])
            self.setting = result[3]
            self.targetTemperature = result[5]
            #print(binascii.hexlify(result))
        return

    def readTargetTemperature(self):
        """! @brief Retreives the currently active target temperature value within °C
        """
        result = self.request(b'\x03')
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
            result = self.request(b'\x43')
        elif temperature == 'eco':
            self.request(b'\x44')
        else:
            if type(temperature) == str:
                return None, None
            data = bytearray(b'\x41\x00')
            data[1] = int(temperature*2)           
            result = self.request(data)
            
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
    
    def writeMode(self, mode, vacationDate: datetime = None, temperatureVacation = 10):
        """! @brief Sets a single or a list of modes
            It is possible to either set manual mode (CC_RT_BLE.Mode.MANUAL), automatic mode (CC_RT_BLE.Mode.AUTO)
            or vacation mode (CC_RT_BLE.Mode.VACATION).
        """
        if mode is self.Mode.MANUAL:
            self.request(b'\x40\x40')              
        elif mode is self.Mode.VACATION and date is not None:
            data = b'\x40\x00\x00\x00\x00\x00'
            data[1] = byte(temperature*2+128)
            data[2] = byte(vacationDate.day)
            data[3] = byte(vacationDate.year%100)
            data[4] = byte(vacationDate.hour*2)
            data[5] = byte(vacationDate.month)
            self.request(data)
        elif mode is self.Mode.AUTO:
            self.request(b'\x40\x00')
        else:
            raise ValueError("Requested Mode cannot be written.")

    def writeConfigurationOpenWindow(self, timeOpenWindowMinutes = 15, temperatureOpenWindow = 5):
        """! brief Configures the automatic open window detection
            In case of a rapid temperature decrease the valve switches to the open window mode automatically. It is not possible doing so
            manually or by BLE command! It is only possible to configure how long the mode should be entered at what minimum temperature should be
            hold during this time. This configuration can be done using this method.
        """
        data = bytearray(b'\x14\x00\x00')
        data[1] = int(temperatureOpenWindow * 2)
        data[2] = int(timeOpenWindowMinutes / 5)
        self.request(data)
        #if res is not None:
        #    print(binascii.hexlify(res))
        #else:
        #    print(res)
        return
                
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
                #raise ValueError('List is too long')
                break;
            time = datetime.strptime(t, timeFormat) - datetime.strptime('00:00', timeFormat)
            minutes = time.seconds // 60
            #print(minutes)
            if i is 0 and minutes is not 0:
                #print ('Error: First time is not 00:00. Time is changed to 00:00')
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

        result = self.request(data)
            
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
        
        result = self.request(data)    
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
            
    def writeOpenWindow(self, on: bool = True, openWindowTemperature: float = None):
        """ Sets the valve into open window mode by bluetooth.
            As the valve internal open window mode can not be activated
            through bluetooth this method stores the active mode, enters
            manual mode and sets the temperature to a low value.
        """
        if openWindowTemperature is not None:
            self.openWindowTemperature = openWindowTemperature
        if on:
            self.writeMode(self.Mode.MANUAL)
            self.writeTargetTemperature(self.openWindowTemperature)
        else:
            self.writeMode(self.Mode.AUTO)
        return

def programGettingStarted():
    from me2grid.devices.eq3 import CC_RT_BLE

    valve = CC_RT_BLE("00:1A:22:12:0F:87")
    print("Connecting")
    valve.connect()
    print("Reading values")
    valve.readModes()
    print(valve.modes)
    print("Temperature target value:")
    print(str(valve.readTargetTemperature()) + " °C")
    print("Disconnecting")
    valve.disconnect()
    print("Ready")
  
if __name__ == '__main__':

    programGettingStarted()
