# /usr/bin/env python3
# -*- coding: utf-8 (ü) -*-
"""!
@file gatt_services.py

@brief Provides predifined service enumerations containing their characteristics
"""
from typing import Union

try: # Necessary, to run this file directly
    from gatt import BaseService, CharacteristicType
except:
    from me2grid.easybleak.gatt import BaseService, CharacteristicType

class GenericAccessService(BaseService):
    """! @brief Enumeration of characteristics within the 'Generic Access' service """
    DEVICE                   = CharacteristicType("00002a00-0000-1000-8000-00805f9b34fb", str)     #!> Device Name
    PREFERRED_CONNECTION     = CharacteristicType("00002a04-0000-1000-8000-00805f9b34fb")          #!> Preferred Connection Parameters

    @classmethod
    def uuidService(cls) -> str:
        return "00001800-0000-1000-8000-00805f9b34fb"
    
class GenericAttributeProfileService(BaseService):
    """! @brief Enumeration of characteristics within the 'Gerneric Attribute Profile' service """
    SERVICE_CHANGED          = CharacteristicType("00002a00-0000-1000-8000-00805f9b34fb")          #!> Device Name

    @classmethod
    def uuidService(cls) -> str:
        return "00001801-0000-1000-8000-00805f9b34fb"
    
class DeviceInformationService(BaseService):
    """! @brief Enumeration of characteristics within the 'Device Information' service """
    SYSTEM_ID               = CharacteristicType("00002a23-0000-1000-8000-00805f9b34fb")           #!> System ID
    MODEL                   = CharacteristicType("00002a24-0000-1000-8000-00805f9b34fb", str)      #!> Model Number String
    SERIAL                  = CharacteristicType("00002a25-0000-1000-8000-00805f9b34fb", str)      #!> Serial Number String
    FIRMWARE                = CharacteristicType("00002a26-0000-1000-8000-00805f9b34fb", str)      #!> Hardware Revision String
    HARDWARE                = CharacteristicType("00002a27-0000-1000-8000-00805f9b34fb", str)      #!> Hardware Revision String
    SOFTWARE                = CharacteristicType("00002a28-0000-1000-8000-00805f9b34fb", str)      #!> Software Revision String
    MANUFACTURER            = CharacteristicType("00002a29-0000-1000-8000-00805f9b34fb", str)      #!> Manufacturer Name String
    IEEE_CERT               = CharacteristicType("00002a2a-0000-1000-8000-00805f9b34fb")           #!> IEEE 11073-20601 Regulatory Cert. Data List
    PNP_ID                  = CharacteristicType("00002a50-0000-1000-8000-00805f9b34fb")           #!> PnP ID

    @classmethod
    def uuidService(cls) -> str:
        return "0000180a-0000-1000-8000-00805f9b34fb"
    
class GenericDescriptors(BaseService):
    """! @brief Enumeration of predefined characteristics used as descriptors """
    CLIENT_CHAR_CONFIG    = CharacteristicType("00002902-0000-1000-8000-00805f9b34fb")           #!> Descriptor for enabling notifications

    @classmethod
    def uuidService(cls) -> Union[str, None]:
        return None
