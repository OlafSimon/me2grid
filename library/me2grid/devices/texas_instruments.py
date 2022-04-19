# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  SensorTag.py

@brief SensorTag client object based on 'bleak' library

@section Description

This is an easy to use BLE client for a Texas Instruments SensorTag. Methods for easy access to its features are
provided.

@section Usage

@code{.py}

from SensorTag import SensorTag

tag = SensorTag('[Bluetooth MAC Address]')
tag.connect()
tag.readManufacturer()
client.disconnect()

@endcode

@section TI_ERR Error handling

- bleak.exc.BleakError: Device with address 54:6C:0E:52:C7:84 was not found.
In this case the Sensor Tag can not be connected to. The Sensor Tag might be not in advertising state (green LED not flashing) or might be out of radio reach.

- AttributeError: 'NoneType' object has no attribute 'call'
This error arises if the Sensor Tag cannot be connected to because the Sensor Tag has already been connected to earlyier

- concurrent.futures._base.TimeoutError
Disconnect failed as device is reset, busy or off

- EOFError
Writing or reading to an unconnected device (e.g. if reconnection has failed or method write_gat_char has been used

- bleak.exc.BleakDBusError: [org.bluez.Error.NotSupported] Operation is not supported
Occurs e.g. when writing to a characteristic that is not writable.

- bleak.exc.BleakDBusError: [org.bluez.Error.Failed] Software caused connection abort
Restart the python interpreter.

@section TI_REQ Requirements

- bleak \n
\n
Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html

@section TI_DOC Documentation
For detailed documentaton see the Texas Instruments web sites or search the internet for 'CC2650_SensorTag_Users_Guide.pdf'.
This is abailable on exteral sites like \html https://usermanual.wiki/Document/CC265020SensorTag20Users20Guide2020Texas20Instruments20Wiki.2070227354.pdf .
A html version can be found on \html http://devrel.zoomquiet.top/data/20160412163806/index.html

@section TI_CREDITS Credits

- The 'bleak' BLE client library providing hardware independent use ( \html https://bleak.readthedocs.io/ ). The 'EasyBleak' library provides additional features to that library with the
intention to further promote that library.
- The 'bluepi' library also deliveres an BLE client implementation together with an appropriate and good SensorTag client,
although callbacks for sensors are not supported (except for the keys) with sensor value calculation. But, the main drawback is the
dependency to a Linux operating system. This is the reason for implementing the me2grid.easybleak.sensors.texas_instruments.SensorTag
BLE client object, based on the 'bleak' library running on several operating systems such as Windows and MacOS.
Viewing the code helped developing my SensorTag implementation concept.
"""
# Alternative BLE libraries are BLE_GATT or bluepi. bluepi also implements a SensorTag cient.

#import asyncio
#import binascii
#from datetime import datetime, timedelta

import time
from typing import Union
from enum import Enum

try: # Necessary, to run this file directly
    from .easybleak.EasyBleakClient import EasyBleakClient
    from .easybleak.ExtBleakClient import BaseService, CharacteristicType
    from .easybleak.gatt import BLE_UUID
    from .BibPy.mathlib.Vector3 import Vector3
except:
    from me2grid.easybleak.EasyBleakClient import EasyBleakClient
    from me2grid.easybleak.ExtBleakClient import BaseService, CharacteristicType
    from me2grid.easybleak.gatt import BLE_UUID
    from me2grid.BibPy.mathlib.Vector3 import Vector3

# TI SensorTag specific predifined services
def TI_UUID(val: int) -> str:
    """ @brief Transforms a 16bit Texas Instruments specific uuid integer value to a full uuid string """
    return ("f000%04x-0451-4000-b000-000000000000" % val)

class IrTemperatureSensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    DATA          = CharacteristicType(TI_UUID(0xaa01))
    CONFIGURATION = CharacteristicType(TI_UUID(0xaa02))
    PERIOD        = CharacteristicType(TI_UUID(0xaa03))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa20)

class HumiditySensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    DATA          = CharacteristicType(TI_UUID(0xaa21))
    CONFIGURATION = CharacteristicType(TI_UUID(0xaa22))
    PERIOD        = CharacteristicType(TI_UUID(0xaa23))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa20)

class BarometricPressureSensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    DATA          = CharacteristicType(TI_UUID(0xaa41))
    CONFIGURATION = CharacteristicType(TI_UUID(0xaa42))
    PERIOD        = CharacteristicType(TI_UUID(0xaa43))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa40)

class MotionSensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    DATA          = CharacteristicType(TI_UUID(0xaa81))
    CONFIGURATION = CharacteristicType(TI_UUID(0xaa82))
    PERIOD        = CharacteristicType(TI_UUID(0xaa83))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa80)

class OpticalSensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Optical Sensor Service'
        Hint: The BLE characteristic 0x2902 (Client Characteristic Control Descriptor) will be automatically written by the BleakClient!
    """
    DATA          = CharacteristicType(TI_UUID(0xaa71))
    CONFIGURATION = CharacteristicType(TI_UUID(0xaa72))
    PERIOD        = CharacteristicType(TI_UUID(0xaa73))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa70)

class InputSensor(BaseService):
    """! @brief Service enumeration of characteristics within the 'Simple Key Service' """
    DATA           = CharacteristicType(BLE_UUID(0xffe1))  #!> IO input data (Notification only! no read possible): bit0: left key (user button), bit1: right key (power button), bit2: reed relay

    @classmethod
    def uuidService(cls) -> str:
        return BLE_UUID(0xffe0)

class OutputActor(BaseService):
    """! @brief Service enumeration of characteristics within the 'IO Service' """
    DATA           = CharacteristicType(TI_UUID(0xaa65))  #!> IO output data: Remote CONFIGURATION -> bit0: LED1 red, bit1: LED2 green, bit2: buzzer ; Test CONFIGURATION (Error indication)-> bit0: IR temperature sensor, bit1: Humidity sensor, bit2: Optical sensor, bit3: Pressure sensor, bit4: MPU, bit5: Magnetometer, bit6: External Flash, bit7: Dev Pack
    CONFIGURATION  = CharacteristicType(TI_UUID(0xaa66))  #!> IO configuration: value -> 0: Application usage (Advertisiung blinking green and error indication red), 1: Remote usage (DATA characteristic controls the output), 2: Test usage (DATA characteristic deliveres self test result)

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xaa64)

