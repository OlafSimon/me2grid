#ifndef __CANAPI2H__        
#define __CANAPI2H__

//  CanApi2.h: Definition of the CAN-API.
//
//  Version 2.57.0
//
//  Principle:
//  ~~~~~~~~~~
//  The driver supports multiple Clients (= Windows or DOS programs that
//  communicate with CAN busses), and multiple CAN Hardware implemented
//  with 82C200 / SJA1000 CAN controllers.
//  A cardinal point is the idea of the "Net": it describes a CAN bus that
//  is extended virtually into the PC. Multiple Clients can be connected
//  to one Net, which itself can have an interface to a physical CAN bus
//  via an appropriate CAN adapter.
//  A Net definition determines, aside from the Baud rate, an amount
//  of CAN messages to process.
//
//  Clients that are specialized on some kind of CAN bus (e.g. stepper
//  motor control, car radio panel, etc.), should not offer any Hardware
//  selection, but directly address a fixed Net (e.g. 'Lab-Net').
//  The connection Net - Hardware can then be accomplished by a separate
//  configuration tool (the settings depend on the respective PC and its
//  CAN Hardware).
//
//  If neccessary, CAN nodes connected to an external CAN bus can 
//  be simulated by Clients on the same Net. In this case there is no
//  CAN Hardware required, the complete bus can be simulated within the
//  PC. The Net can then be defined as an 'Internal Net'.
//
//  Samples for possible Net configurations:
//  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//  (can all be realized at the same time):
//                                                   external
//                                    ,------------< CAN bus 'A'
//  ,--------. ,--------.       ,-----+----.
//  |Client A| |Client B|       |Hardware 1|
//  `---+----' `----+---'       `-----+----'
//      `-----------+-----------------'
//               N e t  I                           external
//                                    ,------------< CAN bus 'B'
//  ,--------. ,--------.       ,-----+----.
//  |Client C| |Client D|       |Hardware 2|
//  `---+--+-' `----+---'       `-----+----'
//      |  `--------+-----------------'              external
//      |        N e t  II            ,------------< CAN bus 'C'
//      |      ,--------.       ,-----+----.
//      |      |Client E|       |Hardware 3|
//      |      `----+---'       `-----+----'
//      `-----------+-----------------'             'Gateway'
//               N e t  III
//   ,--------. ,--------. ,--------.
//   |Client F| |Client G| |Client H|
//   `---+----' `---+----' `---+----'               'Internal Net'
//       `----------+----------'
//               N e t  IV
//
//  Features:
//  ~~~~~~~~~
//   - 1 Client can be connected to multiple Nets
//   - 1 Net supplies multiple Clients
//   - 1 Hardware can be used by 1 Net at the same time
//   - each Net can be assigned to 1 Hardware or no Hardware at all
//   - if a Client sends a message on the Net, the message will be routed
//     to all other Clients and over a connected Hardware to the physical
//     bus
//   - if a message is received from a Hardware, it will be routed to all
//     Clients which are connected to the Hardware via a Net. Each Client
//     only receives the messages which pass its acceptance filter
//   - CAN Hardware can be configured via a Windows Control Panel application,
//     Nets can be configured with a separate tool.
//     Multipled Nets can be defined for each Hardware, but only one can be
//     active at the same time.
//   - Clients connect to a Net via the name of the Net
//   - each Hardware has its own transmit queue to buffer outgoing messages
//   - each Client has a receive queue to buffer received messages
//   - each Client has a transmit queue, which holds outgoing messages until
//     their scheduled real send time. Is the send time reached they will
//     be written into the transmit queue of the Hardware.
//   - hClient: 'Client handle'. This number is used by the driver to
//              identify and manage a Client
//   - hHw :    'Hardware handle'. This number is used by the driver to
//              identify and manage a Hardware
//   - hNet:    'Net handle'. This number is used by the driver to
//              identify and manage a Net
//   - all handles are 1-based. 0 = illegal handle
//   - used Hardware and Nets are defined in the Registry
//     During Windows startup the driver reads the configuration and
//     initializes all Hardware and Nets.
//
//  Registry Keys:
//  WinNT/2000/XP/Vista:
//      HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Peakcan
//  Win95/98/ME:
//      HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Vxd\Peakcan
//
//  Values (as strings):
//      Hardware<HWHandle>=<DriverNo>,<PortBase>,<IRQ>
//      Net<NetHandle>=<Name>,<HWHandle>,<BTR0BTR1>
//
//  Example:
//      Hardware1=1,0x300,15
//      Net7=TestNet,1,0x001C
//
//   - the API functions are devided into 3 groups:
//     1) Control-API: control of the driver through configuration tools
//     2) Client-API: reading and writing of messages through applications
//     3) Info-API: helper functions
//
//
//  Control-API
//  ~~~~~~~~~~~
//  CAN_RegisterHardware(hHw, wDriverNo, wBusID, dwPortBase, wIntNo)
//                  Activates a Hardware.
//                  Performs a memory test, installs an interrupt.
//                  Hardware can be accessed in future via 'hHw'.
//  CAN_RegisterNet(hNet, szName, hHw, wBTR0BTR1)
//                  Creates a new Net, makes an assignment Net - Hardware.
//                  Net can be accessed in future via 'hNet'.
//  CAN_RemoveNet(hNet)
//                  Deletes a Net, the Net handle gets invalid.
//  CAN_RemoveHardware(hHw)
//                  Removes a Hardware from driver management, the
//                  Hardware handle gets invalid.
//  CAN_CloseAll()
//                  Removes all Hardware, Nets, and Clients.
//
//
//  Client-API
//  ~~~~~~~~~~
//
//  Hardware control:
//  ~~~~~~~~~~~~~~~~~
//  CAN_Status(hHw)
//                  Gets the current state of a Hardware.
//  CAN_ResetHardware(hHw)
//                  Resets the CAN controller, resets the transmit queue of a
//                  Hardware. Affects other Clients on the same Net.
//  CAN_ResetClient(hClient)
//                  Resets the receive and transmit queues of a Client.
//
//  Read/Write:
//  ~~~~~~~~~~~
//  CAN_Write(hClient, hNet, &msgbuff, &sendtime)
//                  Writes a message at time 'sendtime' to Net 'hNet'.
//                  The message will be sent to the linked Hardware and to all
//                  Clients that have built up a connection to the Net with
//                  'CAN_ConnectToNet()'.
//  CAN_Read(hClient, &msgbuff, &hNet, &rcvtime)
//                  Reads a message from the Receive queue.
//  CAN_Read_Multi(hClient, &buff, max_msg_count, &msg_count)
//                  Reads "max_msg_count" messages from the Receive queue.
//
//  Registration and connection of Clients:
//  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//  CAN_RegisterClient(name, hWnd, &hClient)
//                  Registers a Client at the driver,
//                  gets a Client handle and initializes the Receive queue
//                  (one call per Client).
//  CAN_ConnectToNet(hClient, szNetName, &hNet)
//                  Connects a Client to a Net
//                  (one call per Client and Net).
//  CAN_RegisterMsg(hClient, hNet, &msg1, &msg2)
//                  A Client indicates that it wants to receive messages from the
//                  Net 'hNet'. The messages 'msg1' to 'msg2' will be received.
//                  The ID, RTR and Standard/Extended Frame parameters will be used.
//                  All others are ignored. msg1.ID1 <= msg2.ID, msg1.MSGTYPE = msg2.MSGTYPE.
//                  There is only ONE filter for Standard and Extended messages.
//                  The Standard messages will be registered as if the ID was
//                  built with the bits 28..18.
//                  Example: registration of Standard ID 0x400 means that the
//                  Extended ID 0x10000000 will be also received.
//                  Every call of this function might open the receive filter
//                  of the CAN Controller. If this happens, the CAN Controller
//                  will perform a Hardware reset.
//                  If a Client wants answer Remote Request messages, these
//                  messages must be also registered with this function.
//                  It is not guaranteed, that a Client only receives those
//                  messages that were registered using this function. This
//                  depends on the used CAN Controller (usually SJA1000/82C200).
//  CAN_RemoveAllMsgs(hClient, hNet)
//                  Resets the filter of a Client.
//  CAN_SetClientFilter(hClient, hNet, nExtended, dwAccCode, dwAccMask)
//  CAN_SetClientFilterEx(hClient, hNet, dwFilterIndex, dwFilterMode,
//                        nExtended, dwAccCode, dwAccMask)
//                  Sets the Client message filter directly (SJA1000-type)
//                  (alternative method to CAN_RegisterMsg())
//  CAN_DisconnectFromNet(hClient, hNet)
//                  Disconnects a Client from a Net.
//  CAN_RemoveClient(hClient)
//                  Removes a Client from the driver. Frees resources.
//
//
//  Info-API
//  ~~~~~~~~
//  CAN_GetDriverName(i, &namebuff)
//                  Gets the names of all Hardware types supported by the
//                  driver.
//  CAN_Msg2Text(&msgbuff, &textbuff)
//                  Debugging: transforms a CAN-message to text.
//  CAN_GetDiagnostic(&textbuff)
//                  Debugging: gets the text from the diagnosis text buffer.
//  CAN_GetSystemTime(&timebuff)
//                  Accesses the function 'Get_System_Time()' of the VMM:
//                  Returns time in Microseconds since Windows start.
//  CAN_GetErrText(err, &textbuff)
//                  Transforms error flags in 'err' to text.
//  CAN_VersionInfo(&textbuff)
//                  Returns version and copyright information from the driver.
//  CAN_GetHwParam(hHw, wParam, &buff, wBuffLen)
//                  Gets the value of a Hardware parameter.
//  CAN_SetHwParam(hHw, wParam, dwValue)
//                  Sets the a Hardware parameter.
//  CAN_GetNetParam(hNet, wParam, &buff, wBuffLen)
//                  Gets the value of a Net parameter.
//  CAN_SetNetParam(hNet, wParam, dwValue)
//                  Sets a Net parameter.
//  CAN_GetClientParam(hClient, wParam, &buff, wBuffLen)
//                  Gets the value of a Client parameter.
//  CAN_SetClientParam(hClient, wParam, dwValue)
//                  Sets a Client parameter.
//  CAN_GetDriverParam(param, &buff, bufflen)
//                  Gets the value of a driver parameter.
//  CAN_SetDriverParam(param, buff)
//                  Sets a driver parameter.
//
//
//  Samples for API usage:
//  ~~~~~~~~~~~~~~~~~~~~~~
//  a) Initialization of Hardware and Nets at Windows startup:
//     in 'VxD -OnDeviceInit()':
//          // controlled through Registry:
//                  ...
//          CAN_RegisterHardware();   // Initialize every found Hardware
//          CAN_RegisterHardware();
//                  ...
//          CAN_RegisterNet();        // Load Net definitions
//          CAN_RegisterNet();
//                  ...
//
//  b) Configuration tool:
//          LoadConfigFromRegistry();
//          EditConfig();             // User sets up a configuration
//          SaveConfigToRegistry();
//          CAN_CloseAll();           // Reset the driver
//          // Controlled by the configuration
//          CAN_RegisterHardware(); SaveHardwareToRegistry();
//          CAN_RegisterHardware(); SaveHardwareToRegistry();
//                  ....
//          CAN_RegisterNet(); SaveNetToRegistry();
//          CAN_RegisterNet(); SaveNetToRegistry();
//                  ....
//          // New configuration is now active, even after Windows is restarted.
//          // All previously connected Clients are now dead.
//
//  c) Client
//          CAN_RegisterClient();     // Just once
//          CAN_ConnectToNet(, &mynet)
//          // CAN_ConnectToNet();    // Perhaps multiple, e.g. if Gateway
//
//          if (own_baudrate)
//          {
//              int buff; byte hw; ushort myBaud;
//              CAN_GetNetParam(myNet, CAN_PARAM_NETHW, &buff, 0);
//              hw = (byte)buff;
//              CAN_SetHwParam(hw, CAN_PARAM_BAUDRATE, myBaud);
//          }
//
//          CAN_RegisterMsg();        // For every Rcv-message
//          CAN_RegisterMsg();
//          CAN_RegisterMsg();
//
//          while (active)
//          {
//              if (!(CAN_Read(..., out rcvtime) & CAN_ERR_QRCVEMPTY))
//              {
//                  // Something has been received
//                  CAN_GetSystemTime(out time);
//                  dwDelay = time.millis - rcvtime.millis;
//              }
//
//              if (something_to_write)
//                  CAN_Write();
//              if (something_exceptional)
//              {
//                  CAN_ResetHardware();
//                  CAN_ResetClient();
//              }
//          }
//
//          CAN_RemoveClient();       // Just once, free resources
//
//
//  Provided constants:
//  CAN_BAUD_1M ... _5K     Baud rates
//  CAN_PARAM_ ...          Parameter codes
//
//  All functions return a combination of error states CAN_ERR_xxx.
//
//
//  Authors:  Hoppe, Wolf
//  Language: C, C++
//
//  --------------------------------------------------------------------
//  Copyright (C) 1995-2014 PEAK-System Technik GmbH, Darmstadt, Germany
//  All rights reserved.

