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

@section Requirements

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
#from enum import IntEnum
#from datetime import datetime, timedelta

from .BibPi.mathlib.Vector3 import Vector3

try: # Necessary, to run this file directly
    from .easybleak.EasyBleakClient import EasyBleakClient
    from .easybleak.gatt import BLE_UUID
except:
    from me2grid.easybleak.EasyBleakClient import EasyBleakClient
    from me2grid.easybleak.gatt import BLE_UUID

# TI SensorTag specific predifined services
def TI_UUID(val: int):
    """ @brief Transforms a 16bit Texas Instruments specific uuid integer value to a full uuid string """
    return UUID("f000%04x-0451-4000-b000-000000000000" % val)

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

class Input(BaseService):
    """! @brief Service enumeration of characteristics within the 'Simple Key Service' """
    DATA           = CharacteristicType(BLE_UUID(0xffe1))  #!> IO input data (Notification only! no read possible): bit0: left key (user button), bit1: right key (power button), bit2: reed relay

    @classmethod
    def uuidService(cls) -> str:
        return BLE_UUID(0xffe0)

class Output(BaseService):
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

class MotionData():
    """ @brief Contains the measurement data of the movement sensor
        Accessable members are gyroscope, acceleration and magnetism, providing the members x, y and z each.
    """
    def __init__(gyroX: float, gyroY: float, gyroZ: float, accX: float, accY: float, accZ: float, magX: float, magY: float, magZ: float):
        self.gyroscope = Vector3(gyroX, gyroY, gyroZ)
        self.acceleration = Vector3(accX, accY, accZ)
        self.magnetism = Vector3(magX, magY, magZ)
 
class Sensor():
    """! @brief Base class for different types of sensor representations """
    def __init__(self, myService: BaseService):
        self.myService = myService         #!> Defines the service the derived classes are designed for
        self.applicationHandler = None     #!> Delegate to the application method handling the sensor notofication. applicationHandler(data: Union[float, tuple, MovementData])

    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief \b virtual Method for derived classes to return calculated sensor values from the passed data bytearray
            Derived classes must set the member 'myService' and the method implementation must call this base method to check if the passed
            service fits the service the derived class is designed for.
            @param service An arbitrary 'BaseService' derived BLE service description object
            @param data 'bytearray' received from the sensor DATA characteristc of the passed service
            @param config Optional 'bytearray' received from the sensor CONFIG characteristc of the passed service
            @returns The calculated sensor data in case the passed service fits the service the derived class is derived for. 'None' otherwise.
        """
        if service is not self.myService
            return None
        
    def encode(self, service: BaseService, value: Union[EnumOutput, tuple(EnumOutput)], actualData: bytearray = None) -> bytearray:
        """! @brief \b virtual Method for derived classes to return the dataarray for the BLE communication from passed 'sensor' output values
            @param service An arbitrary 'BaseService' derived BLE service description object
            @param value Value to be written to the actor ('sensor') defined by the 'service' parameter 
            @param actualData 'bytearray' received from the sensor DATA characteristc of the passed service
            @returns The 'bytearray' to be written to the DATA characteristc of the passed service in case the passed service fits the service the derived class is derived for. 'None' otherwise.
        """
        raise NotImplementedError(f"Writing to service {str(service)} is not implemented: Writing to sensors is not possible, choose an actuator")
    
    def __OnSensor__(self, data: bytearray) -> Union[float, tuple, MovementData, None]:
        """! @brief Handler method for sensor notifications to be passed to the BLE client on 'start_notify'"""
        if self.applicationHandler is not None:
            self.applicationHandler          (self.decode(self.myService, data))
            
    def __setNotificationHandler__(handlerMethod):
        """! @brief To be called from the BLE client applicatoin interface method 'start_notify' in order to set the application callback handler for this sensor """
        self.applicationHandler = handlerMethod
    
class SensorIrTemperature(Sensor)
    """! @brief IR temperature sensor representation """
    zeroC = 273.15 # Kelvin
    tRef  = 298.15
    S0 = 6.4e-14
    Apoly = [1.0,      1.75e-3, -1.678e-5]
    Bpoly = [-2.94e-5, -5.7e-7,  4.63e-9]
    Cpoly = [0.0,      1.0,      13.4]

    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief Decodes ir temperature sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @returns A tuple with targeted object temperature and the ambient temperature in °
        """
        if super().decode(service, data) is None:
            return None
        BaseSensorTag._checkSize_(data, 4)
        rawVobj = int.from_bytes(data[0:2], "little", signed=False)
        rawTamb = int.from_bytes(data[2:4], "little", signed=False)

        tAmb = rawTamb / 128.0
        Vobj = 1.5625e-7 * rawVobj
        tDie = tAmb + SensorIrTemperature.zeroC
        S    = S0 * __calcPoly__(SensorIrTemperature.Apoly, tDie-tRef)
        Vos  = __calcPoly__(SensorIrTemperature.Bpoly, tDie-tRef)
        fObj = __calcPoly__(SensorIrTemperature.Cpoly, Vobj-Vos)
        tObj = math.pow( math.pow(tDie, 4.0) + (fObj/SensorIrTemperature.S), 0.25 ) - SensorIrTemperature.zeroC
        
        return (float(tObj), float(tAmb))

