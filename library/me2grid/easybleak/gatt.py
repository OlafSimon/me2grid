# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file  gatt.py

@brief Provides the GATT_Dict class delivering BLE GATT services as enumerations of named characteristics

@code
print(GATT_Dict.gatt())
@endcode

Each BLE client class derives from GATT_Dict. For excample the EasyBleakClient (and all its derived classes):

@code
print(EasyBleakClient.gatt())
@endcode

"""

versionEasyBleak = "Library EasyBleak 1.0"

from enum import Enum
from typing import Union

def BLE_UUID(val: int) -> str:
    """ @brief Transforms a 16bit BLE specific uuid integer value to a full uuid string """
    return ("0000%04x-0000-1000-8000-00805f9b34fb" % val)

class CharacteristicType:
    """! @brief Holds the type and size information of a characterisitc
        Using this type as uuid input of methods leads to returning or input of the characteristic value in the form of
        its intended tye (bytearray, str, int) instead of the difficult to interprete bytearray. \n
        The excample returns a string:
        @code
        >>> device.read(device.DeviceInformation.MODEL)
        @endcode
        @param uuid String representation of the characteristics UUID
        @param type Type information of the characteristic value (e.g. str).
        @param size Size of the characteristic value in bytes (needed to create the bytearry from e.g. the str input). The standard value zero declares a read only characteristic.
        @param **kargs signed: bool - Indicating signed (True) or unsigned (False) interger values used for the characteristic (used for type 'int' only).
        @param **kargs order: str - Byte order of the bytearray representing an inter value. State standard order 'little' or 'big' (used for type 'int' only).
        @param **kargs encoding: str - The encoding for string conversion. Standard value is 'utf-8' (used for type 'str' only).
    """
    def __init__(self, uuid:str, type = bytearray, size: int = 0, **kargs):
        self.uuid = uuid
        self.type = type
        self.size = size
        self.signed = True
        self.order = 'little'
        self.encoding = 'utf-8'
        
        if "signed" in kargs:
            val = kargs["signed"]
            if isinstance(val, bool):
                self.signed = val
            else:
                raise ValueError("Key parameter 'signed' requires type {repr(bool)} !")
        if "order" in kargs:
            val = kargs["order"]
            if val=='little' or val=='big':
                self.order = val
            else:
                raise ValueError("Key parameter 'order' requires to be either 'little' or 'big'!")
        if "encoding" in kargs:
            val = kargs["encoding"]
            if isinstance(val, str):
                self.encoding = val
            else:
                raise ValueError("Key parameter 'order' requires type {repr(str)} !")

    def __str__(self):
        return "CharacteristicType(uuid={0}, type={1}, size={2})".format(self.uuid, self.type, self.size)
    
    @staticmethod
    def bytearrayToLen(array: bytearray, length: int) -> bytearray:
        """! Appends a bytearray with zero values to the given length or cuts the array to the given length """
        if len(array)>=length:
            res = array[0:length]
        else:
            res = array + bytearray(length-len(array))
        return res
        
    def from_bytearray(self, data: bytearray) -> Union[bytearray, str, int]:
        """! @brief Converts a bytearry to the type specified within this instance """
        if self.type == bytearray:
            return data
        if self.type == str:
            return data.decode("utf-8")
        if self.type == int:
            return int.from_bytes(data, self.order, signed = self.signed)
        
    def to_bytearray(self, value: Union[bytearray, str, int]) -> bytearray:
        """! @brief Converts a value of the type this instance specifies to the according bytearry """
        if not isinstance(value, self.type):
            raise ValueError(f"Parameter 'value' requires type {repr(str)} !")
        if self.type is not bytearray and self.size <= 0:
            raise ValueError("The instance specifies a read only characteristc (size=0)! Conversion is not possible.")
        res = None
        if self.type == bytearray:
            res = value
        if self.type == str:
            res = bytearray("test", encoding="utf-8")
        if self.type == int:
            res = bytearray(value.to_bytes(self.size,'little'))
        if res is None:
             raise ValueError(f"The instance defines a not supported type {type(value)} !")
        return res

class BaseService(Enum):
    """! @brief Base class for characteristic enumerations
        This class is used as base class for a service description class, e.g. 'DeviceInformation'.
        Services define enumeration entities representing characteristics using the type 'CharacteristicType', e.g. 'MODEL'.
        You can receive the UUID of the characteristic entity and the service UUID the entity belongs to by:
        @code
        print(DeviceInformation.MODEL.uuid)
        print(DeviceInfromation.uuidService())
    """
    @property
    def uuid(self) -> str:
        return self.value.uuid

    @classmethod
    def uuidService(cls) -> Union[str, None]:
        raise NotImplementedError("The service enumeration class shall implement the uuid class method to return the service UUID string!")
    
    @classmethod
    def characteristics(cls) -> [str]:
        """! @brief Deliveres a list of enumeration entities
        Use this method to print all characteristic names a service contains.
        @code
        print(DeviceInformation.characteristics())
        @endcode
        To receive all entities as a list of 'CharacteristicType' types use list(characteristics)!
        """
        l=[]
        for c in cls:
            l.append(c.name)
        return l

    @classmethod
    def toString(cls) -> str:
        """! @brief Deliveres a string representing the content of this enumeration in a readable format """
        #r = repr(cls)
        #return "<{0} {1}>".format(r[1:len(r)-1], cls.characteristics())
        return "<enum '{0}.{1}' {2}>".format(__class__.__module__, cls.__name__, cls.characteristics())

    @classmethod
    def fromUUID(cls, uuid:str):
        """! @brief Deliveres the enumeration entity or the enumeration itself of a given UUID string """
        for c in cls:
            if c.uuidService == uuid:
                return cls
            if c.uuid == uuid:
                return c
        return None
 
class ClassServices(dict):
    # Hint for future changes: the __new__ constructor might be an option for avoiding the class GATT_Dict
    # proposed class GattServices
    
    #     def __new__(cls, *args, **kwargs):
    #         obj = super(MyList, cls).__new__(cls, *args, **kwargs)
    #         obj.append('FirstMen')
    #         return obj

    def __str__(self):
        ret = "<dict '"+__class__.__module__+"."+__class__.__name__+"' {\n"
        for key, value in self.items():
            ret = ret + " '{0}':{1}\n".format(key, value.toString())
        ret = ret + "}>"
        return ret

