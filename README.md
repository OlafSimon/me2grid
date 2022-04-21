# me2grid
Energy management for connecting your home to the electrical grid

## Library usage
To use the Python 'me2grid' library create a working folder on your computer. The library itself consists of the folder 'me2grid' which is placed inside the 'library' folder. Copy the complete folder 'me2grid' to your working folder.

The folder 'library' also contains sample files which you can copy also, if you like.

## Library content
The 'me2grid' library consists of several sub libraries. These are organized in different sub folders inside the main library folder 'me2grid'.

1. ['easybleak' BLE client library](#'easybleak'-ble-client-library)
2. ['devices' library](#'devices'-library)
   - - [Texas Instruments Sensor Tag](#texas-instruments-sensor-tag)
   - - [Radiator valve](#radiator-valve)

## 'easybleak' BLE client library
The 'easybleak' library provides an easy to use 'blue tooth low energy (BLE)' client for Python. It is an extension of the ['bleak' library](https://bleak.readthedocs.io/en/latest/installation.html) managed by Henrik Blidh and David Lechner.

The name 'bleak' stands for "BLE hardware agnostic Klient". The library is designed to be hardware independend so it can be used on many platforms and operation systems, like you expect it for a hardware independent programming language like python. A second major advantageous feature is the use of the (quasi) asynchronous programming technique based on the 'asyncio' library, optimizing program flow in case of wait situations.

On the other hand the asynchronous programming leads to difficulties for beginners and makes usage on the command line hardly possible. As command line use is a feature expected from Python programmers the 'EasyBleak' library bridges this gap [See: [Difficulties of 'bleak'](#difficulties-of-'bleak')].

### Getting started with the 'EasyBleakClient'

You can start to use the 'EasyBleakClient' with any BLE device.

*I tested on a Texas Instruments Sensor Tag and explanations related to the Sensor Tag may not apply to your device.*

First, install the 'bleak' Python library.

```
pip install bleak
```

Open your Python interpreter and take care the current directory is your working folder holding the library folder 'me2grid'. Also import the 'EasyBleakClient' and the 'DeviceInformationService' objects.

```
>>> import os
>>> os.chdir('<working directory>')

>>> from me2grid.easybleak.EasyBleakClient import EasyBleakClient
>>> from me2grid.easybleak.gatt_services import DeviceInformationService
```

With just two instructions you can communicate with your BLE device. First, create a 'EasyBleakClient' instance passing the bluetooth MAC address to the constructor as string (something like '54:6C:0E:52:C7:84'), then read the model name from the device.

*To do so with the Sensor Tag you need to switch the Sensor Tag into advertising mode by shortly pressing the power button. In case the green LED is flashing, the advertising mode is active. In some cases you need to release the Sensor Tag from connected mode by long pressing the power button (about 6s) before. The Sensor Tag will remain in advertising mode for only a few minutes!*

```
>>> dev = EasyBleakClient('54:6C:0E:52:C7:84')
>>> dev.read(DeviceInformationService.MODEL)
'CC2650 SensorTag'
```

You may even just call 'dev.read()', as reading the 'DiviceInformationService.MODEL' characteristic is the standard initialization of that parameter.

Although just two instructions are involved so far, unlucky handling of the BLE device or the BLE client software already may cause exceptions. As not all of the exception messages are self explaining see section [Exception handling](#exception-handling) for explanations.

### Short BLE introduction
For the further explanations a short introduction to BLE is necessary for your understanding.

Pieces of information like numbers or names (you may also call it data, variables or parameters) are called 'characteristics' in BLE terminology. Several characteristics are grouped into 'services'. A BLE device provides the Generic Attribute Profile (GATT). The GATT provides a list of all services and their dedicated characteristics (We do not need to know about the 'descriptors' dedicated to characteristics). You may have a predefined GATT available e.g. through the device manual providing understandable descriptions or you can read the GATT from the device (which is done by the 'BleakClient' automatically during connecting) but mostly you only receive cryptic non readable information that way.

All 'attributes' (for my understanding denoting services and characteristics all together) are identified by an Universally Unique Identifier (UUID). At the end the UUID addresses the piece of information you want to read or write to. A UUID is usually denoted as a string of grouped hexadecimal values. For excample the UUID of the characteristic 'Model Number String' within the service 'Device Information Service' is "00002a24-0000-1000-8000-00805f9b34fb". UUIDs are often structured by a base UUID and specific 16 bit IDs. The base UUID for BLE attributes is "0000xxxx-0000-1000-8000-00805f9b34fb". At the places of 'xxxx' the specific short 16 bit ID is inserted. The short ID for the 'Model number string' of the excample is '2a24'. Manufacturers of BLE devices often have their own base UUID and manuals often just denote the short 16 bit ID.

In order to avoid handling with the cryptic and long UUIDs the 'EasyBleak' library provides classes for the BLE general services like e.g. the object 'DeviceInformationService' which is an enumeration of all dedicated characteristics. BLE devices supported by the 'me2grid.devices' library additionally provide service objects for the device specific services.

### Exploring your BLE device
* Exploring the predifined GATT provided by the library

We already used the BLE service object 'DeviceInformationService'. All BLE service objects are static objects, thus you can use their content without creating an instance in advance. To learn about the characteristics accessible by the 'Device Information Service' just use the Python function 'list'. In order to receive a more compact information call the class method 'characteristics()'.

```
>>> list(DeviceInformationService)
[<DeviceInformationService.SYSTEM_ID: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe190>>, <DeviceInformationService.MODEL: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe2d0>>, <DeviceInformationService.SERIAL: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe2b0>>, <DeviceInformationService.FIRMWARE: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe310>>, <DeviceInformationService.HARDWARE: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe330>>, <DeviceInformationService.SOFTWARE: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe370>>, <DeviceInformationService.MANUFACTURER: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe3b0>>, <DeviceInformationService.IEEE_CERT: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe3d0>>, <DeviceInformationService.PNP_ID: <me2grid.easybleak.gatt.CharacteristicType object at 0x756fe3f0>>]

>>> DeviceInformationService.characteristics()
['SYSTEM_ID', 'MODEL', 'SERIAL', 'FIRMWARE', 'HARDWARE', 'SOFTWARE', 'MANUFACTURER', 'IEEE_CERT', 'PNP_ID']
```

If you like to know the UUID of a certain charakteristic use the 'uuid' property. For the UUID of a service call the 'uuidService()' class method.

```
>>> DeviceInformationService.MODEL.uuid
'00002a24-0000-1000-8000-00805f9b34fb'

>>> DeviceInformationService.uuidService()
'0000180a-0000-1000-8000-00805f9b34fb'
```

You probably do not know all available services of a BLE device in advance. Therefore, to really explore your device client you need to view the GATT. Each BLE client provided by the 'easybleak' library, like 'EasyBleakClient', 'ExtBleakClient' or all devices from the 'devices' library like 'SensorTag', contain the predefined attribute profile (GATT) as static information accessible through the class name using the 'gatt()' method (For convenience you can also use the instance name). This method returns a dictionary of GATT services providing the service names as keys and the service classes as values. Printing the GATT gives a deeper insight as the library reference and dedicated characteristics are listed, also.

```
>>> EasyBleakClient.gatt()
{'GenericAccessService': <enum 'GenericAccessService'>, 'GenericAttributeProfileProfile': <enum 'GenericAttributeProfileService'>, 'GenericDescriptors': <enum 'GenericDescriptors'>, 'DeviceInformationService': <enum 'DeviceInformationService'>}

>>> EasyBleakClient.gatt().keys()
dict_keys(['GenericAccessService', 'GenericAttributeProfileProfile', 'GenericDescriptors', 'DeviceInformationService'])

>>> print(EasyBleakClient.gatt())
<dict 'me2grid.easybleak.gatt.ClassServices' {
 'GenericAccessService':<enum 'me2grid.easybleak.gatt_services.GenericAccessService' ['DEVICE', 'PREFERRED_CONNECTION']>
 'GenericAttributeProfileService':<enum 'me2grid.easybleak.gatt_services.GenericAttributeProfileService' ['SERVICE_CHANGED']>
 'GenericDescriptors':<enum 'me2grid.easybleak.gatt_services.GenericDescriptors' ['CLIENT_CHAR_CONFIG']>
 'DeviceInformationService':<enum 'me2grid.easybleak.gatt_services.DeviceInformationService' ['SYSTEM_ID', 'MODEL', 'SERIAL', 'FIRMWARE', 'HARDWARE', 'SOFTWARE', 'MANUFACTURER', 'IEEE_CERT', 'PNP_ID']>
}>
```

To gain read access to a characteristic of a device there are two options of programming as shown below. The first one is the way we already used by importing the service object. In case you don't like the import, you can use the 'gatt()' dictionary instead as the second option.

```
>>> from me2grid.easybleak.gatt_services import DeviceInformationService
>>> dev.read(DeviceInformationService.MODEL)
'CC2650 SensorTag'

>>> dev.read(EasyBleakClient.gatt()['DeviceInformationService'].MODEL)
'CC2650 SensorTag'
```

* Exploring the GATT provided by the device itself

In case you are using the 'EasyBleakClient' for exploring a BLE device that has no specific client provided in the 'me2grid.devices' library, the predefined services of the 'EasyBleakClient' only cover the BLE standard services. We cannot expect device specific services being predefined.

For such cases the 'BleakClient' form the 'bleak' library reads the GATT content from the device during connecting to it. The read GATT content is stored in a member called 'services'. 'EasyBleakClient' (as well as 'ExtBleakClient') provides the method 'printServices' to easily view the devices GATT. *(The output of the following excample is shortened as the SensorTag has very many services)*

```
>>> dev.printServices()
[Service] -> f000ffc0-0451-4000-b000-000000000000: Unknown
	[Characteristic] f000ffc4-0451-4000-b000-000000000000: (Handle: 0x6F) (read,notify) | Name: Unknown, Value: -unread- 
		[Descriptor] 00002901-0000-1000-8000-00805f9b34fb: (Handle: 0x72) | Value: -unread- 
		[Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 0x71) | Value: -unread- 
	[Characteristic] f000ffc3-0451-4000-b000-000000000000: (Handle: 0x6C) (write-without-response,write) | Name: Unknown, Value: -unread- 
		[Descriptor] 00002901-0000-1000-8000-00805f9b34fb: (Handle: 0x6E) | Value: -unread- 
	[Characteristic] f000ffc2-0451-4000-b000-000000000000: (Handle: 0x68) (write-without-response,write,notify) | Name: Unknown, Value: -unread- 
		[Descriptor] 00002901-0000-1000-8000-00805f9b34fb: (Handle: 0x6B) | Value: -unread- 
		[Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 0x6A) | Value: -unread- 
	[Characteristic] f000ffc1-0451-4000-b000-000000000000: (Handle: 0x64) (write-without-response,write,notify) | Name: Unknown, Value: -unread- 
		[Descriptor] 00002901-0000-1000-8000-00805f9b34fb: (Handle: 0x67) | Value: -unread- 
		[Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 0x66) | Value: -unread- 
[Service] -> f000ccc0-0451-4000-b000-000000000000: Unknown
	[Characteristic] f000ccc3-0451-4000-b000-000000000000: (Handle: 0x61) (write) | Name: Unknown, Value: -unread- 
	[Characteristic] f000ccc2-0451-4000-b000-000000000000: (Handle: 0x5F) (write) | Name: Unknown, Value: -unread- 
	[Characteristic] f000ccc1-0451-4000-b000-000000000000: (Handle: 0x5C) (read,notify) | Name: Unknown, Value: -unread- 
		[Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 0x5E) | Value: -unread- 
[Service] -> 0000180a-0000-1000-8000-00805f9b34fb: Device Information
	[Characteristic] 00002a50-0000-1000-8000-00805f9b34fb: (Handle: 0x1A) (read) | Name: PnP ID, Value: -unread- 
	[Characteristic] 00002a2a-0000-1000-8000-00805f9b34fb: (Handle: 0x18) (read) | Name: IEEE 11073-20601 Regulatory Cert. Data List, Value: -unread- 
	[Characteristic] 00002a29-0000-1000-8000-00805f9b34fb: (Handle: 0x16) (read) | Name: Manufacturer Name String, Value: -unread- 
	[Characteristic] 00002a28-0000-1000-8000-00805f9b34fb: (Handle: 0x14) (read) | Name: Software Revision String, Value: -unread- 
	[Characteristic] 00002a27-0000-1000-8000-00805f9b34fb: (Handle: 0x12) (read) | Name: Hardware Revision String, Value: -unread- 
	[Characteristic] 00002a26-0000-1000-8000-00805f9b34fb: (Handle: 0x10) (read) | Name: Firmware Revision String, Value: -unread- 
	[Characteristic] 00002a25-0000-1000-8000-00805f9b34fb: (Handle: 0x0E) (read) | Name: Serial Number String, Value: -unread- 
	[Characteristic] 00002a24-0000-1000-8000-00805f9b34fb: (Handle: 0x0C) (read) | Name: Model Number String, Value: -unread- 
	[Characteristic] 00002a23-0000-1000-8000-00805f9b34fb: (Handle: 0x0A) (read) | Name: System ID, Value: -unread- 
```

Whereas the BLE standard service provides meaningful names, the device specific services do not and just state 'Unknown'. At least you know the UUIDs right now and may find descriptions for those in the internet.

In case you pass 'True' as a parameter to the 'printServices' method, each characteristic will actually being read and its value will be printed as an 'bytearray'.

* Finish exploring

If you don't want to do anything else with your device, you need to (or at least should) disconnect from it. You did not explicitly connect to it before, the 'EasyBleakClient' did that for you at the first 'read' instruction.

```
>>> dev.disconnect()
>>>
```

What happens if you do not disconnect depends on your device you are using.

*The Sensor Tag will remain in the connected state (for ever). After restarting your interpreter you will not be able to again connect to the Sensor Tag. The only way is to manually 'reset' the Sensor tag with a long (about 5 s) press on the power key. Afterwards you need to put it in advertising state with a short press on the power key.*

Other devices (like the radiator valve) behave different. They release from the connected state automatically after a certain time of inactivity (few minutes). On the one hand this is a practical behavior as missed disconnects do not require manual actions. On the other hand, in case a program want to keep connected but has long inactivity before a next read instruction, this instruction will fail, as the device is not connected anymore. The 'easybleak' clients can deal with such an behavior as they will automatically reconnect in such cases.

### Recommended usage
Connecting to a device is typically a time consuming task of several seconds. You probably don't want the read instruction taking so much time at first usage as this might disturb your program flow. Second, in case you do not explicitly connect your device you will tend to forget to disconnect from it.

Therefore, the following use with an explicit connect is recommended.

```
>>> from me2grid.easybleak.EasyBleakClient import EasyBleakClient
>>> from me2grid.easybleak.gatt_services import DeviceInformationService
>>> dev = EasyBleakClient('54:6C:0E:52:C7:84')
>>> dev.connect()
>>> dev.read(DeviceInformationService.MODEL)
'CC2650 SensorTag'
>>> dev.disconnect()
>>>
```

You can do this by using the context manager, also.

```
>>> from me2grid.easybleak.EasyBleakClient import EasyBleakClient
>>> from me2grid.easybleak.gatt_services import DeviceInformationService
>>> with dev as EasyBleakClient('54:6C:0E:52:C7:84'):
        dev.read(DeviceInformationService.MODEL)
'CC2650 SensorTag'
>>>
```

For more and advanced information refer to:
* [Texas Instruments Sensor Tag](#texas-instruments-sensor-tag)
* ['bleak' library](https://bleak.readthedocs.io/en/latest/installation.html) 
* Full documentation (not provided yet)

### The extended 'BleakClient'

The 'easybleak' library provides the object 'ExtBleakClient' you can import from 'me2grid.easybleak.ExtBleakClient'. This extended 'bleak' client is directly derived from 'BleakClient' (and is not a wrapper like the 'EasyBleakClient'). Thus, the asynchronous programming features are kept. 

Nevertheless, the following useful extensions are provided:

#### Predefined GATT by readable services, represented as enumerations of characteristics

To receive a more readable code for characteristic access, enumerations for each service are provided. Use the static 'gatt()' method to receive a dictionary of named services and their enumeration classes representing the dedicated characteristics. The usage is identical with the 'EasyBleakClient' as described in [Exploring your BLE device](#exploring-your-ble-device).         

In case you know a characteristic e.g. from a manual you can search for the corresponding readable enumeration (The use of 'EasyBleakClient' is possible, as well):
        
```
>>> from me2grid.easybleak.ExtBleakClient import ExtBleakClient
>>> service = EasyBleakClient.fromUUID("0000180a-0000-1000-8000-00805f9b34fb")
>>> print(service)
>>> print(service.toString())

>>> characteristic = EasyBleakClient.fromUUID("00002a24-0000-1000-8000-00805f9b34fb")
>>> print(characteristic)
>>> print(characteristic.uuid)
```

#### Printing of the Services actually present within the device
The method 'printServices()' of 'ExtBleakClient' (and 'EasyBleakClient) prints all content provided from the GATT server of the device. This is the information actually read from the device during the connect procedure. This method delivers a string representation of the 'BleakClient.services' property. See also [Exploring your BLE device](#exploring-your-ble-device).

####  Disconnection safe methods 'read', 'write', 'request' and 'disconnect'
The methods 'read' and 'write' provide an error free access to characteristics. A (single) reconnection will be executed, in case the external device disconnected without notice in the meantime. The methods are functional identical to 'read_gatt_char' and 'write_gatt_char' of the 'BleakClient' base class. In case the reconnection fails an 'EOFError' is raised.

####  The methods 'read' and 'write' use characteristic specific types ('str', 'int')
The 'read' and 'write' methods return with or use the characteristic specific types, instead of just an 'bytearray', in case you specify the uuid parameter by using a 'BaseService' type, which is the the base type of the entities of all service enumeration, such as 'DeviceInformationService.MODEL'. Possible types for the 'data' parameter or the return value can be 'str' or 'int' (or still 'bytearray') just like the characteristic is aimed to represent. (Valid for 'EasyBleakClient' also)

```{.py}
import asyncio
from gatt import DeviceInformationService
from ExtBleakClient import ExtBleakClient

async def main()
    myClient = ExtBleakClient('54:6C:0E:52:C7:84')
    await myClient.connect()
    res = await myClient.read(DeviceInformationService.MODEL)
    print(type(res))   # which will be 'str'
    print(res)         # which will be the string 'CC_RT_BLE' and not just the bytearry b'CC_RT_BLE'!
    await myClient.disconnect()

asyncio.run(main())
```

#### Method 'request'
The 'ExtBleakClient' (and 'EasyBleakClient' as well) deliveres a 'request' method. This method simplifies the communication technique of command and response characteristics as e.g. used by the [Radiator valve](#radiator-valve). In such cases a coded command is written to the command characteristic and the device will response using a notification with a coded result from the response characteristic. If the vendor does not provide a service name for the command and response characteristics, the service shall be called 'RequestService' for device specific client implementations!


### Exception handling
During use of the BLE client software library you may encounter some of the following exceptions. Some causes and	remedial measures for those are explained.

- bleak.exc.BleakError: Device with address 54:6C:0E:52:C7:84 was not found

In this case the Sensor Tag cannot be connected to. It might be out of radio reach or be connected to another client or a previous client has not disconnected. Some devices will automatically disconnect after a few minutes of inactivity.

*The Sensor Tag might be not in advertising state (green LED not flashing). Make a short press on the power key to set it in advertising state. If this does not help, make a long press (5 s) on the power key to release the Sensor Tag from a previous connection. Try to set it to advertising again.*

- AttributeError: 'NoneType' object has no attribute 'call'

This exception arises if the device cannot be connected to because the device has already been connected to earlier from the same client. This exception will usually being prevented as the 'easybleak' clients carry a flag to supervise the connection state and will not try to connect if it is already connected. Under certain circumstances (due to other exceptions) flag and real connection state may not be synchronous any more causing this exception.

- concurrent.futures._base.TimeoutError

Disconnect failed as the device has released from connection state itself, is busy or off.

- EOFError

Occurs by writing or reading to an unconnected device (e.g. if automatic reconnection has failed or original 'BleakClient' methods like 'write_gat_char' have been used.

- bleak.exc.BleakDBusError: [org.bluez.Error.NotSupported] Operation is not supported

Occurs e.g. when writing to a characteristic that is not writable (Message will look different but similar on operating systems other than Linux).

- bleak.exc.BleakDBusError: [org.bluez.Error.Failed] Software caused connection abort

The reason for this exception is yet unclear to me. It seems to occur occasionally during command line usage. Restart the python interpreter.

### Difficulties of 'bleak'
Due to the asynchronous programming technique the 'BleakClient' can barely be used within the command line of the Python interpreter. Especially beginners expect to use objects in the command line and is just "pythonic". The following difficulties arise using the 'BleakClient' in the command line and are overcome by the 'EasyBleakClient'.

The 'asyncio' library recommends the user to run 'async' defined methods by using the 'asyncio.run()' function. Therefore you may try the following in the command line:

```
>>> import asyncio
>>> from bleak import BleakClient
>>> dev = BleakClient('54:6C:0E:52:C7:84')
>>> asyncio.run(dev.connect())
True
>>> asyncio.run(dev.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb"))
Traceback (most recent call last):
  File "<pyshell>", line 1, in <module>
  File "/usr/lib/python3.7/asyncio/runners.py", line 43, in run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.7/asyncio/base_events.py", line 584, in run_until_complete
    return future.result()
  File "/usr/local/lib/python3.7/dist-packages/bleak/backends/bluezdbus/client.py", line 675, in read_gatt_char
    body=[{}],
  File "/usr/local/lib/python3.7/dist-packages/dbus_next/aio/message_bus.py", line 303, in call
    self._call(msg, reply_handler)
  File "/usr/local/lib/python3.7/dist-packages/dbus_next/message_bus.py", line 588, in _call
    self.send(msg)
  File "/usr/local/lib/python3.7/dist-packages/dbus_next/aio/message_bus.py", line 326, in send
    self._writer.schedule_write(msg, future)
  File "/usr/local/lib/python3.7/dist-packages/dbus_next/aio/message_bus.py", line 85, in schedule_write
    self.loop.add_writer(self.fd, self.write_callback)
  File "/usr/lib/python3.7/asyncio/selector_events.py", line 334, in add_writer
    return self._add_writer(fd, callback, *args)
  File "/usr/lib/python3.7/asyncio/selector_events.py", line 284, in _add_writer
    self._check_closed()
  File "/usr/lib/python3.7/asyncio/base_events.py", line 480, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
>>> 
```
The tried procedure fails because 'async' defined coworking methods are operated by a background loop. The 'asyncio.run' function starts such a loop. After the function returns, the started loop may(!) be closed and at the next call of 'asyncio.run' the function may(!) start a new loop. The way the 'BleakClient' is (and has to be) programmed, expects the same background loop running at least in between a connect and a disconnect. Therefore, using 'asyncio.run' in a sequence fails.

You can avoid this issue by using 'asyncio' in the not recommended fashion.

```
>>> import asyncio
>>> from bleak import BleakClient
>>> loop = asyncio.get_event_loop()
>>> dev = BleakClient('54:6C:0E:52:C7:84')
>>> loop.run_until_complete(dev.connect())
True
>>> loop.run_until_complete(dev.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb"))
bytearray(b'CC2650 SensorTag')
>>> loop.run_until_complete(dev.disconnect())
True
>>> 
```

It is OK, but not really easy to use, like you can with 'EasyBleakClient'.

## 'devices' library
The 'me2grid.devices' library is dependent on the 'me2grid.easybleak' library and thus depending on the 'bleak' library.

The library provides specialized BLE client classes for specific devices.

### Texas Instruments Sensor Tag
The Python class 'SensorTag' to be imported from 'me2grid.devices.texas_instruments' is a BLE client representing a Sensor Tag device manufactured by Texas Instruments. It features reading all sensor values in physical SI-units, thus implements the calculation from raw data already. It also supports notification callback methods receiving physical values as well. Key (and reed relai) inputs can be received and LED (and buzzer) output can be controlled.

The 'SensorTag' class is derived from the 'EasyBleakClient' for synchronous programming style. For full understanding refer to the ['easybleak' BLE client library](#'easybleak'-ble-client-library) chapter, please.

#### Getting started with 'SensorTag'
Two imports and two instructions are necessary to read a sensor value. Please, take care the current directory of your Phyton interpreter is the working directory containing the 'me2grid' folder (see: ['easybleak' BLE client library](#'easybleak'-ble-client-library)).

Put the Sensor Tag in advertising mode by a short press on the power key and check if the green LED is flashing. Be aware, the Sensor Tag will stay in this state for just a few minutes. Figure out, which bluetooth MAC address (something like '54:6C:0E:52:C7:84') your device has.

Use the 'SensorTag' class in the command line as follows:

```
>>> from me2grid.sensors.texas_instruments import SensorTag, OpticalSensor
>>> tag = SensorTag('54:6C:0E:52:C7:84')
>>> tag.readSensor(OpticalSensor)
45.34
```

Therefore, your current light intensity is 45.34 Lux!

But there is more than just an optical sensor!

```
>>> SensorTag.sensorServices().keys()
dict_keys(['IrTemperatureSensor', 'HumiditySensor', 'MotionSensor', 'BarometricPressureSensor', 'OpticalSensor', 'InputSensor', 'OutputActor'])
```

Let's import all of these sensor services and read them all. For later use we also import the 'OutputValues' class to have all necessary imports together.

```{.py}
>>> from me2grid.devices.texas_instruments import SensorTag
>>> from me2grid.devices.texas_instruments import IrTemperatureSensor, HumiditySensor, MotionSensor, BarometricPressureSensor, OpticalSensor, InputSensor, OutputActor
>>> from me2grid.devices.texas_instruments import OutputValues

>>> print(tag.readSensor(IrTemperatureSensor)) # (object temperature in °C, die (chip) temperature in °C)
(60.45, 21.5)
>>> print(tag.readSensor(HumiditySensor)) # in %RH (relative humidity)
26.690673828125
>>> motion = tag.readSensor(MotionSensor) # units as printed below
>>> print(motion)
MotionValues(gyroscope=Vector3([-1.5106201171875, 1.0223388671875, 1.0223388671875]) deg/s, acceleration=Vector3([0.02947998046875, 0.015167236328125, 0.12078857421875]) G, magnetism=Vector3([7.99560546875, -4.7607421875, 7.6904296875]) uT)
>>> print(tag.readSensor(BarometricPressureSensor)) # (barometric pressure in hPa = mbar, ambient temperature in °C)
(995.79, 20.92)
>>> print(tag.readSensor(OpticalSensor)) # in Lux
48.56
```

The motion sensor has three sub sensor, thus the measurement values are a little more complex and stored in a 'MotionValue' class. One instance of this class is returned by the 'readSensor(MotionSensor)' method and stored in the variable 'motion'. The 'MotionValue' class has three members called 'gyroscope', 'acceleration' and 'magnetism', thus one member for each sub sensor. Just print the result of a single sub sensor by:

```
>>> print(motion.magnetism)
Vector3([7.99560546875, -4.7607421875, 7.6904296875])
```

You receive a tree dimensional vector indicating the cartesian coordinates. You can access a single coordinate by the properties x, y or z. Sorry, but so far I have not figured out what direction the x-direction is with respect to the Sensor Tag housing.


```
>>> motion.magnetism.x
7.99560546875
```

Maybe you like the spherical coordinates you can access through the properties r, phi and theta or you print them all together. Usually the angles are given in radians but you can also display them in degrees.

```
>>> motion.magnetism.toSpherical()
me2grid.BibPy.mathlib.Vector3.Spherical(r=12.579092497963398, phi=-0.43929930144941143, theta=0.7769811492233477)

>>> motion.magnetism.toSpherical().asDegrees()
'Spherical(r=12.579092497963398, phi=-25.169995916096564, theta=44.517740611722246, degrees=True)'
```

The handling of the digital inputs, the state of the power key, the user key and the reed relay, is a little bit special at the sensor tag. Due to its design you cannot simply read from the 'InputSensor' service (called 'Simple Key Service' by Texas Instruments). It is a "notification only" service. Handling notifications will be explained later. Concerning the 'Simple Key Service' the notification handling is initialised automatically by the 'SensorTag' class.

But, due to the synchronous programming style, you need to explicitly call the method 'getNotifications' in order to let the 'SensorTag' instance handle notifications that came in.

In case the 'SensorTag' instance has received a 'simple key service' notification the resulting input value will be stored in the instance. You can access (or get) this stored value by calling the method 'getSensorValue(InputSensor)'.

To sum up, in order to read a pressed key state through the command line you need to execute the following steps. It is assumed, the Sensor Tag is already connected, which is the case if you previously read a sensor value.

1. Press the user key and do not release it!
2. Call the method 'getNotifications()'
3. Call the method 'getSensorValue()'
4. Release the user key
5. Repeat from step 2 and so on.

Type in the two commands before pressing the user key into the Python interpreter to get fast access to them using the cursor up typing. Do not try with the power key, as a long press on the power key will cause a disconnect of the Sensor Tag.

```
>>> tag.getNotifications()
>>> print(tag.getSensorValue(InputSensor))
InputValues(userKey=False, powerKey=False, reedRelai=False)
>>> # Press and hold the user key
>>> tag.getNotifications()
>>> print(tag.getSensorValue(InputSensor))
InputValues(userKey=True, powerKey=False, reedRelai=False)
>>> # Release the user key
>>> tag.getNotifications()
>>> print(tag.getSensorValue(InputSensor))
InputValues(userKey=False, powerKey=False, reedRelai=False)
```

Input values are returned by an instance of the object 'InputValue'. This object has three members you can access separately.

```
>>> input = tag.getSensorValue(InputSensor)
>>> input.userKey
False
```

To be honest, handling inputs from the Sensor Tag using a program is quite easier than trying it with the command line. Program samples will be given later.

The last thing to check out is the use of the digital output, which can be the red or green LED or the buzzer.

Similar to the digital intput an own 'OutputValues' class is defined to control the digital outputs. The 'OutputValues' class has three members, each of them representing on digital output bit. Theses members are of 'bool' type and are named 'ledReg', 'ledGreen' and buzzer. All members are initialized with 'None', indicating these outputs are not to be changed from their previous state after writing to the output. All members can be set within the constructor of the class.

As the output is not a sensing but an acting task, the according sensor service is named 'OutputActor'. Nevertheless, you can also read from the 'OutputActor' service in case you do know any more what you have written to the output last.

The following commands will set the red LED of the Sensor Tag.

```
>>> out = OutputValues(ledRed = True)
>>> print(out)
OutputValues(ledRed=True, ledGreen=None, buzzer=None)
>>> tag.writeSensor(OutputActor, out)
>>>

>>> out.ledRed = False
>>> tag.writeSensor(OutputActor, out)
>>>
 
```

Now we are ready with the demonstration of the command line usage and should release the Sensor Tag from its connected state by software.

```
>>> tag.disconnect()
>>>
```





### Radiator valve