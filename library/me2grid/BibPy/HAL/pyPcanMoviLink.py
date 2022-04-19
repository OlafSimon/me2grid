# -*- coding: utf-8 (ü) -*-
"""
Created on Mon Nov 23 16:13:38 2020

@author: DESIMOLA
"""

import sys, os
from sys import stderr
from enum import IntEnum, IntFlag
import ctypes, ctypes.util
from ctypes import CFUNCTYPE
import threading

try:
    from .pyCanPort import pyCanPort, stCanMsg
except:
  from pyCanPort import pyCanPort, stCanMsg
    
from time import sleep

_all_ = ['pyPCan', 'pyMoviLink']

class ResultCode(IntEnum):
  OK                  = 0x00000000
  Pending             = -1
  NotSended           = -2
  Invalid             = -3
  FalseACK            = 100
  NoPort              = 101
  GenericError        = 253
  NotImplemented      = 254
  Timeout             = 255

class c_stCanMsg(ctypes.Structure):
  _fields_ = [
    ('ID',    ctypes.c_short),
    ('Len',   ctypes.c_short),
    ('Data', (ctypes.c_ubyte * 8)),
    ('RTR',   ctypes.c_ubyte) ]

class PCAN_ERROR(IntFlag):
    OK            = int(0x00000)  # No error 
    XMTFULL       = int(0x00001)  # Transmit buffer in CAN controller is full
    OVERRUN       = int(0x00002)  # CAN controller was read too late
    BUSLIGHT      = int(0x00004)  # Bus error: an error counter reached the 'light' limit
    BUSHEAVY      = int(0x00008)  # Bus error: an error counter reached the 'heavy' limit
    BUSOFF        = int(0x00010)  # Bus error: the CAN controller is in bus-off state
    ANYBUSERR     = int(BUSLIGHT | BUSHEAVY | BUSOFF) # Mask for all bus errors
    QRCVEMPTY     = int(0x00020)  # Receive queue is empty
    QOVERRUN      = int(0x00040)  # Receive queue was read too late
    QXMTFULL      = int(0x00080)  # Transmit queue is full
    REGTEST       = int(0x00100)  # Test of the CAN controller hardware registers failed (no hardware found)
    NODRIVER      = int(0x00200)  # Driver not loaded
    HWINUSE       = int(0x00400)  # Hardware already in use by a Net
    NETINUSE      = int(0x00800)  # A Client is already connected to the Net
    ILLHW         = int(0x01400)  # Hardware handle is invalid
    ILLNET        = int(0x01800)  # Net handle is invalid
    ILLCLIENT     = int(0x01C00)  # Client handle is invalid
    CLIENTREMOVED = int(0x01C20)  # Client handle is invalid
    ILLHANDLE     = int(ILLHW | ILLNET | ILLCLIENT) # Mask for all handle errors
    RESOURCE      = int(0x02000)  # Resource (FIFO, Client, timeout) cannot be created
    ILLPARAMTYPE  = int(0x04000)  # Invalid parameter
    ILLPARAMVAL   = int(0x08000)  # Invalid parameter value
    UNKNOWN       = int(0x10000)  # Unknow error
    ILLDATA       = int(0x20000)  # Invalid data, function, or action
    INITIALIZEOLD = int(0x40000)  # Channel is not initialized (has changed)
    ILLOPERATION  = int(0x80000)  # Invalid operation
    INITIALIZE    = int(0x4000000)# Channel is not initialized
    # Application defined additional error codes
    BUFFEROVERRUN = int(0x001A1)  # Receive buffer of pyPcanMoviLink instance is full. Probaply messages have not been polled fast enough or at all.

libraryName = "PcanMoviLink"
VarDataLen=234
timeoutTime=200
retrys=0
canBufferSize=1024
openCount=0
canInstance=None
busy=False
lastPcanError=PCAN_ERROR.OK

cML = None
MsgBuffer=[]
msgBufferLock = threading.Lock()
canEnabled = False

