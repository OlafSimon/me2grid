# -*- coding: utf-8 (ü) -*-
"""CANOpen Network Module

This module holds objects to represents a CANOpen network. 
A CANOpen network requires a CAN interface for communication
(e.q.:class:`canpy.interfaces.CanInterface`).

Example
-------
A CANOpen network can be initialized by::

    from canpy.canopen import CanOpenNetwork
    from canpy.interfaces.pcan import PCanInterface

    Can = PCanInterface()
    CanOpen = CanOpenNetwork(Can, reset=True)
    
Object entries can be written and read via::

    result = CanOpen.writeSDO(1, 0x1000, 0, 1) 
    result, value = CanOpen.readSDO(1, 0x1000, 0)
   

Note
----
    The length of the Object Entries will be probed by the module and then saved for future access.
    If the probing causes problems, the length can be explicitly set by passing the optional `n`
    parameter in read and write SDO methods.
    
"""

_all_ = ['COB', 'NMT_Command', 'Result', 'CanOpenMsg', 'uCanMsg', 'CanOpenNetwork']

try:
    from .HAL.pyCanPort import pyCanPort, stCanMsg
except:
    from BibPy.HAL.pyCanPort import pyCanPort, stCanMsg
from enum import IntEnum
from ctypes import Structure, Union, c_ubyte, c_ushort, c_ulong
import time
import sys

class COB(IntEnum):
    """ Communication Object Identifier
    This enumeration holds the values associated with communication objects in the CAN Identifier.
    """
    NMT          = 0x000
    SYNC         = 0x080
    TIMESTAMP    = 0x100
    EMERGENCY    = 0x080
    TPDO1        = 0x180
    RPDO1        = 0x200
    TPDO2        = 0x280
    RPDO2        = 0x300
    TPDO3        = 0x380
    RPDO3        = 0x400
    TPDO4        = 0x480
    RPDO4        = 0x500
    TSDO         = 0x580
    RSDO         = 0x600
    RTR          = 0x700
    
class NMT_Command(IntEnum):
    """ Network Management Commands
    This enumeration holds the values associated with network management commands.
    """
    Start              = 0x01
    Stop               = 0x02
    PreOperational     = 0x80
    Reset              = 0x81
    ResetCommunication = 0x82
    
class Result(IntEnum):
    """ CANOpen Result Identifier
    This enumeration holds the values associated with communication results.
    """
    OK                  = 0x00000000
    TimeOut             = 0xFFFF00FF  # Unspecified
    UnsupportedAccess   = 0x06010000
    ReadOnWriteOnly     = 0x06010001
    WriteOnReadOnly     = 0x06010002
    ObjectNonExist      = 0x06020000
    ObjectNotMappabl    = 0x06040041
    HWError             = 0x06060000
    NonExistingSubIndex = 0x06090011
    DataLenMissMatch    = 0x06070010
    DataLenToHigh       = 0x06070012
    DataLenToLow        = 0x06070013
    WriteFailure        = 0x08000020
    ProtocolFailure     = 0x08000000


class CanOpenMsg (Structure):
    """ CANOpen SDO Message
    Represents a CANOpen service data object message as a ctypes structure
    """
    _pack_ = 1
    _fields_ = [ ("ID",         c_ulong),          # 11/29-bit message identifier
                 ("MSGTYPE",    c_ubyte),          # Type of the message
                 ("LEN",        c_ubyte),          # Data Length Code of the message (0..8)
                 ("COMMAND",    c_ubyte),          # Command Specifier
                 ("INDEX",      c_ushort),         # INDEX
                 ("SUBINDEX",   c_ubyte),          # SUBINDEX
                 ("DATA",       c_ulong) ]         # Data of the message (DATA[0]..DATA[3])
                 
class uCanMsg(Union):
    """ Union of CANOpen Message and CAN SDO Message
    Allows to access a message as both CAN Message (RAW) and service data object (SDO)
    """
    _fields_ = [("RAW", stCanMsg),
                ("SDO", CanOpenMsg)]

class stCallbackInfo():
  NODEID = 0
  CALLBACK = None
  
  def __init__(self, **args):
    self.NODEID = args['NODEID']
    self.CALLBACK = args['CALLBACK']
  
