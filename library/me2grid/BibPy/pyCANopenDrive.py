# -*- coding: utf-8 (ü)-*-
"""CANopen Device Profiles Implementations for electric drives (CiA 402)

This module implements the CANopen device profile for electric drives. The profile
describes generic manufacturer independent behaviour of electrical drives. 

Example
-------
A CANopen node can be initialized by::

    from sewlab.can import CANOpenDrive
    from pcanpy import CanOpen
    
    CAN = CanOpen()
    drive = CANOpenDrive(CAN, nodeID=1, IncPerTurn=2000)
    
Note
----
By default the drive will automatically be started by sending the appropriate
NTM Command and switch to state :class:`DriveState.SwitchedOn`. This can be changed by setting
autoStart false.

Object entries can be written and read via::

    CANnode.writeParam(0x4000,0, value)
    value = CANnode.readParam(0x1000,0)
   

Note
----
    If multiple devices communicate on the same BUS and the BUS load becomes
    too heavy it might be required to disable TPDOs that are send by default.
    This can be done with::
    
        CANnode.disableTPOs()
    


Attributes
----------


"""
try:
    from .canopen import pyCANopen
    from .pyDrive import pyDrive
    from .node import CanOpenNode, ObjGeneric
except:
    from canopen import pyCANopen
    from pyDrive import pyDrive
    from node import CanOpenNode, ObjGeneric
        
from enum import IntEnum, IntFlag
from itertools import chain


_all_ = ['pyCANopenDrive']

class DriveState(IntFlag):
    """ This enum holds the bit mapping of the drive state.
    """
    ReadyToSwitchOn    = 1<<0
    SwitchedOn         = 1<<1
    OperationEnabled   = 1<<2
    Fault              = 1<<3
    VoltageEnabled     = 1<<4
    QuickStop          = 1<<5
    SwitchOnDisabled   = 1<<6
    Warning            = 1<<7
    Sync               = 1<<8
    Remote             = 1<<9
    TargetReached      = 1<<10
    IntLimitReached    = 1<<11
    ClosedLoopAvailable= 1<<15
    
class DriveMode(IntEnum):
    """ This enum holds the value associated with the drive mode
    """
    NoMode             = 0
    ProfilePosition    = 1
    Velocity           = 2
    ProfileVelocity    = 3
    ProfileTorque      = 4
    Homing             = 6
    
class ObjDrives(IntEnum):
    """ This enum holds the index value of drive object entries
    """
    ControlWord   = 0x6040
    StatusWord    = 0x6041
    OperationMode = 0x6060
    TargetPosition= 0x607A
    RotPolarity   = 0x607E
    ProfileVelo   = 0x6081
    TargetVelocity= 0x60FF

Obj = IntEnum('Obj', [(i.name, i.value) for i in chain(ObjGeneric,ObjDrives)])