def onCanReceive(cpMsg):
  """ called by an independent thread running within the library on reception of a CAN message
  """
  global MsgBuffer
  global msgBufferLock
  global busy
  global lastPcanError
  
  if busy:
    print("Error: pyPcanMoviLink.onCanReceive: Callback overrun")
  else:
    busy = True
    
  cMsg = cpMsg.contents
  Msg = stCanMsg()
  Msg.ID = cMsg.ID
  Msg.LEN = cMsg.Len
  for i in range(8):
    Msg.DATA[i] = cMsg.Data[i]
  msgBufferLock.acquire()
  # print(len(MsgBuffer))
  if len(MsgBuffer)<canBufferSize:
    MsgBuffer.append(Msg)
    if  lastPcanError == PCAN_ERROR.BUFFEROVERRUN:
      lastPcanError=PCAN_ERROR.OK
      print("Info : pyPcanMoviLink.onCanReceive: Message buffer free after overrun")
  else:
    if PCAN_ERROR.BUFFEROVERRUN != lastPcanError:
      lastPcanError=PCAN_ERROR.BUFFEROVERRUN
      print("Error: pyPcanMoviLink.onCanReceive: Message lost due to message buffer overrun", file=sys.stderr)
  msgBufferLock.release()
  
  # if canInstance:
  #   if canInstance.interruptControl:
  #     canInstance.runCallbacks()
  busy = False
  return
  
def onCanError(ErrorCode):
  """ called by an independent thread running within the library on reception of a CAN message
  """
  global lastPcanError
  
  if PCAN_ERROR(int(ErrorCode))!=lastPcanError:
    lastPcanError=PCAN_ERROR(int(ErrorCode))
    if PCAN_ERROR(int(ErrorCode)) != PCAN_ERROR.OK and PCAN_ERROR(int(ErrorCode)) != PCAN_ERROR.CLIENTREMOVED:
      print("Error: pyPcanMoviLink.onCanError: Can error " + str(PCAN_ERROR(int(ErrorCode))), file=sys.stderr)
    else:
      # print("Info : pyPcanMoviLink.onCanError: Can state" + str(PCAN_ERROR(int(ErrorCode))))
      pass
  return
  
def loadLibrary():
  global cML
  # global c_OnCanReceive
  global timeoutTime
  global openCount
  
  if not openCount:
    mylib=None
    path = ""
    errString = ""
    if not mylib:
      mylib = ctypes.util.find_library(libraryName)
      if mylib:
        try:
          cML = ctypes.CDLL(mylib)
        except OSError as e:
          errString += "Fatal: pyPcanMoviLink.loadLibrary: Failed to load library from current or system path: " + path + libraryName + " - " + str(e) 
          mylib = None
    if not mylib:
      path = "BibPy/HAL/" 
      mylib = ctypes.util.find_library(path + libraryName)
      if mylib:
        try:
          cML = ctypes.CDLL(mylib)
        except OSError as e:
         errString += "Fatal: pyPcanMoviLink.loadLibrary: Failed to load library from BibPy in current path: " + path + libraryName + " - " + str(e)
         mylib = None
    if not mylib:
      path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
      mylib = ctypes.util.find_library(path + libraryName)
      if mylib:
        try:
          cML = ctypes.CDLL(mylib)
        except OSError as e:
          errString += "Fatal: pyPcanMoviLink.loadLibrary: Failed to load library with full path: " + path + libraryName + " - " + str(e)
          mylib = None
    if not mylib:
      if errString!="":
        print(errString, file=stderr)
      else:
        print("Fatal: pyPcanMoviLink.loadLibrary: Unable to find library: " + libraryName + " in ., BibPy/HAL and " + path, file=stderr)
      print("Windows: Copy PcanMoviLink.dll and 'PCAN_USB' foulder to the directory of pyPcanMoviLink.py", file=stderr)
      print("Linux:   Copy libPcanMoviLink.so to /usr/lib and run 'sudo ldconfig'", file=stderr)
      sys.exit()

    # print("Info : pyPcanMoviLink.loadLibrary: Loaded library " + path + libraryName)
    cML.initLib.restype = None
    cML.initLib.argtypes = [ctypes.c_int]
    cML.destroyLib.restype = None
    cML.destroyLib.argtypes = None

    typeOnCanReceive = CFUNCTYPE(None,ctypes.POINTER(c_stCanMsg))
    c_OnCanReceive = typeOnCanReceive(onCanReceive)
    typeOnCanError = CFUNCTYPE(None, ctypes.c_int)
    c_OnCanError = typeOnCanError(onCanError)
    cML.defCallbacks.artypes = [c_OnCanReceive, c_OnCanError]
    cML.defCallbacks(c_OnCanReceive, c_OnCanError)
  openCount += 1
  
