from .import CanOpenDrive

__all__ = ['NanotechCL3']

class NanotechCL3(CanOpenDrive):
    def __init__(self, CAN, NodeID, ClosedLoop=1):
        CanOpenDrive.__init__(self,CAN,NodeID,2000)
        self.setCurrentLimits(600,400,160)
        self.writeParam(0x3202,0, 1<<3) # Open Loop mit Stromreduzierung
        
        self.switchtoPositionMode(80)
        if ClosedLoop:
            self.setPos(1.1)
            self.writeParam(0x3202,0, 1)    # Closed Loop
            self.setPos(0) 

    def setCurrentLimits(self, peakCurrent, nominalCurrent, idleCurrent):
        """Sets the current limits in mA"""
        self.writeParam(0x2031,0, peakCurrent)
        self.writeParam(0x203B,1, nominalCurrent)
        self.writeParam(0x2037,0, idleCurrent)