class Register(BaseService):
    """! @brief Service enumeration of characteristics within the 'Register Service' """
    DATA         = CharacteristicType(TI_UUID(0xac01))
    ADDRESS      = CharacteristicType(TI_UUID(0xac02))
    DEVICE_ID    = CharacteristicType(TI_UUID(0xac03))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xac00)

class ConnectionControl(BaseService):
    """! @brief Service enumeration of characteristics within the 'Connection Control Service' """
    CONNECTION_PARAMETERS          = CharacteristicType(TI_UUID(0xccc1))
    REQUEST_CONNECTION_PARAMETERS  = CharacteristicType(TI_UUID(0xccc2))
    REQUEST_DISCONNECT             = CharacteristicType(TI_UUID(0xccc3))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xccc0)

class OAD(BaseService):
    """! @brief Service enumeration of characteristics within the 'OAD Service' (over air download of firmware images) """
    IMAGE_IDENTIFY          = CharacteristicType(TI_UUID(0xffc1))
    IMAGE_BLOCK  = CharacteristicType(TI_UUID(0xffc2))

    @classmethod
    def uuidService(cls) -> str:
        return TI_UUID(0xffc0)

sensorTagServices = {"IrSensor": IrTemperatureSensor, "HumiditySensor": HumiditySensor, "MotionSensor": MotionSensor, "BarometricPressureSensor": BarometricPressureSensor, "OpticalSensor": OpticalSensor, "InputSensor": InputSensor, "OutputActor": OutputActor}
"""! List of services provided by the Sensor Tag """
    