#ifdef __cplusplus
extern "C" {
#endif

// Constants definitions

#define CAN_MAX_STANDARD_ID     0x7ff
#define CAN_MAX_EXTENDED_ID     0x1fffffff

// Baud rate codes = BTR0/BTR1 register values for the CAN controller
#define CAN_BAUD_1M     0x0014    //   1 MBit/s
#define CAN_BAUD_500K   0x001C    // 500 kBit/s
#define CAN_BAUD_250K   0x011C    // 250 kBit/s
#define CAN_BAUD_125K   0x031C    // 125 kBit/s
#define CAN_BAUD_100K   0x432F    // 100 kBit/s
#define CAN_BAUD_50K    0x472F    //  50 kBit/s
#define CAN_BAUD_20K    0x532F    //  20 kBit/s
#define CAN_BAUD_10K    0x672F    //  10 kBit/s
#define CAN_BAUD_5K     0x7F7F    //   5 kBit/s

// Error Codes
#define CAN_ERR_OK             0x0000  // No error
#define CAN_ERR_XMTFULL        0x0001  // Transmit buffer in CAN controller is full
#define CAN_ERR_OVERRUN        0x0002  // CAN controller was read too late
#define CAN_ERR_BUSLIGHT       0x0004  // Bus error: an error counter reached the 'light' limit
#define CAN_ERR_BUSHEAVY       0x0008  // Bus error: an error counter reached the 'heavy' limit  
#define CAN_ERR_BUSOFF         0x0010  // Bus error: the CAN controller is in bus-off state
#define CAN_ERR_QRCVEMPTY      0x0020  // Receive queue is empty
#define CAN_ERR_QOVERRUN       0x0040  // Receive queue was read too late
#define CAN_ERR_QXMTFULL       0x0080  // Transmit queue ist full
#define CAN_ERR_REGTEST        0x0100  // Test of the CAN controller hardware registers failed (no hardware found)
#define CAN_ERR_NOVXD          0x0200  // Driver not loaded
#define CAN_ERR_NODRIVER       0x0200  // Driver not loaded
#define CAN_ERRMASK_ILLHANDLE  0x1C00  // Mask for all handle errors
#define CAN_ERR_HWINUSE        0x0400  // Hardware already in use by a Net
#define CAN_ERR_NETINUSE       0x0800  // a Client is already connected to the Net
#define CAN_ERR_ILLHW          0x1400  // Hardware handle is invalid
#define CAN_ERR_ILLNET         0x1800  // Net handle is invalid
#define CAN_ERR_ILLCLIENT      0x1C00  // Client handle is invalid
#define CAN_ERR_RESOURCE       0x2000  // Resource (FIFO, Client, timeout) cannot be created
#define CAN_ERR_ILLPARAMTYPE   0x4000  // Invalid parameter
#define CAN_ERR_ILLPARAMVAL    0x8000  // Invalid parameter value
#define CAN_ERR_UNKNOWN        0x10000 // Unknown error
#define CAN_ERR_ILLFUNCTION    0x20000 // CAN-API function not supported

#define CAN_ERR_ANYBUSERR (CAN_ERR_BUSLIGHT | CAN_ERR_BUSHEAVY | CAN_ERR_BUSOFF)

// CAN Driver Types
#define CAN_DRIVERTYPE_UNKNOWN  0
#define CAN_DRIVERTYPE_9X       1
#define CAN_DRIVERTYPE_NT       2
#define CAN_DRIVERTYPE_WDM      3
#define CAN_DRIVERTYPE_WDF      4

// Object Types
#define CAN_OBJECT_DRIVER       0
#define CAN_OBJECT_HARDWARE     1
#define CAN_OBJECT_NET          2
#define CAN_OBJECT_CLIENT       3

// Codes for status messages and (Set|Get)(Hw|Net|Client)Param()

// A bus error, Value = CAN_ERR_...
#define CAN_PARAM_BUSERROR      1

// Number of the driver type (ISA, Dongle, ...)
#define CAN_PARAM_HWDRIVERNR    2

// Name of the Hardware/Driver/Net/Client
#define CAN_PARAM_NAME          3

// I/O address of the hardware
#define CAN_PARAM_HWPORT        4

// Hardware interrupt
#define CAN_PARAM_HWINT         5

// The Net that is connected to the Hardware
#define CAN_PARAM_HWNET         6

// Baud rate, as BTR0BTR1 code
#define CAN_PARAM_BAUDRATE      7

// Acceptance Code/Mask
// Only CAN-ID, bits 28..18 are relevant, even if you run in 11-bit mode!
// see also: CAN_PARAM_ACCCODE_STD / CAN_PARAM_ACCMASK_STD
#define CAN_PARAM_ACCCODE_EXTENDED 8
#define CAN_PARAM_ACCMASK_EXTENDED 9
//#define CAN_PARAM_ACCCODE CAN_PARAM_ACCCODE_EXTENDED // Downward compatibility
//#define CAN_PARAM_ACCMASK CAN_PARAM_ACCMASK_EXTENDED // Downward compatibility

// 0 = controller is in Reset mode, 1 = Operation mode
#define CAN_PARAM_ACTIVE        10

// Unsent messages in Transmit queue
#define CAN_PARAM_XMTQUEUEFILL  11

// Unread messages in Receive queue
#define CAN_PARAM_RCVQUEUEFILL  12

// Number of received messages since activation
#define CAN_PARAM_RCVMSGCNT     13

// Number of received bits since activation
#define CAN_PARAM_RCVBITCNT     14

// Number of transmitted messages since activation
#define CAN_PARAM_XMTMSGCNT     15

// Number of transmitted bits since activation
#define CAN_PARAM_XMTBITCNT     16

// Total number of received and transmitted messages
#define CAN_PARAM_MSGCNT        17

// Total number of received and transmitted bits
#define CAN_PARAM_BITCNT        18

// Hardware handle associated with Net
#define CAN_PARAM_NETHW         19

// Flag: Clients[i] <> 0: Client 'i' belongs to Net
#define CAN_PARAM_NETCLIENTS    20

// Window handle of Client
#define CAN_PARAM_HWND          21

// Flag: Nets[i] <> 0: Net 'i' belongs to Client
#define CAN_PARAM_CLNETS        22

// Transmit buffer size (Hardware, Client)
#define CAN_PARAM_XMTBUFFSIZE   23
#define CAN_PARAM_XMTQUEUESIZE  CAN_PARAM_XMTBUFFSIZE // Better name

// Receive buffer size
#define CAN_PARAM_RCVBUFFSIZE   24
#define CAN_PARAM_RCVQUEUESIZE  CAN_PARAM_RCVBUFFSIZE // Better name

// Handle of Receive Event
#define CAN_PARAM_ONRCV_EVENT_HANDLE  26

// Trigger mode of Receive Events (1 = Pulse, 0 = Set)
#define CAN_PARAM_ONRCV_EVENT_PULSE  27

// Self Receive
// 1 = Client receives all of its transmitted messages
#define CAN_PARAM_SELF_RECEIVE 28

// Delayed Message Distribution
// 0 = Transmits the messages to the other Clients while writing into the
//     Hardware queue (Net property)
// 1 = Transmits the messages to the other Clients only if Hardware has
//     successfully transmitted the message on the bus
#define CAN_PARAM_DELAYED_MESSAGE_DISTRIBUTION 29

// Unique reseller/distributor code for OEM Dongles; 32-bit unsigned integer
#define CAN_PARAM_HW_OEM_ID 30

// Location info: text that describes the "position" of the used Hardware.
// Example: "I/O addr 0x378", "PCI bus 0, slot 7, controller 1"
// Can be specified in the registry or will be created automatically
#define CAN_PARAM_LOCATION_INFO 31

// Number of the bus to which the Hardware is connected
#define CAN_PARAM_HWBUS         32

// PCI slot number to which the Hardware is connected
#define CAN_PARAM_HWDEVICE      33

// PCI function of card
#define CAN_PARAM_HWFUNCTION    34

// Number of the CAN Controller
#define CAN_PARAM_HWCONTROLLER  35

// Unlock code for 'Light'-drivers
#define CAN_PARAM_UNLOCKCODE    36

// Device driver type: 1=Win9x, 2=WinNT, 3=WDM
#define CAN_PARAM_DRIVERTYPE    37

// Measured values of the PCAN-USB adapter (special Hardware required)
#define CAN_PARAM_BUSLOAD       38
#define CAN_PARAM_ANALOG0       39
#define CAN_PARAM_ANALOG1       40
#define CAN_PARAM_ANALOG2       41
#define CAN_PARAM_ANALOG3       42
#define CAN_PARAM_ANALOG4       43
#define CAN_PARAM_ANALOG5       44
#define CAN_PARAM_ANALOG6       45
#define CAN_PARAM_ANALOG7       46

// Clock frequency of CAN controller
#define CAN_PARAM_CHIP_QUARTZ   47

// Values of the CAN controller timing registers (only for advanced users)
#define CAN_PARAM_CHIP_TIMING   48

// Listen Only mode: 1 = activated, 0 = deactivated
#define CAN_PARAM_LISTEN_ONLY   49

// USB device number
#define CAN_PARAM_HW_DEVICENR   50

// PEAK serial number
#define CAN_PARAM_HW_SERNR      51

// ISR timeout protection in Microseconds
#define CAN_PARAM_ISRTIMEOUT    52

// Error Frames
// != 0: Error frames will be received like messages
#define CAN_PARAM_RCVERRFRAMES  53

// Acceptance Code/Mask 11-bit type
#define CAN_PARAM_ACCCODE_STD   54
#define CAN_PARAM_ACCMASK_STD   55  // first set CODE, then set MASK !

// Exact 11-bit filtering
// 0 = Client filters by code/mask,
// 1 = Client filters exact Message ranges
#define CAN_PARAM_EXACT_11BIT_FILTER  56

// Location info that the user can set (USB string descriptor)
#define CAN_PARAM_USER_LOCATION_INFO  57

// Switch on/off "Select" LED (special hardware required)
#define CAN_PARAM_SELECT_LED  58

// Read Firmware version (PCAN-USB only)
#define CAN_PARAM_FIRMWARE_MAJOR  59
#define CAN_PARAM_FIRMWARE_MINOR  60

// CPU frequency in kHz (read-only, only NT/WDM)
#define CAN_PARAM_FCPU          61

// PCAN-USB: Waiting time after activating the hardware, in Milliseconds
#define CAN_PARAM_USBACTIVATEDELAY  64

// TimerFix
// != 0: Activates the PerformanceCounter correction
#define CAN_PARAM_TIMERFIX  65

// Client handle of Net Master
// 0 = no master defined
#define CAN_PARAM_NET_MASTER    66

// CANopen SDO-mode of the PCAN-USB adapter (special firmware required)
#define CAN_PARAM_SDO_MODE      67    // set: CAN_Write(); get: CAN_Read() (MSGTYPE_STATUS)
#define CAN_PARAM_SDO_QUEUEFILL 72    // set: CAN_Write(); get: CAN_Read() (MSGTYPE_STATUS)
#define CAN_PARAM_SDO_STATUS    73    // get: CAN_Read() (MSGTYPE_STATUS)

// Unprocessed mssages in the Delayed Transmit queue of a Client
#define CAN_PARAM_DELAYXMTQUEUEFILL  74

// Size of Delayed Transmit queue of Client
#define CAN_PARAM_DELAYXMTBUFFSIZE   75
#define CAN_PARAM_DELAYXMTQUEUESIZE  CAN_PARAM_DELAYXMTBUFFSIZE // Better name

// PCAN-USB: Check if CANopen SDO-mode is supported
#define CAN_PARAM_SDO_SUPPORT  76 

// Net: Client handle of the CANopen SDO master
// 0 = no master defined
#define CAN_PARAM_SDO_NET_MASTER  77
// Client: 1 = SDO_Status will be received
#define CAN_PARAM_SDO_RECEIVE  78

// Enables 5 V output on CAN connector (PCAN-PC Card only)
#define CAN_PARAM_BUSPOWER  79

// PCAN-1394: Waiting time after activating the hardware, in Milliseconds
#define CAN_PARAM_1394ACTIVATEDELAY  80

// USB/1394: <> 0: no warning message when unplugging Hardware (Win2000)
#define CAN_PARAM_SURPRISEREMOVALOK  81

// Self Receive: how is a self-received message identified?
// 0 = old behaviour: hRcvNet=0
// 1 = new behaviour: MSGTYPE_SELFRECEIVE
#define CAN_PARAM_MARK_SELFRECEIVED_MSG_WITH_MSGTYPE  82

// Error Warning Limit in SJA1000
#define CAN_PARAM_ERROR_WARNING_LIMIT  83

// Dual Filter Mode: use 1 or 2 acceptance filters
#define CAN_PARAM_ACCFILTER_COUNT  84

// Dual Filter Mode: Code/Mask of second filter, 11-bit format
#define CAN_PARAM_ACCCODE1_STD        85
#define CAN_PARAM_ACCMASK1_STD        86 // first set CODE, then set MASK !
// Dual Filter Mode: Code/Mask of second filter, 29-bit format
#define CAN_PARAM_ACCCODE1_EXTENDED   87
#define CAN_PARAM_ACCMASK1_EXTENDED   88 // first set CODE, then set MASK !

// Patch for PCAN-USB: sets the Reset/BusOn mode of SJA1000
#define  CAN_PARAM_BUSON  90

// Load "Hardware" keys from Registry? Default: 1
#define CAN_PARAM_REGISTRYHARDWARELOADING  92

// A bus error, value = CAN_ERR_Q...
#define CAN_PARAM_QUEUEERROR  94

// Offset for the system clock GetSystemTime() and all timestamps in Milliseconds
#define CAN_PARAM_SYSTEMTIME_ADJUST  95

// Auto BusON:
// 1 = Automatic BusON after BusOFF
#define CAN_PARAM_AUTOBUSON  96

// Driver version number
#define CAN_PARAM_VERSIONSTR  97

// Firmware revision number
#define CAN_PARAM_FIRMWARE_REVISION  100

// PCAN-USB Pro: Version of Boot Loader
#define CAN_PARAM_BOOTLOADER_MAJOR     101
#define CAN_PARAM_BOOTLOADER_MINOR     102
#define CAN_PARAM_BOOTLOADER_REVISION  103

// Sample time for bus load measurement in Microseconds
#define CAN_PARAM_BUSLOAD_SAMPLETIME  106

// PCAN-USB Pro: CPLD revision
#define	CAN_PARAM_CPLD_REVISION  108

// Hardware revision
#define	CAN_PARAM_HARDWARE_REVISION  109

// PCAN-USB Pro: Creation of bus errors
#define	CAN_PARAM_BUSERRORGENERATION  110
// Parameters are communicated like strings, but are of type TCAN_PARAM_BUSERRORGENERATION
#pragma pack(push, 1)
typedef struct TCAN_PARAM_BUSERRORGENERATION
{
    WORD  mode;           // 0 = Off, 1 = Repeated, 2 = Single
    WORD  bit_pos;        // Bit position
    DWORD id;             // CAN-ID
    WORD  ok_counter;     // OK CAN message counter
    WORD  error_counter;  // Error CAN message counter
} TCAN_PARAM_BUSERRORGENERATION;
#pragma pack(pop)

// Client: accumulated ERR_QXMTFULL errors of a hardware, if sending from DelayXmtQueue
#define CAN_PARAM_DELAYXMTQUEUE_ERR_QXMTFULL_COUNT  113

// Internal: measured resolution of KeQueryPerformanceCounter()
#define CAN_PARAM_PERFORMANCEFREQUENCY  116

// Client: enable/disable Remote Request Frames reception
#define CAN_PARAM_RCVRTRFRAMES  119

// Client: enable/disable Status Frames
#define CAN_PARAM_RCVSTATUSFRAMES  120

// Version info for driver
#define CAN_PARAM_VERSION_MAJOR  122
#define CAN_PARAM_VERSION_MINOR  123
#define CAN_PARAM_VERSION_REVISION  124
#define CAN_PARAM_VERSION_BUILD  125
#define CAN_PARAM_VERSION_DEBUG  126


#define MAX_HCANHW      16      // only Hardware 1 .. MAX_HCANHW permitted
#define MAX_HCANNET     32      // only Net 1 .. MAX_HCANNET permitted
#define MAX_HCANCLIENT  64      // only Clients 1 .. MAX_HCANCLIENT permitted
#define MAX_HCANMEM = 2 * MAX_HCANCLIENT // max. 2 Memory blocks per Client

#define MAX_NETNAMELEN     20   // max. length of a Net name
#define MAX_CLIENTNAMELEN  20   // max. length of a Client name
#define MAX_DRIVERNAMELEN  32   // max. length of a device name

#define CAN_DIAGBUFFLEN   2048  // size of internal buffer for debug output

#define MAX_STRINGPARAMLEN 256  // max. size of strings in CAN_Get/Set..Param()
#define MAX_STRINGORRECORD_PARAMLEN 256  // max. size of strings or records in CAN_Get/Set..Param()
#define MAX_READ_MULTI_MSGCOUNT   32768 // max. number of messages to read with CAN_Read_Multi

// Bits in the TCANMsg.MSGTYPE field
#define MSGTYPE_STANDARD    0x00  // Standard Data frame (11-bit ID)
#define MSGTYPE_RTR         0x01  // 1, if Remote Request frame
#define MSGTYPE_EXTENDED    0x02  // 1, if Extended Data frame (CAN 2.0B, 29-bit ID)
#define MSGTYPE_SELFRECEIVE 0x04  // 1, if message shall be/has been self-received by the controller
#define MSGTYPE_SINGLESHOT  0x08  // 1, if no re-transmission shall be performed for the message (self ACK)
#define MSGTYPE_PARAMETER   0x20  // 1, if message describes a parameter (e.g. USB-SDO)
#define MSGTYPE_ERRFRAME    0x40  // 1, if Error frame
#define MSGTYPE_BUSEVENT  MSGTYPE_ERRFRAME
#define MSGTYPE_STATUS      0x80  // 1, if Status information
#define MSGTYPE_NONMSG      0xF0  // <> 0, if message is a Status

// Type definitions

typedef BYTE HCANHW;        // Type 'Hardware Handle'
typedef BYTE HCANNET;       // Type 'Hardware Handle'
typedef BYTE HCANCLIENT;    // Type 'Client Handle'
typedef BYTE HCANMEM;       // Type 'Memory Handle'
typedef BYTE HCANOBJECT;    // Any handle type

typedef DWORD TCANStatus;

#pragma pack(push, 1)       // The following structures are Byte-aligned


// Timestamp of a receive/transmit event
// Total microseconds = micros + 1000 * millis + 0x100000000 * 1000 * millis_overflow
typedef struct tagTCANTimestamp
{
    DWORD millis;          // base-value: milliseconds: 0.. 2^32-1
    WORD  millis_overflow; // roll-arounds of millis
    WORD  micros;          // microseconds: 0..999
} TCANTimestamp;


// A CAN message
typedef struct tagTCANMsg
{
    DWORD ID;        // 11-/29-bit CAN-ID
    BYTE  MSGTYPE;   // Bits from MSGTYPE_...
    BYTE  LEN;       // Data Length Code (0..8)
    BYTE  DATA[8];   // Data bytes 0..7
} TCANMsg;

// CAN messages that are read via the Read_Multi() function
typedef struct tagTCANRcvMsg
{
    TCANMsg       msgbuff; // Message
    HCANNET       hNet;    // The Net that received the message
    TCANTimestamp rcvtime; // The reception time of the message
} TCANRcvMsg;


#pragma pack(pop)


///////////////////////////////////////////////////////////////////////////////
// Function prototypes

//-------------------------------------------------------------------------
// CAN_GetDeviceName()
//   Gets the name of the current device.
// Parameters:
//   szBuff: Buffer for the device name
//
// Possible errors: None

TCANStatus __stdcall CAN_GetDeviceName(LPSTR szBuff);


//-------------------------------------------------------------------------
// CAN_SetDeviceName()
//   Sets the name of the current device (e.g. "peakcan", "pcan_pci")
// Parameters:
//   szDeviceName: The device name
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_SetDeviceName(LPSTR szDeviceName);


//-------------------------------------------------------------------------
// CAN_RegisterHardware()
//   Activates a Hardware, performs a CAN controller register test,
//   allocates transmit buffer, and assigns a Hardware handle.
//   Programs the configuration of transmit and receive drivers.
//   Controller stays in Reset mode.
//   There are more than one Hardware at the same IRQ allowed.
// Parameters:
//   hHw:        Requested Hardware handle (is managed by caller)
//   wDriverNo:  No. of the device driver to use
//   wBusID:     Code of bus type for Hardware (0=ISA)
//   dwPortBase: I/O address of card in PC
//   wIntNo:     Used Hardware IRQ
//
// Possible errors: NODRIVER ILLHW REGTEST RESOURCE 

TCANStatus __stdcall CAN_RegisterHardware(
        HCANHW hHw,
        WORD   wDriverNo,
        WORD   wBusID,
        DWORD  dwPortBase,
        WORD   wIntNo);


//-------------------------------------------------------------------------
// RegisterHardwarePCI()
//   Activates a Hardware, performs a CAN controller register test,
//   allocates transmit buffer, and assigns a Hardware handle.
//   Programs the configuration of transmit and receive drivers.
//   Controller stays in Reset mode.
//   There are more than one Hardware at the same IRQ allowed.
// Parameters:
//   hHw:               Requested Hardware handle (is managed by caller)
//   wDriverNo:         No. of the device driver to use (0x101=PCI)
//   dwPCIslotBus:      Which PCI bus?
//   dwPCIslotDevice:   Which slot?
//   dwPCIslotFunction: Bus code of card
//   dwControllerNo:    Which CAN controller on card?
//
// Possible errors: NODRIVER ILLHW REGTEST RESOURCE 
        
TCANStatus __stdcall CAN_RegisterHardwarePCI(
        HCANHW hHw,
        WORD   wDriverNo,
        DWORD  dwPCIslotBus,
        DWORD  dwPCIslotDevice,
        DWORD  dwPCIslotFunction,
        DWORD  dwControllerNo);


//-------------------------------------------------------------------------
// CAN_RegisterNet()
//   Adds a Net to the driver's Net list.
// Parameters:
//   hNet:      Requested Net handle (managed by caller)
//   lpszName:  Name of the Net
//   hHw:       Associated Hardware handle, 0 if internal Net
//   wBTR0BTR1: see CAN_BAUD_... defines
//
// Possible errors: NODRIVER ILLNET ILLHW

TCANStatus __stdcall CAN_RegisterNet(
        HCANNET hNet,
        LPCSTR  lpszName,
        HCANHW  hHw,
        WORD    wBTR0BTR1);


//-------------------------------------------------------------------------
// CAN_RemoveNet()
//   Deletes a Net definition from the driver's Net list.
// Parameters:
//   hNet: Remove this Net
//
// Possible errors: NODRIVER ILLNET NETINUSE

TCANStatus __stdcall CAN_RemoveNet(HCANNET hNet);


//-------------------------------------------------------------------------
// CAN_RemoveHardware()
//   Deactivates a Hardware, frees all resources.
// Parameters:
//   hHw: Remove this Hardware.
//
// Possible errors: NODRIVER ILLHW

TCANStatus __stdcall CAN_RemoveHardware(HCANHW hHw);


//-----------------------------------------------------------------------------
// CAN_CloseAll()
//   Closes all Hardware, unregisters all Nets and Clients.
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_CloseAll(void);


//-----------------------------------------------------------------------------
// CAN_Status()
//   Gets the current state of the Hardware (e.g. BUSOFF, OVERRUN...)
// Parameters:
//   hHw: Return the state of this Hardware
//
// Possible errors: NODRIVER ILLHW BUSOFF BUSHEAVY OVERRUN

TCANStatus __stdcall CAN_Status(HCANHW hHw);


//-----------------------------------------------------------------------------
// CAN_ResetHardware()
//   Resets the Hardware (CAN controller) and initializes the controller
//   with the last valid Baud rate and filter settings.
//   If a Net is connected to a Hardware:
//   Resets the CAN controller, flushes the Transmit queue.
//   Affects the other Clients that are connected to the Net.
// Parameters:
//   hHw: Reset this Hardware
//
// Possible errors: NODRIVER ILLHW REGTEST

TCANStatus __stdcall CAN_ResetHardware(HCANHW hHw);


//-----------------------------------------------------------------------------
// CAN_ResetClient()
//   Resets the receive and transmit queues of a Client.
//
// Possible errors: NODRIVER ILLCLIENT

TCANStatus __stdcall CAN_ResetClient(HCANCLIENT hClient);


//-----------------------------------------------------------------------------
// CAN_Write()
//   The Client 'hClient' transmits a message at the time 'sendTime' to the Net
//   'hNet'. The message is written into the Transmit queue of an associated
//   Hardware and into the Receive queues of all other Clients which are connected
//   to the Net.
//   If the transmit time is the current time or is in the past, the message will
//   be transmitted immediately. If the transmit time is in the future, the driver
//   will transmit the message when the time is reached.
//
// Possible errors: NODRIVER RESOURCE ILLCLIENT ILLNET BUSOFF QXMTFULL

TCANStatus __stdcall CAN_Write(
        HCANCLIENT      hClient,        // Handle of the transmitting Client
        HCANNET         hNet,           // Write message to this net
        TCANMsg*        pMsgBuff,       // Message
        TCANTimestamp*  pSendTime);     // Timestamp


//-----------------------------------------------------------------------------
// CAN_Read()
//   Reads the next message/error/status information from a Client's Receive
//   queue. The message will be written to 'msgbuff'.
//
// Possible errors: NODRIVER ILLCLIENT QRCVEMPTY BUSLIGHT BUSHEAVY BUSOFF
//                  OVERRUN QOVERRUN

TCANStatus __stdcall CAN_Read(
        HCANCLIENT      hClient,        // Read from the RcvQueue of this Client
        TCANMsg*        pMsgBuff,       // Return buffer for message/error/status information
        HCANNET*        phNet,          // The Net from which the message has been received
        TCANTimestamp*  pRcvTime);      // Receive timestamp


//-----------------------------------------------------------------------------
// CAN_Read_Multi()
//   Reads several received messages.
//   Works like multiple calls of Read().
//   MultiMsgBuff must be an array of 'nMaxMsgCount' entries.
//   The size 'nMaxMsgCount' of the array = max. messages that can be received.
//   The real number of read messages will be returned in nMsgCount.
//   The return value is the one of the last Read() call.
//
// Possible errors: NODRIVER ILLCLIENT QRCVEMPTY BUSLIGHT BUSHEAVY BUSOFF
//                  OVERRUN QOVERRUN

TCANStatus __stdcall CAN_Read_Multi(
        HCANCLIENT  hClient,       // Read messages from Receive queue of this Client
        TCANRcvMsg* pMultiMsgBuff, // Message buffer
        long        nMaxMsgCount,  // Number of messages the buffer can store
        long*       pMsgCount);    // Number of read messages


//-----------------------------------------------------------------------------
// CAN_RegisterClient()
//   Registers a Client at the device driver. Creates a Client handle and
//   allocates the Receive queue (only one per Client). The hWnd parameter
//   can be zero for DOS Box Clients. The Client does not receive any
//   messages until RegisterMsg() or SetClientFilter() is called.
//
// Possible errors: NODRIVER RESOURCE

TCANStatus __stdcall CAN_RegisterClient(
        LPCSTR      lpszName,     // Name of the Client
        DWORD       hWnd,         // the Window handle of the Client (only for information purposes)
        HCANCLIENT* phClient);    // Returns the Client handle


//-----------------------------------------------------------------------------
// CAN_ConnectToNet()
//   Connects a Client to a Net.
//   The Net is assigned by its name. The Hardware is initialized with the
//   Baud rate if it is the first Client which connects to the Net.
//   If the Hardware is already in use by another Net, the connection fails and
//   the error ERR_HWINUSE will be returned.
//
// Possible errors: NODRIVER ILLCLIENT ILLNET ILLHW HWINUSE REGTEST

TCANStatus __stdcall CAN_ConnectToNet(
        HCANCLIENT hClient,       // Connect this Client...
        LPSTR      lpszNetName,   // ...to this Net
        HCANNET*   phNet);        // Returns the Net handle


//-----------------------------------------------------------------------------
// CAN_RegisterMsg()
//   Announces that the Client wants to receive messages from the Net 'hNet'.
//   The messages msg1.ID to msg2.ID will be received.
//   The ID and MSGTYPE fields will be used, all other fields are ignored.
//   msg1.ID <= msg2.ID, msg1.MSGTYPE = msg2.MSGTYPE.
//   There is only ONE filter for Standard and Extended messages.
//   The Standard messages will be registered as if the ID was built with
//   the bits in positions 28..18.
//   Example: registration of Standard ID 0x400 means that the Extended ID
//   0x10000000 will be also received.
//   If the indicated CAN-ID range requires a reconfiguration of the CAN
//   controller, the CAN controller performs a Hardware reset.
//   It is not guaranteed that the Client only receives the messages with
//   the indicated CAN-ID range. The actually received messages depend on
//   the used CAN controller (usually SJA100/82C200).
//
// Possible errors: NODRIVER ILLCLIENT ILLNET REGTEST

TCANStatus __stdcall CAN_RegisterMsg(
        HCANCLIENT     hClient, // This Client...
        HCANNET        hNet,    // wants to receive from this Net...
        const TCANMsg* pMsg1,   // all messages from msg1.ID ...
        const TCANMsg* pMsg2);  // to msg2.ID


//-----------------------------------------------------------------------------
// CAN_RemoveAllMsgs()
//   Resets the filter of a Client.
//
// Possible errors: NODRIVER ILLCLIENT ILLNET

TCANStatus __stdcall CAN_RemoveAllMsgs(
        HCANCLIENT hClient,     // Reset the filter of this Client
        HCANNET    hNet);       // This parameter has no meaning


//-----------------------------------------------------------------------------
// CAN_SetClientFilter()
//   Sets the filter of a Client, of the connected Net, and of the
//   connected Hardware.
//
// Possible errors: NODRIVER ILLCLIENT ILLNET

TCANStatus __stdcall CAN_SetClientFilter(
        HCANCLIENT hClient,     // This Client...
        HCANNET    hNet,        // wants to set for this Net...
        long       nExtended,   // this filter...
        DWORD      dwAccCode,
        DWORD      dwAccMask);


//-----------------------------------------------------------------------------
// CAN_SetClientFilterEx()
//   Sets the filters of a Client, of the connected Net, and of the
//   connected Hardware.
//
// Possible errors: NODRIVER ILLCLIENT ILLNET ILLPARAMVAL

TCANStatus __stdcall CAN_SetClientFilterEx(
        HCANCLIENT hClient,       // This Client...
        HCANNET    hNet,          // wants to set for this Net...
        DWORD      dwFilterIndex, // this filter...
        DWORD      dwFilterMode,
        long       nExtended,
        DWORD      dwAccCode, 
        DWORD      dwAccMask);


//-----------------------------------------------------------------------------
// CAN_DisconnectFromNet()
//   Disconnects a Client from a Net. This means: no more messages will be
//   received by this Client. Each call of this function can change the
//   filter of the connected Hardware, so that the CAN controller must be
//   reset.
//
// Possible errors: NODRIVER ILLCLIENT ILLNET REGTEST

TCANStatus __stdcall CAN_DisconnectFromNet(
        HCANCLIENT hClient,  // Disconnect this Client...
        HCANNET    hNet);    // from this Net


//-----------------------------------------------------------------------------
// CAN_RemoveClient()
//   Removes a Client from the Client list in the device driver. Free all
//   resources (Receive/Transmit queues etc.)
//   Each call of this function can change the filter of the connected
//   Hardware, so that the CAN controller must be reset.
//
// Possible errors: NODRIVER ILLCLIENT

TCANStatus __stdcall CAN_RemoveClient(
        HCANCLIENT hClient);  // Remove this Client and free all resources


//-----------------------------------------------------------------------------
// CAN_GetDriverName()
//   Returns the name of the driver of the supported Hardware index 'i'.
//   Start i=1; end of the list is reached when the returned string is
//   empty.
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_GetDriverName(
        SHORT i,             // Index of the Hardware type  
        LPSTR lpszNameBuff); // Text buffer to return the name


//-----------------------------------------------------------------------------
// CAN_Msg2Text()
//  For debugging: generates a text string that describes a CAN message.
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_Msg2Text(
        TCANMsg* pMsgBuff,         // The message to translate
        LPSTR    lpszTextBuff);    // Buffer to return the text


//-----------------------------------------------------------------------------
// CAN_GetDiagnostic()
//   For debugging: returns the diagnosis text buffer
//   (max. CAN_DIAGBUFFLEN characters).
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_GetDiagnostic(
        LPSTR lpszTextBuff);       // Buffer for diagnosis text


//-----------------------------------------------------------------------------
// CAN_GetSystemTime()
//   Gets the internal device driver timer value of the Virtual Machine
//   Manager.
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_GetSystemTime(TCANTimestamp* pTimeBuff);


//-----------------------------------------------------------------------------
// CAN_GetErrText()
//   Converts the error code 'dwError' to a text containing an error
//   desription.
//
// Possible errors: keine

TCANStatus __stdcall CAN_GetErrText(
        DWORD dwError,
        LPSTR lpszTextBuff);       // Buffer for error text


//-----------------------------------------------------------------------------
// CAN_SetHwParam()
//   Sets a Hardware parameter to a given value.
// Parameters:
//   hHw:     a valid Hardware handle
//   wParam:  a CAN_PARAM_... constant (see below)
//   dwValue: the value of the parameter
//
// Allowed CAN_PARAM_... constants in wParam (depend on used CAN hardware):
//   CAN_PARAM_BAUDRATE            int       Sets a new Baud rate for a Hardware.
//                                           Baud rate as 16-bit BTR0BTR1 code.
//                                           Affects all other Clients connected to
//                                           the Net! 
//   CAN_PARAM_LOCATION_INFO       char[250] Info text about location of the Hardware
//   CAN_PARAM_LISTEN_ONLY         int       Activates the Listen Only Mode.
//                                           1=on, 0=off (default)
//   CAN_PARAM_HW_DEVICENR         int       USB: Device number.
//   CAN_PARAM_HW_SERNR            int       USB: PEAK serial number
//   CAN_PARAM_USER_LOCATION_INFO  char[250] User-defined information about Hardware
//   CAN_PARAM_SELECT_LED          int       "Select" LED on/off
//   CAN_PARAM_SDO_MODE            int       USB
//   CAN_PARAM_SDO_QUEUEFILL       int       USB
//   CAN_PARAM_BUSPOWER            int       PC Card: Enables 5 V output on CAN connector,
//                                           1 = enabled
//   CAN_PARAM_ERROR_WARNING_LIMIT int       Error Warning Limit Register of SJA1000
//
// Possible errors: NODRIVER ILLHW ILLPARAMTYPE ILLPARAMVAL REGTEST

TCANStatus __stdcall CAN_SetHwParam(
        HCANHW   hHw,
        WORD     wParam,
        UINT_PTR dwValue);


//-----------------------------------------------------------------------------
// CAN_GetHwParam()
//    Gets a Hardware parameter.
// Parameters:
//   hHw:      a valid Hardware handle
//   wParam:   a CAN_PARAM_* constant (see below)
//   pBuff:    a pointer to a buffer, which stores the return value.
//   wBuffLen: the size of the return buffer (used only for string return
//             values, other types have a fixed size).
//
// Allowed CAN_PARAM_... constants in wParam (depend on used CAN hardware):
//   CAN_PARAM_HWDRIVERNR          int       No. of Driver type (ISA, Dongle, ..)
//   CAN_PARAM_NAME                char[MAX_DRIVERNAMELEN+1]
//                                           Name of the Hardware
//   CAN_PARAM_HWPORT              int       Port address of Hardware
//   CAN_PARAM_HWINT               int       No. of the Hardware IRQ
//   CAN_PARAM_HWNET               int       Handle of the Net that is currently
//                                           connected to the Hardware
//   CAN_PARAM_BAUDRATE            int       Baud rate as 16-bit BTR0BTR1 code
//   CAN_PARAM_ACCCODE_EXTENDED    int       29-bit Acceptance Filter code
//   CAN_PARAM_ACCMASK_EXTENDED    int       29-bit Acceptance Filter mask
//                                           (only ID field, bits 28..18 are relevant)
//   CAN_PARAM_ACCCODE_STD         int       11-bit Acceptance Filter mask
//   CAN_PARAM_ACCMASK_STD         int       11-bit Acceptance Filter code
//                                           (only ID field, bits 10..0 are relevant)
//   CAN_PARAM_ACCFILTER_COUNT     int       Dual Filter Mode
//                                           1 = one filter (default), 2 = two filters
//   CAN_PARAM_ACTIVE              int       0 = Controller is in Reset mode, 1 = Operation mode
//   CAN_PARAM_XMTQUEUEFILL        int       Number of messages im Transmit queue
//   CAN_PARAM_RCVMSGCNT           int       Number of received messages
//   CAN_PARAM_RCVBITCNT           int       Number of received bits
//   CAN_PARAM_XMTMSGCNT           int       Number of transmitted messages
//   CAN_PARAM_XMTBITCNT           int       Number of transmitted bits
//   CAN_PARAM_MSGCNT              int       Number of transmitted and received messages
//   CAN_PARAM_BITCNT              int       Number of transmitted and received bits
//   CAN_PARAM_LOCATION_INFO       char[250] Information text about Hardware location
//   CAN_PARAM_HWBUS               int       The bus, to which the Hardware is connected
//   CAN_PARAM_HWDEVICE            int       PCI slot
//   CAN_PARAM_HWFUNCTION          int       PCI slot function
//   CAN_PARAM_HWCONTROLLER        int       No. of the used controller on the Hardware
//   CAN_PARAM_LISTEN_ONLY         int       Listen Only mode activated? 1 = activated
//   CAN_PARAM_RCVERRFRAMES        int       Error Frames activated ? 1 = activated
//   CAN_PARAM_HW_DEVICENR         int       USB: Device number
//   CAN_PARAM_HW_SERNR            int       USB: PEAK serial number
//   CAN_PARAM_BUSLOAD             int       USB: Busload
//   CAN_PARAM_USER_LOCATION_INFO  char[250] USB: User-defined information about Hardware
//   CAN_PARAM_FIRMWARE_MAJOR      int       USB: Firmware version (major revision)
//   CAN_PARAM_FIRMWARE_MINOR      int       USB: Firmware version (minor revision)
//   CAN_PARAM_SDO_SUPPORT         int       USB: CANopen SDO-mode support
//   CAN_PARAM_ANALOG0..7          int       USB: A/D channels (not used)
//   CAN_PARAM_BUSPOWER            int       PC Card: 5 V output on CAN connector enabled?
//                                           1 = enabled
//   CAN_PARAM_ERROR_WARNING_LIMIT int       Error Warning Limit Register of SJA1000
//
// Possible errors: NODRIVER ILLHW ILLPARAMTYPE

TCANStatus __stdcall CAN_GetHwParam(
        HCANHW hHw,
        WORD   wParam,
        void*  pBuff,
        WORD   wBuffLen);


//-----------------------------------------------------------------------------
// CAN_SetNetParam()
//   Sets a Net parameter to a given value.
// Parameters:
//   hNet:    a valid Net handle
//   wParam:  a CAN_PARAM_... constant (see below)
//   dwValue: the value of the parameter
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_DELAYED_MESSAGE_DISTRIBUTION
//                             int    1 = push message to the Net after the
//                                    Hardware has physically transmitted the
//                                    message
//   CAN_PARAM_NET_MASTER      int    Client handle of Net master
//   CAN_PARAM_SDO_NET_MASTER  int    Client handle of SDO Net master
//
// Possible errors: NODRIVER ILLNET ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_SetNetParam(
        HCANNET  hNet,
        WORD     wParam,
        UINT_PTR dwValue);


