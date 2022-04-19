# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  EasyBleakClient.py

@brief Provides an easy to use BLE client for synchronous programming

@section Requirements \n

- bleak \n

Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html
"""

import asyncio
import bleak

from sys import stderr
from typing import Union
from uuid import UUID
from bleak.backends.characteristic import BleakGATTCharacteristic

try: # Necessary, to run this file directly
    from gatt import BaseService
    from ExtBleakClient import ExtBleakClient, GATT_Dict
except:
    from me2grid.easybleak.gatt import BaseService
    from me2grid.easybleak.ExtBleakClient import ExtBleakClient, GATT_Dict

def syncCall(func):    
    def Call(*args, **kwargs):
        inst = args[0]
        inst._checkConnect_()
        try:
            #print("-> Decorator")
            #print(args)
            result = inst._loop.run_until_complete(func(*args, **kwargs))
            #result = func(*args, **kwargs)
        except bleak.exc.BleakError as e:
            inst._checkDisconnect_()
            raise e
        inst._checkDisconnect_()
        return result
    return Call

class EasyBleakClient(GATT_Dict):
    """! @brief Object to commuinicate to devices by BLE for synchronous programming
    
        This object represents a BLE device and enables communication to it, serving as a BLE client. \n
        It is especially usable within the python 'shell'. \n
        The EasyBleakClient wraps an BleakClient objct from the 'bleak' Library and avoids the need of using the 'asyncio'
        library making programming much easier, especially for beginners. Such way, the usage equals to libraries like
        'BLE_GATT' or 'bluepi' and simplifies migration to the hardware independent 'bleak' library.
     
        @code{.py}
        client = EasyBleakCient('[Bluetooth MAC Address]')
        client.connect()
        data = client.read('[UUID]')
        client.disconnect()
        @endcode
     
        The same can be achieved by using the context manager which automatically connects and disconnects
        
        @code{.py}
        with BleCient('[Bluetooth MAC Address]') as client
            data = client.read('[UUID]')
        @endcode
            
        The simplest usage is just calling the 'read' method. The connection and disconnection process will be executed automaticall.
        Due to the connection and disconnection process at each call this type of access is very slowly.

        @code{.py}
        client = BleCient('[Bluetooth MAC Address]')
        data = client.read('[UUID]')
        @endcode
    """
    def __init__(self, mac: str):
        """! @brief Initialization
        @param mac String representing the bluetooth mac address of the device this instance is representing 
        """
        self._bleakClient = ExtBleakClient(mac)
        self.__globalLoop = asyncio.get_event_loop()
        self._loop = asyncio.new_event_loop()       # A local loop is necessary as the user might call asyncio.run for other purpose.
                                                    # asyncio.run might open a new loop which must not be the case for BleakClient
                                                    # in between the connect and disconnect command.
        asyncio.set_event_loop(self.__globalLoop)   # necessary, as new_event_loop automatically sets the new loop as global
        self._continuousConnect = False
        
    def __destroy__(self):
        if self.is_connected:
            try:
                self.disconnect()
                print("Undesired automatic disconnect within the destructor of {self.__class__} successful!", file=stderr)
            except:
                pass
            self._loop.close()
            raise BleakError(f"Recource leak because {self.__class__} BLE 'bleak' client has not been disconnected before object destruction!") 
        self._loop.close()
        super().__destroy__()
            
    # Context managers
    def __aenter__(self):
        self.connect()
        return self
    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # EasyBleakClient features

    def connect(self):
        """! @brief Connects to the remote BLE device
             Using this method the connection will kept open until \ref disconnect is called. The connection process
             is time consuming as the remote device is scanned for services and characteristics.
        """
        self._continuousConnect = True;
        self._checkConnect_()
        self._checkDisconnect_()
        
    def disconnect(self):
        """! @brief Disconnects to the remote BLE device
             To be called after the \ref connect method to finish communication to the remote device.
        """
        self._continuousConnect = False;
        self._checkConnect_()
        self._checkDisconnect_()
        
    def _checkConnect_(self):
        """! @brief \b protected Connects if not connected yet and switches to the client asyncio loop """
        # Switching to the objects own local event loop
        self.__globalLoop = asyncio.get_event_loop()
        asyncio.set_event_loop(self._loop)
        # Check for the connection status
        if not self._bleakClient.is_connected:
            try:
                #print("-> connect")
                self._loop.run_until_complete(self._bleakClient.connect())
            except bleak.exc.BleakError as e:
                asyncio.set_event_loop(self.__globalLoop)
                raise e
                        
    def _checkDisconnect_(self):
        """! @brief \b protected Disconnects if no permanent connection is chosen and switches back to the global asyncio loop """
        # Check for the need of disconnecting
        if not self._continuousConnect and self._bleakClient.is_connected:
            try:
                #print("-> disconnect")
                self._loop.run_until_complete(self._bleakClient.disconnect())
            except bleak.exc.BleakError as e:
                asyncio.set_event_loop(self.__globalLoop)
                raise e
        # switch back to global system loop from the objects own local event loop
        asyncio.set_event_loop(self.__globalLoop)

    # ExtBleakClient interface
    
    @syncCall
    async def read(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID]) -> Union[bytearray, str, int]:            
        """! @brief Reads from a GATT characteristic """
        return await self._bleakClient.read(uuid)
        
    @syncCall
    async def write(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], data: Union[bytearray, str, int]):
        """! @brief Writes to a GATT characteristic  """
        await self._bleakClient.write(uuid, data)

    @syncCall
    async def requestUsing(self, requestResponseUUID: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], requestCommandUUID: Union[BaseService, BleakGATTCharacteristic, int, str, UUID, None] = None, data: Union[bytearray, None] = None, timeOut: float = 1.0) -> bytearray:            
        """! @brief Requesting a read or write operation of a GATT characteristic using a GATT command characteristic
            This method uses a notification answer (response) of the BLE device for reading initiated by the write to the command characteristic.
            The command and response characteristics should be defined within the 'RequestService' enumeration of the derived class of
            'EasyBleak'
        """
        await self._bleakClient.requestUsing(requestResponseUUID, requestCommandUUID, data, timeOut)

    @syncCall
    async def request(self, data: Union[bytearray, None] = None, timeOut: float = 1.0) -> bytearray:
        """! @ Short call to request data by using the command response mechanism
            This method can be used in case a previous call to \ref requestUsing has already defined the
            corresponding command and response characteristics. Derived client classes usually do that within
            their constructor.
        """
        return await self._bleakClient.request(data, timeOut)

    @syncCall
    async def __sleep__(self, time: float=0):
        """! @brief Synchronous call of asyncio.sleep(), used to keep the loop running """ 
        await asyncio.sleep(time)
        
    def getNotifications(self, waitTime: float = 0):
        """! @brief Executes received notifications 
             For synchronous programming it is necessary to explicitly give time to 'receive' notifications. Actually,
             notifications are received asynchronously and memoriezed within a stack. This method executes all memorized
             notifications by calling the coresponding callback methods. \n
             Usually, this method is called periodically during application program execution.
             @param waitTime If zero all memorized notifications since the last call are executed. Otherwise continues to receive and execute incoming notifications.
        """
        self.__sleep__(waitTime)
        
    def printServices(self):
        self._bleakClient.printServices()
        
    # BaseBleakClient interface
    
    @property
    def is_connected(self) -> str:
        return self._bleakClient.is_connected

    @property
    def services(self) -> bleak.backends.service.BleakGATTServiceCollection:
        """! @brief Deliveres the serivces memorized in the client
            The services have been read during connecting, or may be newly read by calling \ref get_services().
        """
        return self._bleakClient.services

    @syncCall
    async def read_gatt_char(self, uuid: Union[BleakGATTCharacteristic, int, str, UUID]) -> bytearray:
        """! @brief Not recommended, use \ref read instead! Reads a characteristic value
            Calls the same method of the BleakClient class. This method is not safe in case of disconnections without notice,
            thus it is recommended to use the method \ref read with safe access instead.
        """
        return await self._bleakClient.read_gatt_char(uuid)

    @syncCall
    async def write_gatt_char(self, uuid: Union[BleakGATTCharacteristic, int, str, UUID], data: bytearray):
        """! @brief Not recommended, use \ref write instead! Writes a value to a characteristic
            Calls the same method of the BleakClient class. This method is not safe in case of disconnections without notice,
            thus it is recommended to use the method \ref write with safe access instead.
        """
        await self._bleakClient.write_gatt_char(uuid, data)
                           
    @syncCall
    async def read_gatt_descriptor(self, handle: int) -> bytearray:
        """! @brief Reads the value content of a GATT descriptor
            There is no alternative connection safe implementation yet. 
        """
        await self._bleakClient.read_gatt_descriptor(handle)

    @syncCall
    async def write_gatt_descriptor(self, handle: int, data: Union[bytes, bytearray, memoryview]) -> None:
        """! @brief Writes the value to GATT descriptor
            There is no alternative connection safe implementation yet. 
        """
        await self._bleakClient.write_gatt_descriptor(handle, data)
        
    @syncCall
    async def start_notify(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID], notificationHandler):
        """! @brief Registeres a callback method in order to receive notification messages from the given characteristic
             The method also writes to the 0x2902 descriptor of that characteristic to start notifichations on the external device.
        """
        await self._bleakClient.start_notify(uuid, notificationHandler)
    
    @syncCall
    async def stop_notify(self, uuid: Union[BaseService, BleakGATTCharacteristic, int, str, UUID]):
        """! @brief Removes a notification callback method and stops notifications"""        
        await self._bleakClient.stop_notify(uuid)
         
    @syncCall
    async def get_services(self) -> bleak.backends.service.BleakGATTServiceCollection:
        """! @brief Receives services, characteristics and descriptors from the remote device """
        return await self._bleakClient.get_services()

    @syncCall
    async def pair(self, *args, **kwargs) -> bool:
        """Pair with the peripheral."""
        return await self._bleakClient.pair(*args, **kwargs)


    @syncCall
    async def unpair(self) -> bool:
        """Unpair with the peripheral."""
        return await self._bleakClient.unpair()

    def set_disconnected_callback(self, onDisconnect):
        """! @brief Receives services, characteristics and descriptors from the remote device """
        self._bleakClient.set_disconnected_callback(onDisconnect)


if __name__ == '__main__':
    
    from gatt_services import DeviceInformationService
    charUUID_ReadWriteRequest  = "3fa4585a-ce4a-3bad-db4b-b8df8179ea09" # handle 0x0411
    charUUID_ReadWriteResponse = "d0e8434d-cd29-0996-af41-6c90f4e0eb2a" # handle 0x0421

    print("EasyBleakClient")

    eq  = EasyBleakClient('00:1A:22:12:0F:87')
    tag = EasyBleakClient('54:6C:0E:52:C7:84')

    # sample program for 'request' to be used at the EQ3 CC_RT_BLE valve device
    def TestRequest():
        print("Use of 'request' at an EQ3 CC_RT_BLE valve device")
        print("Connecting")
        eq.connect()
        print("Request")
        eq.requestUsing(charUUID_ReadWriteResponse, charUUID_ReadWriteRequest)
        command = b'\00'
        print(f"Command:  {command}")
        res = eq.request(b'\00')
        print(f"Response: {res}")
        print("Disconnecting")
        eq.disconnect()

    def TestDeviceReading(client: EasyBleakClient):
        print("Use of 'read'")
        print("Connecting")
        client.connect()
        print("Read DeviceInformationService.MODEL with uuid string")
        res = client.read(DeviceInformationService.MODEL.uuid)
        print(res)
        print("Read DeviceInformationService.MODEL with CharacteristicType")
        res = client.read(DeviceInformationService.MODEL)
        print(res)
        print("Disconnecting")
        client.disconnect()
    
    TestDeviceReading(eq)