class MotionValues():
    """ @brief Contains the measurement data of the movement sensor
        Accessable members are gyroscope, acceleration and magnetism, providing the members x, y and z each.
    """
    def __init__(self, gyroX: float, gyroY: float, gyroZ: float, accX: float, accY: float, accZ: float, magX: float, magY: float, magZ: float):
        self.gyroscope    = Vector3([gyroX, gyroY, gyroZ])
        self.acceleration = Vector3([accX, accY, accZ])
        self.magnetism    = Vector3([magX, magY, magZ])

    def __str__(self):
        return (f"MotionValues(gyroscope={str(self.gyroscope)} deg/s, acceleration={str(self.acceleration)} G, magnetism={str(self.magnetism)} uT)")
    
class OutputValues():
    """! brief Contains output bits 'ledRed', 'ledGreen' and 'buzzer' of type 'bool' to be set or unset """
    def __init__(self, ledRed: bool = None, ledGreen: bool = None, buzzer: bool = None):
        """! brief Constructor """
        self.ledRed = ledRed
        self.ledGreen = ledGreen
        self.buzzer = buzzer
        
    def fromBytearray(self, data: bytearray):
        """! brief Sets the member variables by decoding the passed data 'byte' """
        if (int(data[0]) & 1) != 0:
            self.ledRed = True
        else:
            self.ledRed = False
        if (int(data[0]) & 2) != 0:
            self.ledGreen = True
        else:
            self.ledGreen = False
        if (int(data[0]) & 4) != 0:
            self.buzzer = True
        else:
            self.buzzer = False

    def __str__(self):
        return (f"OutputValues(ledRed={self.ledRed}, ledGreen={self.ledGreen}, buzzer={self.buzzer})")
    
class InputValues():
    """! brief Contains input bits 'userKey', 'powerKey' and 'reedRelai' of type 'bool' indicating if they are closed (True) or open (False) """
    def __init__(self, data: bytearray):
        """! brief Constructor """
        self.userKey = (int(data[0]) & 1) != 0
        self.powerKey = (int(data[0]) & 2) != 0
        self.reedRelai = (int(data[0]) & 4) != 0
        
    def __str__(self):
        return (f"InputValues(userKey={self.userKey}, powerKey={self.powerKey}, reedRelai={self.reedRelai})")
    