//-----------------------------------------------------------------------------
// CAN_GetNetParam()
//   Gets a Net parameter.
// Parameters:
//   hNet:     a valid Net handle
//   wParam:   a CAN_PARAM_... constant (see below)
//   pBuff:    a pointer to a buffer which stores the return value
//   wBuffLen: the size of the return buffer (used only for string
//             return values, other types have a fixed size).
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_NAME            char[MAX_NETNAMELEN+1]
//                                       Name of the Net
//   CAN_PARAM_BAUDRATE        int       Baud rate, as 16-bit BTR0BTR1 code
//   CAN_PARAM_MSGCNT          int       Number of transported messages
//   CAN_PARAM_BITCNT          int       Number of transported bits
//   CAN_PARAM_NETHW           int       Hardware handle of the Net
//   CAN_PARAM_NETCLIENTS      char[MAX_HCANCLIENT+1]
//                                       Flag[i] <> 0: Client 'i' belongs to
//                                       Net 'hNet'
//   CAN_PARAM_DELAYED_MESSAGE_DISTRIBUTION
//                             int       1 = messages are passed on to the Net
//                                       after the Hardware has physically
//                                       transmitted the message
//   CAN_PARAM_RCVERRFRAMES    int       1 = Error Frames are activated
//   CAN_PARAM_NET_MASTER      int       Client handle of Net masters
//   CAN_PARAM_SDO_NET_MASTER  int       Client handle of SDO Net master
//
// Possible errors: NODRIVER ILLNET ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_GetNetParam(
        HCANNET hNet,
        WORD    wParam,
        void*   pBuff,
        WORD    wBuffLen);


