# -*- coding: utf-8 (ü)-*-
"""
The pyDrive object describes a virtual interface to control drives at all kind of different busses and networks
by very generic command methods
"""

_all_ = ['pyDrive']

class pyDrive:
    """
    Generic interface for controlling drives independently of their bus or network interface and actual command structure
    """

    def __init__(self):
        pass

    def enableOperation(self):
        """ Usually enables the power electronics operation """
        pass

    def disableOperation(self):
        """ Usually enables the power electronics operation """
        pass
        
    def setModeVelocity(self, enable: bool = True, speed = 0):
        """ speed in rev/second """
        pass
        
    def setVelocity(self, velocity, wait=True):
        """
        Sets the velocity command value to the specified value (Standard unit is rev/second).
        In case of positioning mode the maximum speed is set to plus minus the specified value
        """
        pass

    def setModePositioning(self, enable: bool = True, position: int = None, referencePosition: int = None):
        """ position in revolutions"""
        pass

    def setPositionReference(self, positionValue = 0):
        """ sets the current position to the value of positionValue (unit is revolutions)"""
        pass

    def setPosition(self, position, wait=True):
        """ Instructs the drive to move to a new position (Standard unit is revolutions)."""
        pass
        
    def setAcceleration(self, a):
        """ Standard unit is rev/second^2 """
        pass

    def getVelocity(self):
        """ Standard unit is rev/second """
        return 0

    def isVelocity(self) -> bool:
        """ Returns if the command velocity has been reached """
        return False

    def getPosition(self):
        """ Standard unit is revolitions """
        return

    def getTargetPosition(self):
        """ Standard unit is revolitions """
        return
        
    def moveForward(self,revolutions):
        pass

    def isInPosition(self) -> bool:
        """ Returns if the command position has been reached """
        return False

    def resetError(self):
				pass
				
    def moveForward(self, deltaRevolutions):
        move=self.getTargetPosition()
        self.setPosition(move+deltaRevolutions, True)
      