class pyCANopenDrive(CanOpenNode, pyDrive):
    """Representation of a CANopen drive.

    The class is derived from :class:`~sewlab.can.CanOpenNode` and represents
    an electrical drive respectively inverter connected to the CANopen Bus.
        
    Parameters
    ----------
    CanInterface: CanOpen Interface
        The CANOpen interface used for communication
    NodeID : int
        The devices node ID [0..255]
    IncPerTurn : int
        Increments equalling one turn
    invertRotation : bool, optional
        Flag used to change the Rotation from CW to CCW
    autoStart : bool, optional
        Flag to chose whether the drive should automatically be switched on
    """
    def __init__(self, CANopen:pyCANopen, NodeID:int, IncPerTurn:int, invertRotation:bool=False, autoStart:bool=True):
        CanOpenNode.__init__(self, CANopen, NodeID)
        pyDrive.__init__(self)

        self.IncPerTurn = IncPerTurn
        
        if autoStart:
          try:
            self.startNode()
            print("Info : CanOpenDrive.init: Drive at CANopen address %i detected" % NodeID)
            self.switchOn()
          except AssertionError as e:
            print(e)
        
        if invertRotation:
            self.writeParam(Obj.RotPolarity, 0, 0b1100_0000, 1)
 
    def switchOff(self):
        """ Writes the required command sequence to power off the device"""
        self.writeParam(Obj.ControlWord,0, DriveState.SwitchOnDisabled)

 
    def switchOn(self):
        """ Writes the required command sequence to power on the device"""
        self.writeParam(Obj.ControlWord,0, 0x00)
        assert self.checkfor(Obj.StatusWord, 0, DriveState.SwitchOnDisabled)
        self.writeParam(Obj.ControlWord, 0, 0x06)
        assert self.checkfor(Obj.StatusWord, 0, DriveState.ReadyToSwitchOn)
        self.writeParam(Obj.ControlWord, 0, 0x07);
        assert self.checkfor(Obj.StatusWord, 0, DriveState.SwitchedOn)
        
    def enableOperation(self):
        """ Sets the drive in the state :class:`DriveState.OperationEnabled`"""
        self.writeParam(Obj.ControlWord,0, 0xF)
        self.checkfor(Obj.StatusWord,0,DriveState.OperationEnabled)

    def disableOperation(self):
        """ Switches back from the state :class:`DriveState.OperationEnabled` to
        :class:`DriveState.SwitchedOn`"""
        self.writeParam(Obj.ControlWord,0, 0x7)
        self.checkfor(Obj.StatusWord,0,DriveState.SwitchedOn)
        
    def getStatus(self):
        """ Returns the StatusWord of the drive as :class:`DriveState`"""
        state   = self.readParam(Obj.StatusWord,0)
        return DriveState(state)
            
    def autoSetup(self):
        """ Performs an autosetup to reference the encoder """
        self.writeParam(Obj.OperationMode,0, 0xFE) # AutoSetup Mode
        
        self.writeParam(Obj.ControlWord,0, 0x0F) # Toggle Bit 4 to start
        self.writeParam(Obj.ControlWord,0, 0x1F)
        
        self.checkfor(Obj.StatusWord,0,0x1400, verbosity=1)
        
    def setModeVelocity(self, enable: bool = True, speed = 0):
        self.disableOperation()
        self.checkfor(Obj.StatusWord,0,DriveState.SwitchedOn)
        self.writeParam(Obj.OperationMode,0, DriveMode.ProfileVelocity)
        self.writeParam(Obj.TargetVelocity,0, 0)   # Velocity
        self.enableOperation()
        
    def setModePosition(self, enable: bool = True):
        """ Switches the drive to Profile Position Mode
        
        Parameters
        ----------
        velocity
            The velocity used in Profile Position Mode in rpm
        """
        self.disableOperation()
        assert self.checkfor(Obj.StatusWord, 0,DriveState.SwitchedOn)
        self.writeParam(Obj.OperationMode, 0, DriveMode.ProfilePosition)
        self.writeParam(Obj.ProfileVelo, 0, velocity) # Position Velocity
        self.writeParam(Obj.TargetPosition,0, 0)        # Position
        self.enableOperation()
        
    def setProfileVelocity(self, velocity):
        """ Sets the velocity used in Profile Position Mode
        
        Parameters
        ----------
        velocity : float
            The velocity in rpm
        """
        assert velocity > 0 
        veloi = int(round(velocity * self.IncPerTurn / 60))
        self.writeParam(Obj.ProfileVelo, 0, veloi) # Position Velocity in Inc/s
        
    def setPosition(self, position, wait=True):
        """ Instructs the drive to move to a new position.
        
        Expects a float representing the position in turns.
        
        Parameters
        ----------
        position : float
            The position in turns of the drive
        velocity : int
            The subindex of the object entry
        """
        if velocity:
            self.setProfileVelocity(velocity)
            
        posi = int(round(position*self.IncPerTurn))
        self.setPosInc(posi, relative, wait)
        
    def setPosInc(self, position, relative=False, wait=True):
        """
        Sets a new drive position relative or absolute.
        Expects the position in increments.
        """
        assert self.checkfor(Obj.StatusWord,0,DriveState.SwitchedOn)
        if self.readParam(Obj.OperationMode,0) != DriveMode.ProfilePosition:
            print('Drive automatically switched to PositionMode')
            self.switchtoPositionMode(100)
            
        relative = (relative != 0)
        self.writeParam(Obj.TargetPosition,0, position)               # Target Pos.
        self.writeParam(Obj.ControlWord,0, 0x0F)
        self.writeParam(Obj.ControlWord,0, 0x3F | (relative << 6)) # New Set-Point
        
        if wait:
            self.checkfor(Obj.StatusWord,0, 1<<10,-1)
            
    def setVelocity(self, velocity):
        assert self.checkfor(Obj.StatusWord,0,DriveState.SwitchedOn)
        if self.readParam(Obj.OperationMode,0) != DriveMode.ProfileVelocity:
            # print('Switching to Velo Mode')
            self.switchtoVeloMode()
        self.writeParam(Obj.TargetVelocity,0, velocity * 60) # Velocity
            
    def getPosition(self):
        """ 
        Returns a tuple where the first element indicates if the axis has come to a stop
        or is still moving. The second element is the position as float.
        """
        
        valid  = self.checkfor(Obj.StatusWord,0, bitmask=DriveState.TargetReached, timeout=0)
        posi   = self.readParam(0x6064,0)
            
        return posi/self.IncPerTurn
        
    def setAcceleration(self, a):
        """ Sets the acceleration in Position and Velocity profile in turns per :math:`sec^2`."""
        a = 32000 if a > 32000 else a
        # Velocity Profile
        try:
            self.writeParam(0x6048,1, self.IncPerTurn*a*10) # Acc
            self.writeParam(0x6048,2, 10) # dT=10
            self.writeParam(0x6049,1, self.IncPerTurn*a*10) # Decel
            self.writeParam(0x6049,2, 10) # dT=10
        except:
            pass
        # Position Profile
        self.writeParam(0x6083,0, a) # Acc
        self.writeParam(0x6084,0, a) # Decel
    
    
    def reference(self, wait=True):
        """ A call to this function starts the homing mode"""
        self.writeParam(Obj.OperationMode,0, 6)    # Homing Mode
        self.writeParam(0x6098,0, 20)   # Homing Mode 20
        self.writeParam(Obj.ControlWord,0, 0x0F) # Stop
        self.writeParam(Obj.ControlWord,0, 0x1F) # Start
        
        # Waiting for Reference Run to finish
        while (wait and not self.referenced()): pass
    
    
    def referenced(self):
        """Returns True if drive has been referenced else False"""
        return self.checkfor(Obj.StatusWord,0, bitmask=1<<12, timeout=0)
    
if __name__ == "__main__": #Dieses Programm muss in einem übergeordneten Ordner gestartet werden!
    print('Testing drive implementing a CANopen protocol using address 1')
    from HAL.pyPcanMoviLink import pyPCan
    Can = pyPCan()
    CANopen = pyCANopen(Can)
    drive = CanOpenDrive(CANopen, 1, 3000)
    drive.switchtoVeloMode()
    drive.setVelocity(1200)
    Can.close()
    print('Ready')