//-----------------------------------------------------------------------------
// CAN_SetClientParam()
//   Sets a Client parameter to a given value.
// Parameters:
//   hClient: a valid Client handle
//   wParam:  a CAN_PARAM_... constant (see below)
//   dwValue: the value of the parameter
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_ONRCV_EVENT_HANDLE  int     Event handle of the ONRCV-event
//   CAN_PARAM_ONRCV_EVENT_PULSE   int     Event Trigger mode:
//                                         1 = PulseEvent, 0 = SetEvent
//   CAN_PARAM_SELF_RECEIVE        int     1 = receive own transmitted messages
//   CAN_PARAM_RCVERRFRAMES        int     1 = Error Frames activated
//   CAN_PARAM_EXACT_11BIT_FILTER  int     1 = Exact filtering of 11-bit
//                                         messages
//   CAN_PARAM_SDO_RECEIVE         int     1 = SDO_Status will be received
//   CAN_PARAM_ACCFILTER_COUNT     int     Dual Filter Mode
//                                         1 = one filter (default), 2 = two filters
//
// Possible errors: NODRIVER ILLCLIENT ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_SetClientParam(
        HCANCLIENT hClient,
        WORD       wParam,
        UINT_PTR   dwValue);


//-----------------------------------------------------------------------------
// CAN_GetClientParam()
//   Gets a Client parameter.
// Parameters:
//   hClient:  a valid Client handle
//   wParam:   a CAN_PARAM_... constant (see below)
//   pBuff:    a pointer to a buffer which stores the return value.
//   wBuffLen: the size of the return buffer (used only for string return
//             values, other types have a fixed size).
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_NAME               char[MAX_CLIENTNAMELEN+1]
//                                         Name of the Client
//   CAN_PARAM_ACCCODE_EXTENDED   int      29-bit Acceptance Filter code
//   CAN_PARAM_ACCMASK_EXTENDED   int      29-bit Acceptance Filter mask
//                                         (only ID field, bits 28..18 are relevant)
//   CAN_PARAM_ACCCODE_STD        int      11-bit Acceptance Filter mask
//   CAN_PARAM_ACCMASK_STD        int      11-bit Acceptance Filter mask
//                                         (only ID field, bits 10..0 are relevant)
//   CAN_PARAM_ACCFILTER_COUNT    int      Dual Filter Mode
//                                         1 = one filter (default), 2 = two filters
//   CAN_PARAM_RCVQUEUESIZE       int      Size of the Receive queue
//   CAN_PARAM_RCVQUEUEFILL       int      unread messages in Receive queue
//   CAN_PARAM_XMTQUEUESIZE       int      Size of the Transmit queue
//   CAN_PARAM_DELAYXMTQUEUESIZE  int      Size of the Delay Transmit queue
//   CAN_PARAM_XMTQUEUEFILL       int      unsent messages in Transmit queue
//   CAN_PARAM_DELAYXMTQUEUEFILL  int      unsent messages in Delay Transmit queue
//   CAN_PARAM_RCVMSGCNT          int      Number of received messages
//   CAN_PARAM_RCVBITCNT          int      Number of received bits
//   CAN_PARAM_XMTMSGCNT          int      Number of transmitted messages
//   CAN_PARAM_XMTBITCNT          int      Number of transmitted bits
//   CAN_PARAM_MSGCNT             int      Number of totally transmitted and
//                                         received messages
//   CAN_PARAM_BITCNT             int      Number of totally transmitted and
//                                         received bits
//   CAN_PARAM_HWND               int      Window handle of the Client application
//                                         (can be zero for DOS Box Clients)
//   CAN_PARAM_CLNETS             char[MAX_HCANNET+1]
//                                         Flag[i] <> 0: Net 'i' belongs to
//                                         Client 'hClient'
//   CAN_PARAM_ONRCV_EVENT_HANDLE int      Event handle of the ONRCV-events
//   CAN_PARAM_ONRCV_EVENT_PULSE  int      Event Trigger mode:
//                                         1 = PulseEvent, 0 = SetEvent
//   CAN_PARAM_SELF_RECEIVE       int      1 = Receive all transmitted messages
//   CAN_PARAM_RCVERRFRAMES       int      1 = Error Frames activated
//   CAN_PARAM_EXACT_11BIT_FILTER int      1 = Exact filtering of 11-bit messages
//   CAN_PARAM_SDO_RECEIVE        int      1 = SDO_Status will be received
//
// Possible errors: NODRIVER ILLCLIENT ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_GetClientParam(
        HCANCLIENT hClient,
        WORD       wParam,
        void*      pBuff,
        WORD       wBuffLen);