class SensorHumidity(Sensor)
    """! @brief Humidity sensor representation """
    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief Decodes humidity sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @return A float value of the relative humidity in %RH
        """
        BaseSensorTag._checkSize_(data, 4)
        return float(int.from_bytes(data[2:4], "little", signed=False) / 65536 * 100)

class SensorBarimetricPressure(Sensor)
    """! @brief Barimetric pressure sensor representation """
    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief Decodes barimetric pressure sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @return A tuple in the order of pressure and temperature. The values are of 'float' type.  The pressure is in hPa (1 hPa = 1 mbar), the temperature in °C.
        """
        BaseSensorTag._checkSize_(data, 6)
        temperature = int.from_bytes(data[0:3], "little", signed=True)  / 100
        pressure    = int.from_bytes(data[3:6], "little", signed=False) / 100;
        return (float(pressure), float(temperature))

class SensorMotion(Sensor)
    """! @brief Motion sensor (including gyroscope, accelleration and magnetism) representation """
    def __init(self):
        """! @brief Constructor
            The accelleration sensor, as part of the motion sensor, requires the value of the CONFIG characteristic for value calculation
            of the DATA characteristic. The member 'accelerationConfig' is to be set by the BLE Sensor Tag client.
        """
        self.config: bytearray = None
        
    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief Decodes motion sensor data
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @return A 'MotionData' instance implementing members 'gyroscope', 'accelleration' and 'magnetism' data, each as 'Vector3' having x,y and z properties.
        """
        BaseSensorTag._checkSize_(data, 6)
        # Gyroscope of motion sensor
        gyrX = int.from_bytes(data[0:2], "little", signed=True)  / 32768 * 250
        gyrY = int.from_bytes(data[2:4], "little", signed=True)  / 32768 * 250
        gyrZ = int.from_bytes(data[4:6], "little", signed=True)  / 32768 * 250
        # Acceleration of motion sensor
        if config is None:
            if self.config is None:
                accX = 0
                axxY = 0
                accZ = 0
        else:
            self.config = config
        SensorTag._checkSize_(self.config, 2)
        scale = 2**(self.config[1] & 0x3 + 1)
        accX = int.from_bytes(data[6:8], "little", signed=True)    / 32768 * scale
        accY = int.from_bytes(data[8:10], "little", signed=True)   / 32768 * scale
        accZ = int.from_bytes(data[10:12], "little", signed=True)  / 32768 * scale
        # Magnetism of motion sensor
        magX = int.from_bytes(data[12:14], "little", signed=True)  / 32768 * 1000  
        magY = int.from_bytes(data[14:16], "little", signed=True)  / 32768 * 1000
        magZ = int.from_bytes(data[16:18], "little", signed=True)  / 32768 * 1000
        # Result of motion sensor
        return MotionData[gyrX, gyrY, gyrZ, accX, accY, accZ, magX, magY, magZ]

class SensorOptical(Sensor)
    """! @brief Optical sensor representation, measuring light intensity """
    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData, InputData, OutputData, None]:
        """! @brief Decodes ligth intensity sensor data of the optical sensor
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            @return A 'float) value in Lux
        """
        SensorTag._checkSize_(data, 2)
        val = int.from_bytes(data[0:2], "little", signed=False)
        m = val & 0x0FFF;
        e = (val & 0xF000) >> 12;
        return float(m * (0.01 * 2**e))



    def decode(self, service: BaseService, data: bytearray, config: bytearray = None) -> Union[float, tuple, MovementData]:
        """ @brief Decoding a received uuid and bytearray to a service and appropriate calculated data
            To be called after a read operation of the BLE client in order to decode the bytearray virtual Method to be implemented by a subclassing BLE client
            @param service The sensor service linked to the data bytearray
            @param data The data bytearray to be decoded
            The returned sensor measurement differ according to the passed sensor service class.
            - IrTemperatureSensor
            - HumiditySensor
            - BarometricPressureSensor
            
        """
        if isinstance(sensor, IrTemperatureSensor):
            
        if isinstance(sensor, HumiditySensor):
    
        if isinstance(sensor, BarometricPressureSensor):

        if isinstance(sensor, MotionSensor):

        if isinstance(sensor, MotionSensor):

#,Input, Output

        raise ValueError(f"An unimplemented sensor service type {sensor.__class__} has been passed!")
        return None
    
class BaseSensorTag():
    """! @brief Class implementing the Sensor Tag functionality
        This class is programmed to be independent of the blue tooth client used to connect to the Sensor Tag device.
        Clients shall subclass from BaseSensorTag.
    """
    # virtual class
    def write_SensorTag(self, uuid: str, data: bytearray):
        """ @brief \b virtual Method to be implemented by a subclassing BLE client """
        raise NotImplementedError()
    
    # virtual class
    def start_notify_SensorTag(self, uuid: str, notificationHandler):
        """ @brief \b virtual Method to be implemented by a subclassing BLE client """
        raise NotImplementedError()

    # virtual class
    def start_notify_SensorTag(self, uuid: str):
        """ @brief \b virtual Method to be implemented by a subclassing BLE client """
        raise NotImplementedError()
    
    # Class methods for easy sensor service access
    @staticmethod
    def IrTemperatureSensor()
        return IrTemperatureSensor

    def __calcPoly__(coeffs, x):
        """ @brief \b private Calculates a polynom interpolated value """
        return coeffs[0] + (coeffs[1]*x) + (coeffs[2]*x*x)

    @staticmethod
    def _checkSize_(data, expectedSize: int):
        if data is None:
            raise ValueError()
        if  len(data)!=expectedSize:
            raise ValueError()
    
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
        SensorTag._checkSize_(rawTime, 1)
        t = int.from_bytes(rawTime, "little", signed=False)
        return float(t)/100.0
        
    def enableIrTemperature(self, on: bool = True):
        """ \brief Activates or deactivates the infrared (and ambient) temperature measurements
        """
        data = bytearray(1)
        if on:
            data[0] = 0x01
        else:
            data[0] = 0x00
        self.write(self.charUUID_IR_TEMPERATURE_CONFIG, data)

    def isEnabledIrTemperature(self) -> bool:
        """ \brief Cecks for the infrared (and ambient) temperature measurements being active
        """
        return self.read(self.charUUID_IR_TEMPERATURE_CONFIG) == b'\x01'

    def writePeriodIrTemperature(self, periodTime: float):
        """! @brief Sets the measurement period time for humidity / sec (ranges from 0.1s to 2.55s)"""
        self.write(self.charUUID_IR_TEMPERATURE_PERIOD, SensorTag._codePeriodTime_(periodTime))

    def readPeriodIrTemperature(self) -> float:
        """! @brief Reads the measurement period time for humidity / sec """
        return SensorTag._decodeCycleTime_(self.read(self.charUUID_IR_TEMPERATURE_PERIOD))
    
    def enableMagnetism(self, on: bool = True):
        """ \brief Enables or disables magnetic measurements """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)

        if on:
            data[0] = data[0] | 0x40
        else:
            data[0] = data[0] & ~0x40
        self.write(self.charUUID_MOTION_CONFIG, data)

    def isEnabledMagnetism(self) -> bool:
        """ \brief Cecks for enabled magnetic measurements """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)
        return  (data[0] & 0x40) != 0

    def enableGyroscope(self, on: bool = True):
        """ \brief Enables or disables gyroscope measurements """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)

        if on:
            data[0] = data[0] | 0x07
        else:
            data[0] = data[0] & ~0x07
        self.write(self.charUUID_MOTION_CONFIG, data)

    def isEnabledGyroscope(self) -> bool:
        """ \brief Cecks for enabled magnetic measurements """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)
        return  (data[0] & 0x07) != 0

    def enableAcceleration(self, on: bool = True, sensitvity: int = 2):
        """ \brief Enables or disables acceleration measurements and sets a sensitivity (scale) 0=2G, 1=4G, 2=8G, 3=16G  """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)

        if on:
            data[0] = data[0] | 0x38
        else:
            data[0] = data[0] & ~0x38
        self.write(self.charUUID_MOTION_CONFIG, data)

    def isEnabledAcceleration(self):
        """ \brief Checks for enabled accelleration measurements and returns the chosen sensitivity """
        data = self.read(self.charUUID_MOTION_CONFIG)
        SensorTag._checkSize_(data, 2)
        enable = (data[0] & 0x07) != 0
        sens = (data[1] & 0x03)
        return enable, sens
    
    def writePeriodMagnetism(self, periodTime: float):
        """! @brief Sets the measurement Period time for magnetism / sec (ranges from 0.1s to 2.55s) """
        self.write(charUUID_MOTION_CYCLE, SensorTag._codePeriodTime(periodTime))

    def readPeriodMagnetism(self) -> float:
        """! @brief Reads the measurement period time for magnetism / sec """
        return SensorTag._decodePeriodTime(self.read(charUUID_MOTION_PERIOD))
    
    def writePeriodGyroscope(self, periodTime: float):
        """! @brief Sets the measurement period time for gyroscope / sec (ranges from 0.1s to 2.55s) """
        self.writePeriodMagnetism(periodTime)

    def readPeriodGyroscope(self) -> float:
        """! @brief Reads the measurement period time for gyroscope / sec """
        return self.readPeriodMagnetism()
    
    def writePeriodAcceleration(self, periodTime: float):
        """! @brief Sets the measurement cycle time for humidity / sec (ranges from 0.1s to 2.55s) """
        self.writePeriodMagnetism(periodTime)

    def readPeriodAcceleration(self) -> float:
        """! @brief Reads the measurement period time for humidity / sec """
        return self.readPeriodMagnetism()
    
    def enableHumidity(self, on: bool = True):
        """ \brief Enables or disables magnetic measurements """
        data = b'\x00'
        if on:
            data = b'\x01'
        self.write(self.charUUID_HUMIDITY_CONFIG, data)

    def isEnabledHumidity(self) -> bool:
        """ \brief Cecks for enabled magnetic measurements """
        return self.read(self.charUUID_HUMIDITY_CONFIG) == b'\x01'

    def writePeriodHumidity(self, periodTime: float):
        """! @brief Sets the measurement period time for humidity / sec (ranges from 0.1s to 2.55s)"""
        self.write(charUUID_HUMIDITY_CYCLE, SensorTag._codeCycleTime(periodTime))

    def readPeriodHumidity(self) -> float:
        """! @brief Reads the measurement cycle time for humidity / sec """
        return SensorTag._decodeCycleTime(self.read(charUUID_HUMIDITY_CYCLE))
    
    def enableTemperature(self, on: bool = True):
        """ \brief Enables or disables temperature measurements """
        self.enableHumidity(on)

    def isEnabledTemperature(self) -> bool:
        """ \brief Cecks for enabled temperature measurements """
        return self.isEnabledHumidity(self, on)

    def readTemperature(self):
        """! @brief Retreives the temperature measurement value / °C """
        data = self.read(self.charUUID_HUMIDITY_DATA)
        SensorTag._checkSize_(data, 4)
        
        return int.from_bytes(data[0:2], "little", signed=False) / 65536 * 165 - 40;
    
    def writePeriodTemperature(self, periodTime: float):
        """! @brief Sets the measurement period time for temperature / sec (ranges from 0.1s to 2.55s)"""
        self.writePeriodHumidity(periodTime)

    def readPeriodTemperature(self) -> float:
        """! @brief Reads the measurement period time for temperature / sec """
        return self.readPeriodHumidity()
    
    def enableBarometricPressure(self, on: bool = True):
        """ \brief Enables or disables barometric pressure measurements """
        data = b'\x00'
        if on:
            data = b'\x01'
        self.write(self.charUUID_BAROMETRICPRESSURE_CONFIG, data)

    def isEnabledBarometricPressure(self) -> bool:
        """ \brief Cecks for enabled barometric pressure measurements """
        return self.read(self.charUUID_BAROMETRICPRESSURE_CONFIG) == b'\x01'

    def writePeriodBarometricPressure(self, periodTime: float):
        """! @brief Sets the measurement period time for barometric pressure / sec (ranges from 0.1s to 2.55s)"""
        self.write(self.charUUID_BAROMETRICPRESSURE_PERIOD, SensorTag._codePeriodTime(periodTime))

    def readPeriodBarometricPressure(self) -> float:
        """! @brief Reads the measurement period time for barometric pressure / sec """
        return SensorTag._decodePeriodTime(self.read(self.charUUID_BAROMETRICPRESSURE_PERIOD))
    
    def enableLightIntensity(self, on: bool = True):
        """ \brief Enables or disables magnetic measurements """
        data = b'\x00'
        if on:
            data = b'\x01'
        self.write(self.charUUID_LIGHTINTENSITY_CONFIG, data)

    def isEnabledLightIntensity(self) -> bool:
        """ \brief Cecks for enabled light intensity measurements """
        return self.read(self.charUUID_LIGHTINTENSITY_CONFIG) == b'\x01'

    def writePeriodLightIntensity(self, periodTime: float):
        """! @brief Sets the measurement period time for light intensity / sec (ranges from 0.1s to 2.55s)"""
        self.write(self.charUUID_LIGHTINTENSITY_CYCLE, SensorTag._codeCycleTime(periodTime))

    def readPeriodLightIntensity(self) -> float:
        """! @brief Reads the measurement period time for humidity / sec """
        return SensorTag._decodePeriodTime(self.read(self.charUUID_LIGHTINTENSITY_PERIOD))
    
    def enableOutput(self, on: bool = True, resetOutputs: bool = True):
        """ \brief Enables or disables digital output (LED, Buzzer)"""
        data = b'\x00'
        if on:
            data = b'\x01'
        if resetOutputs:
            self.write(self.charUUID_OUTPUT_DATA, b'\x00')
        self.write(self.charUUID_IO_CONFIG, data)

    def isEnabledOutput(self, on: bool = True) -> bool:
        """ \brief Cecks for enabled digital output """
        return self.read(self.charUUID_IO_CONFIG) == b'\x01'

    def readOutput(self) -> int:
        """! @brief Retreives the digital output byte (bit 0: LED red, bit 1: LED green, bit 2: Buzzer) """
        data = self.read(self.charUUID_OUTPUT_DATA)
        SensorTag._checkSize_(data, 1)

        return int(data[0])
    
    def writeLedRed(self, on: bool):
        """! @brief Sets the red LED """
        data = self.readOutput()
        if on:
            data = data | 0x01
        else:
            data = data & ~0x01
        out = bytearray(1)
        out[0] = data
        self.write(self.charUUID_OUTPUT_DATA, out)

    def readLedRed(self) -> bool:
        """! @brief Reads if the red LED is on """
        return (self.readOutput() & 1) == 1

    def writeLedGreen(self, on: bool):
        """! @brief Sets the green LED """
        data = self.readOutput()
        if on:
            data = data | 0x02
        else:
            data = data & ~0x02
        out = bytearray(1)
        out[0] = data
        self.write(self.charUUID_OUTPUT_DATA, out)

    def readLedGreen(self) -> bool:
        """! @brief Reads if the red LED is on """
        return (self.readOutput() & 2) == 2

    def writeBuzzer(self, on: bool):
        """! @brief Sets the buzzer """
        data = self.readOutput()
        if on:
            data = data | 0x04
        else:
            data = data & ~0x04
        out = bytearray(1)
        out[0] = data
        self.write(self.charUUID_OUTPUT_DATA, out)

    def readBuzzer(self) -> bool:
        """! @brief Reads if the red LED is on """
        return (self.readOutput() & 4) == 4

if __name__ == '__main__':
    
    inputUUID = '0000ffe1-0000-1000-8000-00805f9b34fb'

    def myOnNotify(sender, data):
        print("Notification from {0}: {1}".format(sender, data))
    
    tag = SensorTag('54:6C:0E:52:C7:84')
    print("Connecting")
    tag.connect()
    tag.registerNotification(SensorTag.charUUID_INPUT_DATA, myOnNotify)
    #tag.enableNotification(SensorTag.charUUID_INPUT_DATA)
    print("Reading data")
    print(tag.readModel())
    print("Light intensity measurement")
    tag.enableLightIntensity()
    tag.getNotifications(1) # Just a creation of a time delay to let the sensor start up
    print(str(tag.readLightIntensity()) + " Lux")
    print("Waiting for notifications. Press user key on the SensorTag!")
    tag.getNotifications(5)
    print("Disconnecting")
    tag.disconnect()
    print("Ready")
