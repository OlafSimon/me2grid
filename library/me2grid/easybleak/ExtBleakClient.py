# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  ExtBleakClient.py

@section Requirements
- bleak\n
Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html
"""

import asyncio
import bleak

#from enum import Enum
from typing import Union
from uuid import UUID
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak import BleakClient

try: # Necessary, to run this file directly
    from gatt import versionEasyBleak, BaseService, CharacteristicType, ClassServices
    from gatt_services import GenericAccessService, GenericAttributeProfileService, GenericDescriptors, DeviceInformationService
    from gatt import versionEasyBleak, BaseService, CharacteristicType, ClassServices
except:
    from me2grid.easybleak.gatt import versionEasyBleak, BaseService, CharacteristicType, ClassServices
    from me2grid.easybleak.gatt_services import GenericAccessService, GenericAttributeProfileService, GenericDescriptors, DeviceInformationService
    from me2grid.easybleak.gatt import versionEasyBleak, BaseService, CharacteristicType, ClassServices

class GATT_Dict():
    """! @brief This class holds the predifined GATT characteristic of an BLE device
        Call the static \ref gatt method to receive a dictionary of services.
        It is a base class for ExtBleakClient and EasyBleakClient as well.
        @code
        print(ExtBleakClient.gatt)
        @endcode
    """
    __services__ = ClassServices({"GenericAccessService": GenericAccessService, "GenericAttributeProfileProfile": GenericAttributeProfileService, "GenericDescriptors": GenericDescriptors, "DeviceInformationService": DeviceInformationService})

    @classmethod
    def gatt(cls):
        """! @brief \b static Deliveres the predefined GATT (generic attributes) of the device as a dictionary of services with readable enumerations of there characteristics
            As these attributes are predefined, the device may not necessarily implement all these attributs, espessially concerning the generic services.
        """
        return cls.__services__
    
    @classmethod
    def appendServiceDict(cls, serviceDict: ClassServices):
        """! @brief \b static Appents a service dictionary to the GATT_Dict objects dictionary
        """
        cls.__services__ .update(serviceDict)

    @classmethod
    def fromUUID(cls, uuid:str):
        """! @brief Deliveres the enumeration entity or the enumeration itself of a given UUID string """
        for t in cls.__services__.items():
            value = t[1]
            if value.uuidService() == uuid:
                return value
            for char in value:
                if char.uuid == uuid:
                    return char
        return None
    
    @classmethod
    def version(cls):
        return versionEasyBleak

class ExtBleakClient(BleakClient, GATT_Dict):
    """! @brief Extends the BleakClient from the 'bleak' library
         
        The following extensions are privided:

        @ section SEC_GATT Predefined readable services, represented as enumerations of characteristics

        To receive a more readable code for characteristic access, enumerations for each service are provided.
        Use the static \ref gatt method to recieve a dictionary of named services and their enumeration classes
        representing the dedicated characteristics. See the gatt.GATT_Dict class for further information. \n
        The basic usage e.g. for the BLE device client \ref EasyBleakClient and its derived classes is:

        @code{.py}
        from gatt import GATT_Dict
        print(GATT_Dict.gatt()
        
        from EasyBleak import EasyBleak
        print(EasyBleak.gatt())
        service = EasyBleak.gatt()['DeviceInformatonService']
        print(service.toString())
        characteristic = service.MODEL
        print(characteristic.uuid)

        from gatt import DeviceInformationService
        service = DeviceInformationService
        print(service.uuidService())
        characteristic = DeviceInformationService.MODEL
        print(characteristic.uuid)
        @endcode
        
        In case you know a characteristic e.g. from a manual you can search for the corresponding readable enumeration:
        
        @code{.py}
        from gatt import GATT_Dict
        service = GATT_Dict.fromUUID("0000180a-0000-1000-8000-00805f9b34fb")
        print(service)
        characteristic = GATT_Dict.fromUUID("00002a24-0000-1000-8000-00805f9b34fb")
        print(characteristic)
        print(characteristic.uuid)
        @endcode
        
        @ section SEC_PRINTSERVICES Printing of the Services actually present within the device      
        
        The method \ref printServices prints all content provided from the GATT server device. This is the information
        actually read from the device. This method deliveres a string representation of the BleakClient.services property.

        @ section SEC_READWRITE Disconnection safe methods 'read', 'write', 'request' and 'disconnect'

        The methods \ref read and \ref write provide an error free access to characteristics. A (single) reconnection will be executed,
        in case the external device disconnected without notice in the meantime.The methods are functional identical to
        'read_gatt_char' and 'write_gatt_char' of the 'BleakClient' base class. In case the reconnection fails an EOFError
        is raised.

        @ section TYPE_READWRITE The methods 'read' and 'write' use characteristic specific types ('str', 'int') instead of just 'bytearray'.

        In case you specify the uuid parameter as a \ref BaseService, which is the the base type of the entities of
        all service enumeration, such as DeviceInformationService.MODEL, the 'data' parameter or return value can be given or
        are received in the real type like str or int the characteristic is aimed to represent.
        
        @ code{.py}
        import asyncio
        from gatt import DeviceInformationService
        from ExtBleakClient import ExtBleakClient
                
        async def main()
            myClient = ExtBleakClient("00:1A:22:12:0F:87")
            await myClient.connect()
            res = await myClient.read(DeviceInformationService.MODEL)
            print(type(res))   # which will be 'str'
            print(res)         # which will be the string 'CC_RT_BLE' and not just the bytearry b'CC_RT_BLE'!
            await myClient.disconnect()
            
        asyncio.run(main())
        @ endcode
        
        @ section SEC_REQUEST Method 'request'

        The 'ExtBleakClient' deliveres a 'request' method. This method simplifies the communication technique
        of command and response characteristics. In such cases a coded command is written to the command characteristic
        and the device will response with a coded result from the response characteristic. If the vendor does not
        provide a service name for the command and response characteristics, the service shall be called 'RequestServie'! \n
        The property 'gatt' deliveres a dictionary of available service enumerations.
        @code
        myExtBleakClient = ExtBleakClient("00:1A:22:12:0F:87")
        print(myExtBleakClient.gatt)
        print(myExtBleakClient.gatt['DeviceInformation'].MODEL.uuid)
        await myExtBleakClient.connect()
        print( await myExtBleakClient.read(myExtBleakClient.gatt['DeviceInformation'].MODEL.uuid )
    """
    def __init__(self, mac: str):
        """! @brief Initialization
        @param mac String representing the bluetooth mac address (e.g. '00:1A:22:12:0F:87')of the device this instance is representing 
        """
        super().__init__(mac)
        self.requestCommandUUID = None
        self.requestResponseUUID = None
        self.requestNotifycationResult = None
        self.requestTimeOut = 1.0
        self.requestResponseTime = 0.0

    def __destroy__(self):
        if self.is_connected:
            raise BleakError(f"Recource leak because {self.__class__} BLE 'bleak' client has not been disconnected before object destruction!") 
        super().__destroy__()
    
    async def disconnect(self):        
        await self.__stopResponseNotification__()
        try:
            await super().disconnect()
        except EOFError:    # Needed, in case the external device has already disconnected without notice.
            pass
        
    async def read(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID]) -> Union[bytearray, str, int]:
        """! @brief Reading a GATT characteristic value"""
        # Some devices desconnect without notice to the client. In such cases the next access fails and one try to reconnect is executed.
        uid = uuid
        if isinstance(uuid, BaseService):
            uid = uuid.value.uuid
        done = 2
        #print("-> read: uid = " + str(uid))
        while done > 0:
            try:
                res = await self.read_gatt_char(uid)
                done = 0
            except EOFError as e:
                if done < 2:
                    raise e
                else:
                    #print("-> Read failure, trying to connect and repeat writing")
                    done = 1
                    await self.connect()
                    await self.__startResponseNotification__(self.requestResponseID, True)            
        if isinstance(uuid, BaseService):
            return uuid.value.from_bytearray(res)
        return res

    async def write(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], data: Union[bytearray, str, int]):
        """! @brief Writing to a GATT characteristic value"""
        # Some devices desconnect without notice to the client. In such cases the next access fails and one try to reconnect is executed.
        uid = uuid
        if isinstance(uuid, BaseService):
            uid = uuid.value.uuid
            data = uuid.value.to_bytearray(data)
        done = 2
        while done > 0:
            try:
                await self.write_gatt_char(uid, data)
                done = 0
            except EOFError as e:
                if done < 2:
                    raise e
                else:
                    #print("-> Write failure, trying to connect and repeat writing")
                    done = 1
                    await self.connect()
                    await self.__startResponseNotification__(self.requestResponseUUID, True)            
        return

    async def start_notify(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], notificationHandler):
        """! brief Starts notifications on a characteristic """
        uid = uuid
        if isinstance(uuid, BaseService):
            uid = uuid.value.uuid
        await super().start_notify(uid, notificationHandler)
        
    async def stop_notify(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID]):
        """! brief Stops notifications on a characteristic """
        uid = uuid
        if isinstance(uuid, BaseService):
            uid = uuid.value.uuid
        await super().stop_notify(uid)
        
    def __response_notification_handler__(self, sender, data):
        """Simple notification handler which stores the data received."""
        self.requestNotifycationResult = data
        #print("-> __response_notification_handler__ from {0}: {1}".format(sender, data))
    
    async def __startResponseNotification__(self, requestResponseUUID, force = False):
        """ Does nothing in case the 'requestResponseUUID' has already started notifying earlier. """
        if not force and self.requestResponseUUID == requestResponseUUID:
            return
        if not force:
            await self.__stopResponseNotification__() 
        uid = requestResponseUUID
        if isinstance(uid, BaseService):
            uid = uid.value.uuid
        #print("-> start notify")
        await self.start_notify(uid, self.__response_notification_handler__)
        self.requestResponseUUID = requestResponseUUID

    async def __stopResponseNotification__(self):
        if self.requestResponseUUID is None:
            return
        #print("-> stop notify")
        uid = self.requestResponseUUID
        if isinstance(uid, BaseService):
            uid = uid.value.uuid
        await self.stop_notify(uid)
        self.requestResponseUUID = None
        await asyncio.sleep(self.requestTimeOut)  # This is necessary as e.g. the EQ3 CC_RT_BLE requires time to accept a new start_notify. Might be the case for other devices also.
            
    async def requestUsing(self, requestResponseUUID: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], requestCommandUUID: Union[BaseService, BleakGATTCharacteristic, int, str, UUID, None] = None, data: Union[bytearray, None] = None, timeOut: float = 1.0) -> Union[bytearray, None]:
        """! @brief Requests data from a BLE device using the notification response procedure
             Some BLE devices use a command characeristic. Writing e.g. a read request command coded
             within the data bytearry, specific to the vendor of the device, will force a notification
             response containing the answer with the requested infromation content, also specifically coded
             by the vendor.
             The usual call is
             @code
             requestUsing(requestResponseUUID, requestCommandUUID, b'\00')
             @endcode
             For easyer and typing error avoiding use the UUIDs can be registered within the object: \n
             @code
             requestUsing(requestResponseUUID, requestCommandUUID) \n
             @endcode
             After that case the requests can be executed by \n
             @code
             request(b'\00')
             @endcode
        """
        #print("-> request")
        self.requestCommandUUID = requestCommandUUID
        self.requestTimeOut = timeOut
        self.requestNotifycationResult = None
        if requestCommandUUID is None or requestResponseUUID is None:
            await self.__stopResponseNotification__()
            return       
        await self.__startResponseNotification__(requestResponseUUID)
        if data is None:
            return
        #print("-> write request")
        uid = self.requestCommandUUID
        if isinstance(uid, BaseService):
            uid = uid.value.uuid
        await self.write(uid, data)
        timeOutCnt = timeOut*100
        while timeOutCnt>0 and self.requestNotifycationResult==None:
            timeOutCnt = timeOutCnt - 1
            await asyncio.sleep(0.01)
        self.requestResponseTime = (timeOut*100-timeOutCnt)*0.01
        #print("-> response time {}s".format(self.requestResponseTime))
        if (timeOutCnt==0):
            raise bleak.exc.BleakError("Request procedure failed with time out of {}s while waiting for the notification response!".format(timeOut))
        return self.requestNotifycationResult

    async def request(self, data: Union[bytearray, None] = None, timeOut: float = 1.0) -> Union[bytearray, None]:
        """! @ Short call to request data by using the command response mechanism
            This method can be used in case a previous call to \ref requestUsing has already defined the
            corresponding command and response characteristics. Derived client classes usually do that within
            their constructor.
        """
        if self.requestCommandUUID is None or self.requestResponseUUID is None:
            raise bleak.exc.BleakError("Method 'request' called but requestCommandUUID or requestResponseUUID are undefined.")
        return await self.requestUsing(self.requestResponseUUID, self.requestCommandUUID, data, timeOut)

    def printServices(self, readValues: bool = False):
        """! @brief Prints all content provided from the GATT server device
             The method does not retrieve this information from the device. Instead, the information received from the last connect
             and stored in the 'services' property is used.
             @param readValues If true, all values related to services, characteristics and descriptors are actually read from the device
        """
        for service in self.services:
            print("[Service] -> {0}: {1}".format(service.uuid, service.description))
                  
            for char in service.characteristics:
                if readValues and "read" in char.properties:
                    try:
                        value = self.read(char.uuid)
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = '-unread-'
                print(
                    "\t[Characteristic] {0}: (Handle: 0x{1:02X}) ({2}) | Name: {3}, Value: {4} ".format(
                        char.uuid,
                        char.handle,
                        ",".join(char.properties),
                        char.description,
                        value,
                    )
                )
                
                for descriptor in char.descriptors:
                    if readValues:
                        value = self.read_gatt_descriptor(descriptor.handle)
                    else:
                        value = '-unread-'
                    print(
                        "\t\t[Descriptor] {0}: (Handle: 0x{1:02X}) | Value: {2} ".format(
                            descriptor.uuid, descriptor.handle, value #bytes(value)
                            )
                        )

if __name__ == '__main__':

    from gatt_services import DeviceInformationService
    charUUID_ReadWriteRequest  = "3fa4585a-ce4a-3bad-db4b-b8df8179ea09" # handle 0x0411
    charUUID_ReadWriteResponse = "d0e8434d-cd29-0996-af41-6c90f4e0eb2a" # handle 0x0421

    print("Test of ExtBleakClient")

    eq  = ExtBleakClient('00:1A:22:12:0F:87')
    tag = ExtBleakClient('54:6C:0E:52:C7:84')

    # sample program for 'request' to be used at the EQ3 CC_RT_BLE valve device
    async def TestRequest():
        print("Use of 'request' at an EQ3 CC_RT_BLE valve device")
        print("Connecting")
        await eq.connect()
        print("Request")
        await eq.requestUsing(charUUID_ReadWriteResponse, charUUID_ReadWriteRequest)
        command = b'\00'
        print(f"Command:  {command}")
        res = await eq.request(b'\00')
        print(f"Response: {res}")
        print("Disconnecting")
        await eq.disconnect()

    async def TestDeviceReading(client: ExtBleakClient):
        print("Use of 'read'")
        print("Connecting")
        await client.connect()
        print("Read DeviceInformationService.MODEL with uuid string")
        res = await client.read(DeviceInformationService.MODEL.uuid)
        print(res)
        print("Read DeviceInformationService.MODEL with CharacteristicType")
        res = await client.read(DeviceInformationService.MODEL)
        print(res)
        print("Disconnecting")
        await client.disconnect()
    
    asyncio.run(TestDeviceReading(eq))