//-----------------------------------------------------------------------------
// CAN_VersionInfo()
//   Returns a string containing Copyright information and the device
//   driver version number (max. 255 characters).
//
// Possible errors: NODRIVER

TCANStatus __stdcall CAN_VersionInfo(LPSTR lpszTextBuff);


//-----------------------------------------------------------------------------
// CAN_SetDriverParam()
//   Sets a driver parameter to a given value.
// Parameters:
//   wParam:  a CAN_PARAM_... constant (see below)
//   dwValue: the value of the parameter
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_UNLOCKCODE        int    Code to enable special driver features
//                                      (not used)
//   CAN_PARAM_ISRTIMEOUT        int    Runtime limit of ISR in Milliseconds
//   CAN_PARAM_USBACTIVATEDELAY  int    USB: waiting time after activating the
//                                      hardware, in Milliseconds
//   CAN_PARAM_1394ACTIVATEDELAY int    PCAN-1394: waiting time after activating
//                                      the hardware, in Milliseconds
//   CAN_PARAM_SURPRISEREMOVALOK int    <> 0: USB/1394: no warning message when
//                                      unplugging Hardware (Win2000)
//   CAN_PARAM_TIMERFIX          int    <> 0: activates the correction of wrong
//                                      PerformanceCounter values caused by
//                                      certain chip sets
//   CAN_PARAM_RCVQUEUESIZE      int    Size of Receive queue
//   CAN_PARAM_XMTQUEUESIZE      int    Size of Transmit queue
//   CAN_PARAM_DELAYXMTQUEUESIZE int    Size of Delay Transmit queue
//   CAN_PARAM_AUTOBUSON         int    1 = Automatic BusON after BusOFF
//
// Possible errors: NODRIVER ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_SetDriverParam(
        WORD     wParam,
        UINT_PTR dwValue);