class pyPCan(pyCanPort):
  def __init__(self, interruptControl = False, enable=True):
    global cML
    global onCanReceive
    global onCanError
    global canInstance
    global canEnable
    canEnable = enable
    loadLibrary()
    cML.initLib(timeoutTime)
    cML.canSend.restype  = ctypes.c_int
    cML.canSend.argtypes = [ctypes.POINTER(c_stCanMsg), ctypes.c_int]
    cML.canReceive.restype  = ctypes.c_int
    cML.canReceive.argtypes = [ctypes.POINTER(c_stCanMsg), ctypes.c_int]
    self.cML = cML                      # necessary to keep object alive until self instance is deleted
    self.onCanReceive = onCanReceive    # necessary to keep object alive until self instance is deleted
    self.onCanError = onCanError        # necessary to keep object alive until self instance is deleted
    self.ifCanReceive = []              # list of regisered call-back functions
    self.interruptControl = interruptControl
    if not canInstance:
      canInstance=self
    else:
      print("Fatal: pyPcanMoviLink.pyPCan.__init__: Creation of a second instance is not allowed", file=stderr)
      sys.exit()
    
  def enable(self, on:bool=True):
    global canEnable
    canEnable=on

  def close(self):
    global openCount
    global canInstance
    canInstance = None
    cML.destroyLib()
    openCount -= 1
    return

  def __del__(self):
    global openCount
    if openCount:
      print("Fatal: pyPcanMoviLink.pyPCan.__del__: Instance of pyPCan or pyMoviLink has not been cosed at end of program", file=stderr)
    return

  def receive(self, Wait=0):
    global MsgBuffer
    global msgBufferLock
    ret=None
    msgBufferLock.acquire()
    if len(MsgBuffer):
      if len(self.ifCanReceive):
        ret = MsgBuffer[0]
      else:
        ret = MsgBuffer.pop(0)
    else:
      ret = None
    msgBufferLock.release()
    return ret

  def send(self, Msg, delay_ms=0, retrys=3):
    cMsg = c_stCanMsg()
    cMsg.ID = Msg.ID
    cMsg.Len = Msg.LEN
    for i in range (Msg.LEN):
      cMsg.Data[i] = Msg.DATA[i]
    res = self.cML.canSend(cMsg, 1)
    return res

  def operate(self):
    if not self.interruptControl:
      self.runCallbacks()
    return 
 
  def runCallbacks(self):
    global MsgBuffer
    global msgBufferLock
    if len(self.ifCanReceive):
      msgBufferLock.acquire()
      while len(MsgBuffer):
        msgBufferLock.release()
        for cb in self.ifCanReceive:
          cb(self)
        msgBufferLock.acquire()
        MsgBuffer.pop(0)
      msgBufferLock.release()
    return 
      
  def flush(self):
    global MsgBuffer
    global msgBufferLock
    msgBufferLock.acquire()
    while len(MsgBuffer)>1: # keep last message to avoid trouble with multi thread operation
      MsgBuffer.pop(0)
    msgBufferLock.release()
    return  
      