class SensorActor():
    """! @brief Base class for different types of sensor representations """
    def __init__(self, myService: BaseService):
        self.__myService = myService        #!> Defines the service the derived classes are designed for
        self._isEnabled = False            #!> Memorizes, if the sensor has already been enabled
        self.__applicationNotificationHandler = None     #!> Delegate to the application method handling the sensor notofication. applicationHandler(data: Union[float, tuple, MotionValues])
        self.__value: Union[float, tuple, MotionValues, InputValues, OutputValues, None] = None   #!> Memorizes the last decoded value 

    @property
    def service(self):
        """' @brief Retrieves the gatt service enumeration of the sensor derived from type 'BaseService' """
        return self.__myService        
    
    @property
    def value(self):
        """' @brief Retrieves the gatt service enumeration of the sensor derived from type 'BaseService' """
        return self.__value        
    
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief \b virtual Method for derived classes to return calculated sensor values from the passed data bytearray
            Derived classes must set the member 'myService' and the method implementation must call this base method to check if the passed
            service fits the service the derived class is designed for at the begin of the overriding 'decode' method. At the end of the overriding
            'decode' method the '__returnFromDecode__' method must be called to memorize the last decoded value.
            @param service An arbitrary 'BaseService' derived BLE service description object
            @param data 'bytearray' received from the sensor DATA characteristc of the passed service
            @param config Optional 'bytearray' received from the sensor CONFIGURATIONIG characteristc of the passed service
            @returns The calculated sensor data in case the passed service fits the service the derived class is derived for. 'None' otherwise.
        """
        if service is not self.service:
            return None
        
    def __returnFromDecode__(self, decodedValue: Union[float, tuple, MotionValues, InputValues, OutputValues, None]) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @ Memorizes the last decoded value
            To be called from the derived class at the end of the overriding 'decode' method. See \decode .
        """ 
        self.__value = decodedValue
        return decodedValue
           
    def encode(self, value: Union[float, tuple, MotionValues, InputValues, OutputValues, None], actualData: bytearray = None) -> bytearray:
        """! @brief \b virtual Method for derived classes to return the dataarray for the BLE communication from passed 'sensor' output values
            @param service An arbitrary 'BaseService' derived BLE service description object
            @param value Value to be written to the actor ('sensor') defined by the 'service' parameter 
            @param actualData 'bytearray' received from the sensor DATA characteristc of the passed service
            @returns The 'bytearray' to be written to the DATA characteristc of the passed service in case the passed service fits the service the derived class is derived for. 'None' otherwise.
        """
        raise NotImplementedError(f"Writing to service {str(service)} is not implemented: Writing to sensors is not possible, choose an actuator")
        
    def enableCode(self, enable: bool = True) -> bytearray:
        """! @brief Returns and memorizes the code to be written to the CONFIGURATION characteristic in order to enable measurements
            @param enable 'True' enables, 'False' disables
        """
        self._isEnabled = enable
        if enable:
            return bytearray(b'\x01')
        else:
            return bytearray(b'\x01')        
        
    def disabledMask(self) -> bytearray:
        """! @brief Returns a mask to binary and with the CONFIGURATION characteristic in order to check for enabled measurements
        """
        if enable:
            return bytearray(b'\x01')
        else:
            return bytearray(b'\x01')        
        
    @property
    def isEnabled(self) -> bool:
        """! @ Returns the last memorized enabled state of the sensor
            To be called from the derived class at the end of the overriding 'decode' method. See \decode .
        """ 
        return self._isEnabled
           
    def _OnNotification_(self, sender, data: bytearray) -> Union[float, tuple, MotionValues, None]:
        """! @brief Handler method for sensor notifications to be passed to the BLE client on 'start_notify' """
        value = self.decode(data)
        if self.__applicationNotificationHandler is not None:
            self.__applicationNotificationHandler(value)
            
    def _setNotificationHandler_(self, notificationHandler):
        """! @brief To be called from the BLE client applicatoin interface method 'start_notify' in order to set the application callback handler for this sensor """
        self.__applicationNotificationHandler = notificationHandler
    
    @staticmethod
    def _checkSize_(data: bytearray, expectedSize: int):
        if data is None:
            raise ValueError()
        if  len(data)!=expectedSize:
            raise ValueError(f"The bytearray size is {len(data)} but the expected size is {expectedSize}")
    
    @staticmethod
    def _codePeriodTime_(periodTime: float) -> bytearray:
        t = int(periodTime*100)
        if t<10:
            t=10
        if t>255:
            t=255
        return bytearray(t.to_bytes(1, 'little'))
        
    @staticmethod
    def _decodePeriodTime_(rawTime: bytearray) -> float:
        SensorActor._checkSize_(rawTime, 1)
        t = int.from_bytes(rawTime, "little", signed=False)
        return float(t)/100.0
        