//-----------------------------------------------------------------------------
// CAN_GetDriverParam()
//   Gets a driver parameter.
// Parameters:
//   wParam:   a CAN_PARAM_... constant (see below)
//   pBuff:    a pointer to a buffer which stores the return value
//   wBuffLen: the size of the return buffer (used only for string return
//             values, other types have a fixed size).
//
// Allowed CAN_PARAM_... constants in wParam:
//   CAN_PARAM_UNLOCKCODE        int    Code to enable special driver features
//                                      (not used)
//   CAN_PARAM_ISRTIMEOUT        int    Runtime limit of ISR in Milliseconds
//   CAN_PARAM_USBACTIVATEDELAY  int    USB: waiting time after activating the
//                                      hardware, in Milliseconds
//   CAN_PARAM_DRIVERTYPE        int    System: 9x/NT/WDM ?
//   CAN_PARAM_RCVQUEUESIZE      int    Size of Receive queue
//   CAN_PARAM_XMTQUEUESIZE      int    Size of Transmit queue
//   CAN_PARAM_DELAYXMTQUEUESIZE int    Size of Delay Transmit queue
//   CAN_PARAM_FCPU              int    CPU frequency in KHz (available 1
//                                      second after CAN_Init(), only NT/WDM)
//   CAN_PARAM_TIMERFIX          int    <> 0: correction of wrong
//                                      PerformanceCounter values caused by
//                                      certain chip sets activated
//   CAN_PARAM_SURPRISEREMOVALOK int    <> 0: USB/1394: no warning message when
//                                      unplugging Hardware (Win2000)
//   CAN_PARAM_VERSIONSTR        char[]
//   CAN_PARAM_AUTOBUSON         int    1 = Automatic BusON after BusOFF
//
// Possible errors: NODRIVER ILLPARAMTYPE ILLPARAMVAL