class pyMoviLink():
  def __init__(self):
    global cML
    global onCanReceive
    global onCanError
    loadLibrary()
    cML.initLib(timeoutTime)
    cML.readParameter.restype  = ctypes.c_int
    cML.readParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_long)]
    cML.writeParameter.restype = ctypes.c_int
    cML.writeParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
    cML.sendVardata.restype    = ctypes.c_int
    cML.sendVardata.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_int]
    self.__DataBuffer = ctypes.create_string_buffer(VarDataLen)
    self.cML = cML                   # necessary to keep object alive until self instance is deleted
    self.onCanReceive = onCanReceive # necessary to keep object alive until self instance is deleted
    self.onCanError = onCanError     # necessary to keep object alive until self instance is deleted
      
  def close(self):
    global openCount
    cML.destroyLib()
    openCount -= 1
    return
    
  def __del__(self):
    global openCount
    if openCount:
      print("Fatal: pyMoviLink.pyPCan.__del__: Instance of pyPCan or pyMoviLink has not been cosed at end of program", file=stderr)
    return
  
  def readParam(self, addr=0, index=8301, subindex=0, format='int', n=1):   # Standard index value is the mandatory device type ID
    values = []
        
    for i in range(n):
      for trys in range(retrys+1):
        cvalue = ctypes.c_long(0)
        res = self.cML.readParameter(addr, index, subindex, cvalue)
        value=cvalue.value
        values.append(value)
        if res == ResultCode.OK:
          # values.append(value)
          break
      else:
        print("Error: pyMoviLink.readParam: Parameter could not be read: Addr:%d, Index:%d, SubIndex:%d -> %s"%(addr,index,subindex,res), file=stderr)
        # raise IOError('Parameter could not be read: Addr:%d, Index:%d, SubIndex:%d -> %s'%(addr,index,subindex,res))
                  
    if format=='int':
      if n==1:
        val = values[0]
      else:
        val = values
          
    elif format=='str':
      values = list(map(lambda x: x.to_bytes(4, 'little').decode('latin-1').replace("\00",""), values))
      val = str.join('', values)
    else:
      raise ValueError("format must be 'int' or 'str'")
            
    return val

  def writeParam(self, addr, index, subindex, val):
      """ This function writes a Movilink parameter with exception handling
      Args:
        addr      (int): Node address 
        index     (int): Parmater index
        subindex  (int): Parameter subindex
        val       (int,str): Parameter value
        
      Returns:
        Nothing
      """
      if type(val) == str:
          txt = val.encode('latin-1')
          if len(txt)>4:
              raise ValueError("Only 4 chars per parameter")
              
          val = int.from_bytes(txt, byteorder='little')
      elif not type(int):
          raise ValueError("Value must be string or 4-Char")
      
      for trys in range(retrys+1):
        res = self.cML.writeParameter(addr, index, subindex, val)
        if res == ResultCode.OK:
          break
      else:
        print('Error: pyMoviLink.writeParam: Parameter could not be written: Addr:%d, Index:%d, SubIndex:%d -> %s' % (addr,index,subindex,res), file=stderr)
        # raise IOError('Parameter could not be written: Addr:%d, Index:%d, SubIndex:%d -> %s' % (addr,index,subindex,res))
      
# if __name__ == "__main__":
#   print('Testing pyPcanMoviLink')
#   print('Movi-Link:')
#   ML = pyMoviLink()
#   print('Reading device type (parameter: 8301.0) at address 1')
#   try:
#     Value = ML.readParam(1, 8301, 0)
#     print("Reading result: " + str(Value))
#   except IOError as e:
#     Value = 0
#     print("Reading failed: " + str(e))    
#   print("Can")
#   Msg = stCanMsg()
#   Msg.ID=0x1
#   Msg.LEN=1
#   Msg.DATA[0]=0x4
#   Can=pyPCan()
#   print("Send ID: " + str(Msg.ID))
#   Can.send(Msg)
#   print("Receiving can messages for 10 s")
#   print("Received messages will be shown afterwards, ID 524 will be received due to previous Movi-Link request!")
#   sleep(10)
#   Msg=Can.receive()
#   while Msg:
#     print("Received can message ID " + str(Msg.ID))
#     Msg=Can.receive()
#   ML.close()
#   Can.close()
#   print("Done")

if __name__ == "__main__":
  def onMainCanReceive(can):
    msg = can.receive()
    print("Received can message ID " + str(msg.ID))
    
  print('Testing pyPcan by operate()')
  can=pyPCan()
  can.ifCanReceive.append(onMainCanReceive)
  ml = pyMoviLink()

  msg = stCanMsg()
  msg.ID=0x1
  msg.LEN=1
  msg.DATA[0]=0x4
  print("Send ID: " + str(msg.ID))
  can.send(msg)
  print("Receiving can messages for 10 s")
  for i in range(0,100):
    sleep(0.01)
    #msg = can.receive()
    #if msg:
    #  print("Received can message ID " + str(msg.ID))
    can.operate()

  print('Reading device type (parameter: 8301.0) at address 1')
  for i in range(200):
    try:
      Value = 0
      Value = ml.readParam(1, 8301, 0)
      print("Reading result: " + str(Value))
    except IOError as e:
      Value = 0
      print("Reading failed: " + str(e))    
  # sleep(1) 
  ml.close()
  can.close()
  print("Done")
  