class SensorIrTemperature(SensorActor):
    """! @brief IR temperature sensor representation """
    zeroC = 273.15 # Kelvin
    tRef  = 298.15
    S0 = 6.4e-14
    Apoly = [1.0,      1.75e-3, -1.678e-5]
    Bpoly = [-2.94e-5, -5.7e-7,  4.63e-9]
    Cpoly = [0.0,      1.0,      13.4]

    def __init__(self):
        super().__init__(IrTemperatureSensor)
        
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes ir temperature sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A tuple with targeted object temperature and the ambient temperature in °C
        """
        if super().decode(service, data) is None:
            return None
        SensorActor._checkSize_(data, 4)
        rawVobj = int.from_bytes(data[0:2], "little", signed=False)
        rawTamb = int.from_bytes(data[2:4], "little", signed=False)

        tAmb = rawTamb / 128.0
        Vobj = 1.5625e-7 * rawVobj
        tDie = tAmb + SensorIrTemperature.zeroC
        S    = S0 * SensorIrTemperature.__calcPoly__(SensorIrTemperature.Apoly, tDie-tRef)
        Vos  = SensorIrTemperature.__calcPoly__(SensorIrTemperature.Bpoly, tDie-tRef)
        fObj = SensorIrTemperature.__calcPoly__(SensorIrTemperature.Cpoly, Vobj-Vos)
        tObj = math.pow( math.pow(tDie, 4.0) + (fObj/SensorIrTemperature.S), 0.25 ) - SensorIrTemperature.zeroC
        
        return self.__returnFromDecode__( (float(tObj), float(tAmb)) )
        
    @staticmethod
    def __calcPoly__(coeffs, x):
        """ @brief \b private Calculates a polynom interpolated value """
        return coeffs[0] + (coeffs[1]*x) + (coeffs[2]*x*x)

class SensorHumidity(SensorActor):
    def __init__(self):
        super().__init__(HumiditySensor)
        
    """! @brief Humidity sensor representation """
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes humidity sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A float value of the relative humidity in %RH
        """
        SensorActor._checkSize_(data, 4)
        return self.__returnFromDecode__( float(int.from_bytes(data[2:4], "little", signed=False) / 65536 * 100) )

class SensorBarometricPressure(SensorActor):
    def __init__(self):
        super().__init__(BarometricPressureSensor)
        
    """! @brief Barimetric pressure sensor representation """
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes barimetric pressure sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A tuple in the order of pressure and temperature. The values are of 'float' type.  The pressure is in hPa (1 hPa = 1 mbar), the temperature in °C.
        """
        SensorActor._checkSize_(data, 6)
        temperature = int.from_bytes(data[0:3], "little", signed=True)  / 100
        pressure    = int.from_bytes(data[3:6], "little", signed=False) / 100;
        return self.__returnFromDecode__( (float(pressure), float(temperature)) )

class SensorMotion(SensorActor):
    """! @brief Motion sensor (including gyroscope, accelleration and magnetism) representation """
    def __init__(self):
        """! @brief Constructor
            The accelleration sensor, as part of the motion sensor, requires the value of the CONFIG characteristic for value calculation
            of the DATA characteristic. The member 'acceleration config' is to be set by the BLE Sensor Tag client.
        """
        super().__init__(MotionSensor)
        self.config: bytearray = None
        
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes motion sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A 'MotionValues' instance implementing members 'gyroscope', 'accelleration' and 'magnetism' data, each as 'Vector3' having x,y and z properties.
        """
        SensorActor._checkSize_(data, 18)
        # Gyroscope of motion sensor
        gyrX = int.from_bytes(data[0:2], "little", signed=True)  / 32768 * 250
        gyrY = int.from_bytes(data[2:4], "little", signed=True)  / 32768 * 250
        gyrZ = int.from_bytes(data[4:6], "little", signed=True)  / 32768 * 250
        # Acceleration of motion sensor
        if config is None and self.config is None:
            print('Config missing')
            accX = 0
            accY = 0
            accZ = 0
        else:
            if self.config is None:
                self.config = config
            SensorActor._checkSize_(self.config, 2)
            scale = 2**(self.config[1] & 0x3 + 1)
            accX = int.from_bytes(data[6:8], "little", signed=True)    / 32768 * scale
            accY = int.from_bytes(data[8:10], "little", signed=True)   / 32768 * scale
            accZ = int.from_bytes(data[10:12], "little", signed=True)  / 32768 * scale
        # Magnetism of motion sensor
        magX = int.from_bytes(data[12:14], "little", signed=True)  / 32768 * 1000  
        magY = int.from_bytes(data[14:16], "little", signed=True)  / 32768 * 1000
        magZ = int.from_bytes(data[16:18], "little", signed=True)  / 32768 * 1000
        # Result of motion sensor
        return self.__returnFromDecode__( MotionValues(gyrX, gyrY, gyrZ, accX, accY, accZ, magX, magY, magZ) )

    def enableCode(self, enable: bool = True, selection = None) -> bytearray:
        """! @brief Returns the code to be written to the CONFIGURATION characteristic in order to enable measurements
            @parameter selection May be used to selct different kinds of subsensors (service 'MotionSensor')
        """
        if selection:
            raise NotImplementedError("Enabling of subsensors is not provided yet!")
        self._isEnabled = enable
        if enable:
            return bytearray(b'\xFF\x02')
        else:
            return bytearray(b'\x00\x00')        

