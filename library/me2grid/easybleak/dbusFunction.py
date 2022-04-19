""" Code extracted from library 'bluepi' """

import dbus

class constants:
    DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
    BLUEZ_SERVICE_NAME = 'org.bluez'
    ADAPTER_INTERFACE = 'org.bluez.Adapter1'
    DEVICE_INTERFACE = 'org.bluez.Device1'
    GATT_SERVICE_IFACE = 'org.bluez.GattService1'
    GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
    GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

def generic_start_notify_cb():
    """Callback associated with enabling notifications."""
    return

def generic_stop_notify_cb():
    """Callback associated with disabling notifications."""
    return

def generic_error_cb(error):
    """Generic Error Callback function."""
    print('generic_error_cb: D-Bus call failed: %s', str(error))

def _get_dbus_path2(objects, parent_path, iface_in, prop, value):
    """
    Find DBus path for given DBus interface with property of a given value.

    :param objects: Dictionary of objects to search
    :param parent_path: Parent path to include in search
    :param iface_in: The interface of interest
    :param prop: The property to search for
    :param value: The value of the property being searched for
    :return: Path of object searched for
    """
    if parent_path is None:
        return None
    for path, iface in objects.items():
        props = iface.get(iface_in)
        if props is None:
            continue
        dev_name = "dev_" + value.lower().replace(":", "_")
        if (props[prop].lower() == value.lower() or
            path.lower().endswith(dev_name)) \
                and path.startswith(parent_path):
            return path
    return None


def get_dbus_path(adapter=None,
                  device=None,
                  service=None,
                  characteristic=None,
                  descriptor=None):
    """
    Return a DBus path for the given properties
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus path
    """
    bus = dbus.SystemBus()
    manager = dbus.Interface(
        bus.get_object(constants.BLUEZ_SERVICE_NAME, '/'),
        constants.DBUS_OM_IFACE)
    mngd_objs = manager.GetManagedObjects()

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)
    else:
        _dbus_obj_path='/org/bluez/hci0'

    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if service is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_SERVICE_IFACE,
                                         'UUID',
                                         service)

    if characteristic is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_CHRC_IFACE,
                                         'UUID',
                                         characteristic)

    if descriptor is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_DESC_IFACE,
                                         'UUID',
                                         descriptor)
    return _dbus_obj_path

def get_iface(adapter=None,
              device=None,
              service=None,
              characteristic=None,
              descriptor=None):
    """
    For the given list of properties return the deepest interface
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus Interface
    """
    if adapter is not None:
        _iface = constants.ADAPTER_INTERFACE

    if device is not None:
        _iface = constants.DEVICE_INTERFACE

    if service is not None:
        _iface = constants.GATT_SERVICE_IFACE

    if characteristic is not None:
        _iface = constants.GATT_CHRC_IFACE

    if descriptor is not None:
        _iface = constants.GATT_DESC_IFACE

    return _iface

def get_dbus_obj(dbus_path):
    """
    Get the the DBus object for the given path
    :param dbus_path:
    :return:
    """
    bus = dbus.SystemBus()
    return bus.get_object(constants.BLUEZ_SERVICE_NAME, dbus_path)

def get_dbus_iface(iface, dbus_obj):
    """
    Return the DBus interface object for given interface and DBus object
    :param iface:
    :param dbus_obj:
    :return:
    """
    return dbus.Interface(dbus_obj, iface)

def get_methods(adapter=None,
                device=None,
                service=None,
                characteristic=None,
                descriptor=None):
    """
    Get methods available for the specified
    :param adapter: Adapter Address
    :param device: Device Address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: Object of the DBus methods available
    """
    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)
    iface = get_iface(adapter,
                      device,
                      service,
                      characteristic,
                      descriptor)
    if path_obj is not None:
        return get_dbus_iface(iface, get_dbus_obj(path_obj))
    else:
        return None

def enableNotification(self, characteristicUUID: Union[BleakGATTCharacteristic, int, str, UUID]) -> None:
    """! @brief Sends a command to the remote divice to activate notifications for a given characteristic
         Just a historic implementation to start notifications by direct use of DBus functions to communicate to BlueZ
         kept as an excample (see also 'bluepi' library code).
    """
    char = self.services.get_characteristic(characteristicUUID)
    srv_uuid = char.service_uuid
    characteristic_methods = dbusFunction.get_methods(None, self.address, srv_uuid, characteristicUUID)
    try:
        characteristic_methods.StartNotify(
            reply_handler  = dbusFunction.generic_start_notify_cb,
            error_handler  = dbusFunction.generic_error_cb,
            dbus_interface = dbusFunction.constants.GATT_CHRC_IFACE)
    except:
        raise bleak.exc.BleakError('Characteristic %s cannot execute StartNotify' % characteristicUUID)       
