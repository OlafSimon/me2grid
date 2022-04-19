from ctypes import Structure, c_ulong, c_ubyte

_all_ = ['pyCanPort', 'stCanMsg']

class stCanMsg (Structure):
    """ Represents a CAN message
    
    A CAN message consists of an identifier which can be 11/29-bit long and appended data.
    The identifier is also used as a priority based bus arbitration. For the underlying
    implementations a field for the message length and the message type (e.g. 11/29-bit ID) are
    reserved
    """
    _fields_ = [ ("ID",      c_ulong),          # 11/29-bit message identifier
                 ("MSGTYPE", c_ubyte),          # Type of the message
                 ("LEN",     c_ubyte),          # Data Length Code of the message (0..8)
                 ("DATA",    c_ubyte * 8) ]     # Data of the message (DATA[0]..DATA[7])
    
    def __str__(self):
        txt = "stCanMsg: ID=" + str(self.ID) +" Len=" + str(self.LEN)
        for i in range(self.LEN):
            txt += " " + str(self.DATA[i])
        return txt

class pyCanPort:
    """This Module holds the base class for a CanInterface
    
    This class should be the blueprint for underlying implementations. In principal only three
    methods for reading, writing and flushing messages are required to be exposed to top modules
    """
    def receive(self):
        """Read a message from the CAN bus"""
        pass

    def send(self, Msg, delay_ms=0, retrys=3):
        """Write a message to the CAN bus""" 
        pass
        
    def flush(self):
        """Write a message to the CAN bus""" 
        pass