TCANStatus __stdcall CAN_GetDriverParam(
        WORD  wParam,
        void* pBuff,
        WORD  wBuffLen) ;


//=============================================================================
// Attention: the following functions are only for internal use

//-----------------------------------------------------------------------------
// CAN_RegisterMemory() - Allocates a Non-paged Memory block
// CAN_GetMemory()      - Converts a Memory handle into a pointer
// CAN_RemoveMemory()   - Releases a Memory block
//
// Possible errors: NODRIVER RESOURCE

TCANStatus __stdcall CAN_RegisterMemory(
        DWORD dwSize,
        DWORD dwFlags,
        HCANMEM *hMem);

TCANStatus __stdcall CAN_GetMemory(
        HCANMEM hMem,
        PVOID *memptr);

TCANStatus __stdcall CAN_RemoveMemory(HCANMEM hMem);


//-----------------------------------------------------------------------------
// CAN_InternRead()  - Read data from the driver
// CAN_InternWrite() - Write data into the driver
//
// Possible errors: NODRIVER ILLFUNCTION

TCANStatus __stdcall CAN_InternRead(
        DWORD      function,
        HCANOBJECT hObject,
        BYTE       *buffer,
        DWORD      buffersize,
        DWORD      *bytesreturned);

TCANStatus __stdcall CAN_InternWrite(
        DWORD      function,
        HCANOBJECT hObject,
        BYTE       *buffer,
        DWORD      buffersize);


//-----------------------------------------------------------------------------
// CAN_InternIoctl()  - Read data from the driver

TCANStatus __stdcall CAN_InternIoctl(
        DWORD function,
        HCANOBJECT hObject,
        BYTE *inbuffer,
        DWORD inbuffersize,
        BYTE *outbuffer,
        DWORD outbuffersize,
        DWORD *bytesreturned);

#ifdef __cplusplus
}
#endif

#endif // __CANAPI2H__