class SensorOptical(SensorActor):
    """! @brief Optical sensor representation, measuring light intensity """
    def __init__(self):
        super().__init__(OpticalSensor)
        
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes ligth intensity sensor data of the optical sensor
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A 'float' value in Lux
        """
        SensorActor._checkSize_(data, 2)
        val = int.from_bytes(data[0:2], "little", signed=False)
        m = val & 0x0FFF;
        e = (val & 0xF000) >> 12;
        return self.__returnFromDecode__( float(m * (0.01 * 2**e)) )

class SensorInput(SensorActor):
    """! @brief Digital I/O input sensor representation (Simple Key Service)
        The Sensor Tag BLE client must activate the 'Simple key service' after connecting, as input values can only received by notifications.
        Reading the DATA characteristic is not possible!
    """
    def __init__(self):
        super().__init__(InputSensor)
        self._isEnabled = True
        
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes input sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns An 'InputValues' class representing 'userKey', 'powerKey' and 'reedRelai' digital values as 'bool' members
        """
        SensorActor._checkSize_(data, 1)
        return self.__returnFromDecode__( InputValues(data) )

class ActorOutput(SensorActor):
    def __init__(self):
        super().__init__(OutputActor)
        
    def decode(self, data: bytearray, config: bytearray = None) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Decodes input sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns An 'OutputValues' class representing 'ledRed', 'ledGreen' and 'buzzer' digital values as 'bool' members
        """
        SensorActor._checkSize_(data, 1)
        return self.__returnFromDecode__( OutputValues().fromBytearray(data) )

    def encode(self, value: OutputValues, actualData: bytearray = None) -> bytearray:
        """! @brief Decodes input sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns An 'OutputValues' class representing 'ledRed', 'ledGreen' and 'reedRelai' digital values as 'bool' members
        """
        SensorActor._checkSize_(actualData, 1)
        data = int.from_bytes(actualData, 'little')
        if value.ledRed is not None:
            if value.ledRed:
                data = data | 0x01
            else:
                data = data & ~0x01
        if value.ledGreen is not None:
            if value.ledGreen:
                data = data | 0x02
            else:
                data = data & ~0x02
        if value.buzzer is not None:
            if value.buzzer:
                data = data | 0x04
            else:
                data = data & ~0x04
        dataBytes = int.to_bytes(data, 1, 'little')
        self.decode(dataBytes)    # Memorizes a newly written output like having read after writing
        return bytearray(dataBytes)

class Sensors():
    """! @brief Iterable class of all sensor and actor representation instances of a Sensor Tag
        This class is aimed to be a member of a BLE Sensor Tag client. Actors are included as their output state is mostly readable also.
    """
    def __init__(self):
        """! @brief Constructor """
        self.sensorIrTemperature       = SensorIrTemperature()
        self.sensorHumidity            = SensorHumidity()
        self.sensorMotion              = SensorMotion()
        self.sensorBarometricPressure  = SensorBarometricPressure()
        self.sensorOptical             = SensorOptical()
        self.sensorInput               = SensorInput()
        self.actorOutput               = ActorOutput()
        
    def __iter__(self):
        """! @brief Iterates through all sensor representations """
        return [value for value in self.__dict__.values() if isinstance(value, SensorActor)].__iter__()

    def find(self, service: BaseService) -> SensorActor:
        """! @brief Finds the sensor representation instance belonging to the passed service """
        for sensor in self:
            if sensor.service is service:
                return sensor
        raise ValueError(f"The requested service {service.name} is not a Sensor Tag service for reading from sensors!")
       
 
class SensorTag(EasyBleakClient):
    """! @brief Sensor Tag BLE client based on \ref EasyBleakClient """
    def __init__(self, mac: str):
        super().__init__(mac)
        SensorTag.appendServiceDict(sensorTagServices)
        self._sensors = Sensors()
        self.lastException = None
        self.notifySensor(InputSensor, None)
            
    @classmethod
    def services(cls) -> dict:
        """! @brief Returns a dictionary of SensorTag services, only
            This method is equivalent to the 'gatt' property but contains less content. On the other hand, the delivered content
            is appropriate for all application interfacing methods of this class. \n
            The usage is e.g. SensorTag.services()["OpticalSensor"] .
        """
        return sensorTagServices
        
    def readSensor(self, service: BaseService, noExceptions = True) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Reads from a service provided by the Sensor Tag
            You can achieve the services by several ways:
            - use the Sensor Tag class method services like e.g. SensorTag.services()["OpticalSensor"] . SensorTag.services() is a printable 'dict', from which you can receive all availabe sensor service names.
            - Through import from this module e.g. import texas_instruments.OpticalSensor
            - Through your Sensor Tag sensor representation instances property by e.g. using mySensorTag.sensors.sensorOptical.service
            @param service The serivce of the sensor to be read from
            @param noExceptions If 'True' the method captures all exceptions and in case of an exceptions stores the exception in its member 'lastException' and returns 'False'.
            The returned value class type and its physical unit depend on the sensor service (all derived from 'BaseService') chosen:
            - 'IrTemperaturesSensor' service
            @returns A tuple in the order of targeted object temperature and the ambient temperature in °C
            - 'HumiditySensor' service
            @returns A float value of the relative humidity in %RH
            - 'BarometricPressureSensor' service
            @returns A tuple in the order of pressure and temperature. The values are of 'float' type. The pressure is in hPa (1 hPa = 1 mbar), the temperature in °C.
            - 'MotionSensor' service
            @returns A 'MotionValues' instance implementing the members 'gyroscope', 'accelleration' and 'magnetism' each of type 'Vector3' providing x,y and z properties as 'float'. Unit of the gyroscope is deg/s, of the accelleration is G and of the magnetism is uT.
            - 'OpticalSensor' service
            @returns A 'float' value in Lux
            - 'InputSensor' service
            @returns An 'InputValues' class representing 'userKey', 'powerKey' and 'reedRelai' digital values as 'bool' members
            - 'OutputActor'
            @returns An 'OutputValues' class representing 'ledRed', 'ledGreen' and 'buzzer' digital values as 'bool' members
        """
        sensor = self.__checkEnabled__(service)
        data = self.read(service.DATA)
        return sensor.decode(data)     
    
    def writeSensor(self, service: BaseService, value: OutputValues):
        """! @brief Writes to an actor service provided by the Sensor Tag
            - 'OutputActor'
            @param service The only actor service is 'me2grid.devices.texas_instruments.OutputActor'
            @param data An object 'OutputValues' representing 'LEDred', 'LEDgreen', 'buzzer as bool members. Standard value of each member is None to indicate no change on that output.
        """
        sensor = self.__checkEnabled__(service)
        if service is OutputActor:
            prevdata = self.read(OutputActor.DATA)
            data = sensor.encode(value, prevdata)
        else:
            data = sensor.encode(service, value)
        self.write(service.DATA, data)
        return

    def getSensorValue(self, service: BaseService) -> Union[float, tuple, MotionValues, InputValues, OutputValues, None]:
        """! @brief Returns the last memorized value from the passed sensor service
            To return valid values the sensor must have been read using 'readSensor' or notifications must be enabled (with or without a notification handler).
        """
        sensor = self._sensors.find(service)
        return sensor.value        
        
    def enableSensor(self, service: BaseService, enable: bool = True):
        """! @brief Enables or disables the sensor according to 'service' to take measurements
            @param service A sensor service, e.g. out of the 'dict' 'SensorTag.services'
            @param enable 'True' to enable, 'False' to disable
            @returns 'bool' value indicating success
        """
        if not self.is_connected:
            self.connect()
        sensor = self._sensors.find(service)
        if service is not InputSensor:
            cfg = sensor.enableCode(enable)
            self.write(service.CONFIGURATION, cfg)
            if  service is MotionSensor:
                sensor.config = cfg
            time.sleep(1.5)
        
    def readSensorEnabled(self, service: BaseService) -> bool:
        """! @brief Actually reads from the sensor to veryfy if it is enabled to take measurements
            @param service A sensor service, e.g. out of the 'dict' 'SensorTag.services'
            @returns 'bool' value indicating if the sensor is enabled
        """
        self.__checkEnabled__(service)
        data = self.write(service.CONFIGURATION)
        return (int(data) & int(disabledMask(service))) != 0

    def isSensorEnabled(self, service: BaseService) -> bool:
        """! @brief Reads from the memorized enabled state
            @param service A sensor service, e.g. out of the 'dict' 'SensorTag.services'
            @returns 'bool' value indicating if the sensor is enabled
        """
        sensor = self._sensors.find(service)
        return sensor.enabled

    def writeSensorPeriod(self, service: BaseService,  periodTime: float) -> bool:
        """! @brief Sets the measurement period time for the sensor according to 'service' (ranges from 0.1s to 2.55s)
            @returns 'bool' value indicating success
        """
        self.__checkEnabled__(service)
        return self.write(service.PERIOD, SensorActor._codePeriodTime_(periodTime))

    def readSensorPeriod(self, service: BaseService,  periodTime: float) -> bool:
        """! @brief Sets the measurement period time for the sensor according to 'service' (ranges from 0.1s to 2.55s)
            @returns 'bool' value indicating success
        """
        self.__checkEnabled__(service)
        return SensorTag._decodePeriodTime(self.read(service.PERIOD))

    def notifySensor(self, service: BaseService, notificationHandler) -> bool:
        """! @brief Enales notifications from the passed sensor service and sets the appropriate notification handler
            If 'None' is passed as 'notificationHandler' the notifications will be collected by the Sensor Tag client and received values are stored.
            These values can be accessed using the method getSensor().
            @param service A sensor service, e.g. out of the 'dict' 'SensorTag.services'
            @param notificationHandler A method or function delegate accepting a single parameter of type Union[float, tuple, MotionValues, None] delivering the sensor value similar to the 'readSensor' method
            @returns 'bool' value indicating success
        """
        sensor = self.__checkEnabled__(service)
        self.start_notify(service.DATA, sensor._OnNotification_)
        sensor._setNotificationHandler_(notificationHandler)
               
    def stopNotifySensor(self, service: BaseService) -> bool:
        """! @brief Disables notifications from the passed sensor service
            @param service A sensor service, e.g. out of the 'dict' 'SensorTag.services'
            @returns 'bool' value indicating success
        """
        sensor = self.__checkEnabled__(service)
        if service is not InputSensor:
            self.stop_notify(service.DATA)
        sensor._setNotificationHandler_(None)
        return True
   
    def __checkEnabled__(self, service) -> SensorActor:
        """! @brief Checks, whether the device is connected and the passed service already has been enabled and returns the corresponding 'SensorActor' instance """ 
        if not self.is_connected:
            self.connect()
        sensor = self._sensors.find(service)
        if not sensor.isEnabled:
            if service is OutputActor:
                self.write_gatt_char(OutputActor.DATA.uuid, b'\x00')
            self.enableSensor(service)
        return sensor

def gettingStarted():
    tag = SensorTag('54:6C:0E:52:C7:84')
    print("Connecting")
    tag.connect()
    print("Enabling optical sensor")
    tag.enableSensor(SensorTag.services()['OpticalSensor'])
    print("Reading light intensity from optical sensor")
    light = tag.readSensor(SensorTag.services()['OpticalSensor'])
    print(f"{light} Lux")
    print("Disconnecting")
    tag.disconnect()
    print("Ready")

if __name__ == '__main__':
    
    # inputUUID = '0000ffe1-0000-1000-8000-00805f9b34fb'

    # def myOnNotify(sender, data):
    #    print("Notification from {0}: {1}".format(sender, data))
    
    gettingStarted()
    
