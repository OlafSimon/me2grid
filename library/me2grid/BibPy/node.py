# -*- coding: utf-8 (ü) -*-
"""CANopen Nodes Module

This module holds the functions that are generic to all CANopen devices.
A CANopen node requires a CANopen interface (e.q. :class:`pcanpy.CANOpen`).

Example
-------
A CANopen node can be initialized by::

    from canpy.canopen import CanOpen
    from canpy.devices import CanOpenNode
    
    CAN = CanOpen()
    CANnode = CanOpenNode(CAN, nodeID=1)
    
Object entries can be written and read via::

    CANnode.writeParam(0x4000,0, value=10)
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
    from .canopen import pyCANopen, NMT_Command, Result
except:
   from canopen import pyCANopen, NMT_Command, Result        
from enum import IntEnum
import time
    
__all__ = ['CanOpenNode']

class ObjGeneric(IntEnum):
    """ This enum holds the index value of genric object entrys
    """
    DeviceType    = 0x1000
    ErrorRegister = 0x1001
    RestoreParams = 0x1011
    TxPDO         = 0x1800

class CanOpenNode():
    """Representation of a CANopen node.
    
    Parameters
    ----------
    CONetwork: :class:`CanOpenNetwork`
        The CANOpen interface used for communication
    NodeID:
        The devices node ID [0..255]
    """
    def __init__(self, CANopen:pyCANopen, NodeID:int):
        self.net = CANopen
        self.NodeID = NodeID
        self.Obj = ObjGeneric
        self.online = False
        
    def readParam(self, index, subindex=0):
        """Reads a node object entry.
        
        Parameters
        ----------
        index : int
            The index of the object entry
        subindex : int
            The subindex of the object entry

        Returns
        -------
        int
            The value of the object entry
        """
        res,val = self.net.readSDO(self.NodeID, index,subindex)
        res
        assert res==Result.OK, "Error reading Node ID %d, Index 0x%x, SubIndex 0x%x:  %s" \
                                % (self.NodeID, index, subindex, res)
        return val
    
    def writeParam(self, index, subindex, value, n=None):
        """Writes a node object.
        
        Parameters
        ----------
        index : int
            The index of the object entry
        subindex : int
            The subindex of the object entry
        value : int
            The value to be written
        n : int, optional
            The size in bytes of the object entry. If omitted it will be
            auto-detected and remembered
        """
        res = self.net.writeSDO(self.NodeID, index, subindex, value, n)
        #assert res==Result.OK, "Error writing Node ID %d, Index 0x%x, SubIndex 0x%x:  %s" \
        #                % (self.NodeID, index, subindex, res)
        if res!=Result.OK:
          print("Error writing Node ID %d, Index 0x%x, SubIndex 0x%x:  %s" \
                        % (self.NodeID, index, subindex, res))
                        
    def resetParams(self, kind='all'): 
        """Resets parameters to factory settings.
        
        Parameters
        ----------
        kind: str
            all, communication, application, user, movement, tuning
        """
        if kind == 'all':
            subindex = 1
        elif kind == 'communication':
            subindex = 2
        elif kind == 'application':
            subindex = 3
        elif kind == 'user':
            subindex = 4
        elif kind == 'movement':
            subindex = 5
        elif kind == 'tuning':
            subindex = 6
        else:
            raise ValueError('kind not understood')
        
        self.writeParam(self.Obj.RestoreParams, subindex, 0x64616F6C)
        self.waitforStartUp()
    
    def startNode(self):
        """Sends the NTM Command to start the node."""
        self.net.sendNMT(self.NodeID, NMT_Command.Start)
        self.waitforStartUp()
        
    def stopNode(self):
        """Sends the NTM Command to stop the node."""
        self.net.sendNMT(self.NodeID, NMT_Command.Stop)
        
    def resetNode(self):
        """Sends the NTM Command to reset the node."""
        self.net.sendNMT(self.NodeID, NMT_Command.Reset)
        self.waitforStartUp()
        
    def checkfor(self, index, subindex, bitmask=None, timeout=0.5, verbosity=0):
        """This function checks object entries for conditions.
        
        The specified object entry is read until one of the following conditions
        are met:
        
            - A timeout occures after the time specified in `timeout`
            - The object entries value matches the `bitmask`
            - The first response if `bitmask` is set to None

        A negative timeout value disables the timeout check
        
        Parameters
        ----------
            index : int
                The index of the object entry
            subindex : int
                The subindex of the object entry
            bitmask : int, optional
                The bitmask to match against
            timeout : int, optional
                The time in sec after which a timeout is generated
            verbosity : int, optional
                The level of verbosity if >0 prints the time needed to return
                
        Returns
        -------
            bool
                `True` on success and `False` in case of timeout.
        """
        start_time = time.time()
        while True:
            res,val = self.net.readSDO(self.NodeID, index, subindex, verbosity=0)

            if res == Result.OK:
                if not bitmask:
                    break
                if (bitmask & val)==bitmask:
                    (bitmask & val)==bitmask 
                    break

            if (timeout >=0) and (time.time() - start_time) > timeout:
                return False
        
        if verbosity > 0:
            print('Device responded after %5.3fs with %x' % (time.time() - start_time, val))
        return True
    
    def waitforStartUp(self,timeout=0.5):
        """ Waits for the device to respond to SDO requests by checking for COB device type
        """
        assert self.checkfor(self.Obj.DeviceType, 0, timeout=timeout)==True, "Error Node %d not responding. Please check the connection and NodeID" % self.NodeID
        
    def disableTPOs(self):
        """ Disables the transmission of PDOs. Can help to prevent BusOverload.
        """
        for i in range(3):
            self.writeParam(self.Obj.TxPDO + i,1,0)
            