class pyCANopen:
    """Representation of a CANOpen Network.
    
    This object represents a CANOpen network with an associated CAN interface. It provides basic
    functions to send and receive SDO and NMT messages. 
    
    Parameters
    ----------
    CanInterface: :class:`canpy.interfaces.CanInterface`
        The CANOpen interface used for communication
    timeout:
        The timeout before a SDO request raises a timeout exception
    verbosity:
        Used for debugging to print details in case of unexpected behaviour
    reset:
        Set to True if nodes should be reset during initialisation
    """
    def __init__(self, CanPort=None, timeout=200e-3, verbosity=0, reset=False, callback=True):
        if CanPort==None:
          print('Info : CanOpenNetwork: __init__: No CAN port defined. No message exchange will happen.')
          CanPort = pyCanPort()
            
        self.CanInterface = CanPort
        self.callback = callback
        self.receiveMsg = None
        self.receiveMsgValid = False
        self.receiveMsgExpectedId = None
        if self.callback:
            self.CanInterface.ifCanReceive.append(self.__onCanReceive__)
        self.timeout = timeout
        self.verbosity = verbosity
        
        self.msg =  uCanMsg()
        self.msg.SDO.LEN = 8 #Fix for CAN SDO
        
        self.__DTDict = {}   # Dict for DataTypes (length)
        self.ifTPDO1 = []
        
        #Set Can Nodes global to operational
        self.sendNMT(0,NMT_Command.Start)
        
        if reset:
            self.sendNMT(0,NMT_Command.Reset)
        
    def __onCanReceive__(self, can):
        msg = self.CanInterface.receive()
        if not msg: return
        # print ("CANopen Can receive")
        cob = COB(msg.ID & 0x780)
        addr = msg.ID & 0x7F
        if self.receiveMsgExpectedId and not self.receiveMsgValid:
          if msg.ID == self.receiveMsgExpectedId:
            # print("received expected")
            self.receiveMsg = msg
            self.receiveMsgValid = True
        if cob==COB.TPDO1:
          for f in self.ifTPDO1:
            if addr==f.NODEID and f.CALLBACK:
              f.CALLBACK(msg.DATA)
              
    def __setExpectedResponseId__(self, id):
        self.receiveMsgExpectedId = id
        self.receiveMsgValid = False
        
    def __receive__(self):
        if self.callback:
          self.CanInterface.operate()
          if self.receiveMsgValid:
            msg = self.receiveMsg
            self.receiveMsgExpectedId = None
            self.receiveMsgValid = 0
            return msg
          else:
            return None
        else:
          return self.CanInterface.receive()
                
    def flushQueue(self):
        """ Flush all pending messages on the CAN Network """
        self.CanInterface.flush()
            
    def sendNMT(self, nodeID, command):
        """ Send a Network Management Command """
        msg = stCanMsg()
        msg.ID = COB.NMT
        msg.DATA[0] = command.value
        msg.DATA[1] = nodeID
        msg.LEN = 2
        
        self.flushQueue()
        self.CanInterface.send(msg)
            
        return Result.OK
    
    def sendRPDO1(self, nodeID, data):
      msg=stCanMsg()
      msg.ID=COB.RPDO1 + nodeID
      msg.LEN=len(data)
      for i in range(msg.LEN):
        msg.DATA[i]=data[i]
      self.CanInterface.send(msg)
        
    def writeSDO(self, nodeID, index, subindex, value, n=None, attempts=1, verbosity=None, timeout=None):
        """ Write a SDO object in the CANOpen network
        
        Parameters
        ----------
        nodeID: int
            The nodeID of the device to access
        index : int
            The index of the object entry
        subindex: int
            The subindex of the object entry
        value:
            The value to be written to the object entry
        n: int (optional)
            The length in bytes of the object entry. If none it will be probed
            and saved for the future
        attempts: int (optional)
            Retries before generating an error
        verbosity: int (optional)
            Override verbosity level for this request
        timeout: float (optional)
            Override timeout for this request
    """
        if type(value) == bytes:
            value = int.from_bytes(value, byteorder='little')
        if type(value) == str:
            value =int.from_bytes(bytes(value, encoding='utf-8'), byteorder='little')
            
        if timeout == None:
          timeout = self.timeout
          
        if verbosity == None:
          verbosity = self.verbosity
          
        if n == None:
            try:
                n = self.__DTDict[nodeID, index, subindex]
            except:
                n = 1
        
        # assert n<=4, "DataLen to High"
        if n>4:
          n=4
        
        self.msg.SDO.ID = COB.RSDO.value + nodeID
        self.msg.SDO.COMMAND  = 0x23 | ((4-n) << 2) # 0x20 | e | s
        self.msg.SDO.INDEX    = index
        self.msg.SDO.SUBINDEX = subindex
        self.msg.SDO.DATA     = value
        
        self.flushQueue()
        self.__setExpectedResponseId__(COB.TSDO.value + nodeID)
        # print("writeSDO")
        self.CanInterface.send(self.msg.RAW)
        start_time = time.time()
        while True:
            #error, msg, timestamp = self.CanInterface.read()
            msg = self.__receive__()
            if msg:
              sdo = uCanMsg(msg).SDO
              if (sdo.ID == COB.TSDO.value + nodeID
                  and sdo.INDEX == index and sdo.SUBINDEX == subindex):
                      break
                
            if time.time() - start_time > timeout:
                if (attempts == 1):
                    if verbosity >=1:
                        print('Error: Could not write SDO [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (nodeID, index, subindex), file=sys.stderr)
                    return Result.TimeOut
                else:
                    if verbosity >=2:
                        print('Warning: Reattempting to write SDO [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (nodeID, index, subindex), file=sys.stderr)
                    return self.writeSDO(nodeID, index, subindex, value, n, attempts-1, verbosity, timeout)
        
        msg = uCanMsg(msg)
        
        # Check for Abort Message
        if msg.SDO.COMMAND == 0x80:
            result = Result(msg.SDO.DATA)
            if (result == Result.DataLenToHigh or result == Result.DataLenToLow or result == Result.DataLenMissMatch):
                if result == Result.DataLenToHigh:
                    m = n-1
                else:
                    m = n+1
                
                if verbosity >=2:
                    print('Warning: Reattempting to write SDO. Changeing the data length from %d to %d Bytes [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (n, m, nodeID, index, subindex), file=sys.stderr)
                res = self.writeSDO(nodeID, index, subindex, value, m, attempts, verbosity, timeout)
                self.__DTDict[nodeID, index, subindex] = m
                return res
            
            
            print('Error: SDO Request returned %s : 0x%x' % (result, result), file=sys.stderr)
            return result
            
        
        if msg.SDO.COMMAND != 0x60:
            
            raise NotImplementedError("Unexpected Return Code [%s]" % result)
            
        return Result.OK
        
    def readSequentialSDO(self, nodeID, index, subindex=0, verbosity=None, timeout=None):
        data = bytes()
        t = 0
        EOT = False
        while not EOT:
            self.msg.SDO.COMMAND = 0x60 | (t<<4)
            self.__setExpectedResponseId__(COB.TSDO.value + nodeID)
            # print("readSeqSDO")
            self.CanInterface.send(self.msg.RAW)
            start_time = time.time()
            while True:
                #error, msg, timestamp = self.CanInterface.receive()
                msg = self.__receive__()
                if msg:
                  sdo = uCanMsg(msg).SDO
                  if (sdo.ID == COB.TSDO.value + nodeID):
                      break
                    
                if time.time() - start_time > timeout:
                    print('Error: Could not read sequential SDO [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (nodeID, index, subindex), file=sys.stderr)
                    return Result.TimeOut, 0

            msg = uCanMsg(msg)
            
            # Check for Abort Message
            if msg.SDO.COMMAND == 0x80:
                result = Result(msg.SDO.DATA)
                if verbosity >=1:
                    print('Error: SDO Request returned %s : 0x%x' % (result, result), file=sys.stderr)
                return result, 0 
            
            n = 8-((msg.SDO.COMMAND & 0x0F) >> 1)
            data += bytes(msg.RAW.DATA[1:n])

            if msg.SDO.COMMAND & 1:
                EOT = True
            t ^= 1
        return Result.OK, data
  
        
    def readSDO(self, nodeID, index, subindex=0, attempts=3, verbosity=None, timeout=None):
    
        if timeout == None:
            timeout = self.timeout
          
        if verbosity == None:
            verbosity = self.verbosity
          
        self.msg.SDO.ID = COB.RSDO.value + nodeID
        self.msg.SDO.COMMAND  = 0x40
        self.msg.SDO.INDEX    = index
        self.msg.SDO.SUBINDEX = subindex
        
        self.__setExpectedResponseId__(COB.TSDO.value + nodeID)
        self.flushQueue()
        # print("readSDO")
        self.CanInterface.send(self.msg.RAW)
        
        start_time = time.time()
        while True:
            #error, msg, timestamp = self.CanInterface.read()
            msg = self.__receive__()
            if msg:
              sdo = uCanMsg(msg).SDO
              if (sdo.ID == COB.TSDO.value + nodeID
                  and sdo.INDEX == index and sdo.SUBINDEX == subindex):
                      break
                
            if time.time() - start_time > timeout:
                if (attempts == 1):
                    if verbosity >=1:
                      print('Error: Could not read SDO [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (nodeID, index, subindex), file=sys.stderr)
                    return Result.TimeOut, 0
                else:
                    if verbosity >=2:
                      print('Warning: Reattempting to read SDO [NodeID: %d | Index: 0x%x | Subindex: 0x%x]' % (nodeID, index, subindex), file=sys.stderr)
                    return self.readSDO(nodeID, index, subindex, attempts-1, verbosity)
                    
        msg = uCanMsg(msg)
        
        # Check for Abort Message
        if msg.SDO.COMMAND == 0x80:
            result = Result(msg.SDO.DATA)
            if verbosity >=1:
                print('Error: SDO Request returned %s : 0x%x' % (result, result), file=sys.stderr)
            return result, 0
            
        
        n = (msg.SDO.COMMAND & 0x0C) >> 2
        e = (msg.SDO.COMMAND & 0x02) >> 1
        s = (msg.SDO.COMMAND & 0x01)
        
        l = 4-n # Length of used Bytes
        
        if e != 1:
            return self.readSequentialSDO(nodeID, index, subindex, verbosity, timeout)
            #raise NotImplementedError("Only Expedited Transfer implemented: %s" % (msg.SDO.COMMAND))
            
        if s != 1:
            raise NotImplementedError("Unindicated transfer size not implemented")
        
        # Mask Value
        value = msg.SDO.DATA & ((1 << (8*l)) -1)
        return Result.OK, value
       
