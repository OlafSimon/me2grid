# -*- coding: utf-8 (ü)-*-
"""
The pyMoviLinkDrive object describes a drive using the Movi Link protocol to be controlled
"""

try:
    from pyDrive import pyDrive
    from HAL.pyPcanMoviLink import pyPCan, pyMoviLink, pyCanPort
except:
    from BibPy.pyDrive import pyDrive
    from BibPy.HAL.pyPcanMoviLink import pyPCan, pyMoviLink, pyCanPort

_all_ = ['pyMoviLinkDrive']

class pyMoviLinkDrive(pyDrive):
    """
    Generic interface for controlling drives independently of their bus or network interface and actual command structure
    """

    def __init__(self, moviLink: pyMoviLink, mlAddress: int = 0):
        self.moviLink=moviLink
        self.address=mlAddress

    def enableOperation(self):
        """ Usually enables the power electronics operation """
        # pass
        # DR 05.05.2021
        controlWord = self.moviLink.readParam(self.address,11484,0)
        self.moviLink.writeParam(self.address,11484,0,controlWord & (~0x40000000)) #Reglersperre wieder aus

    def disableOperation(self):
        """ Usually enables the power electronics operation """
        #'pass
        # DR 05.05.2021
        controlWord = self.moviLink.readParam(self.address,11484,0)
        self.moviLink.writeParam(self.address,11484,0,controlWord | 0x40000000) #ControlWord Reglersperre
        
    def setModeVelocity(self, enable: bool = True, speed = 0):
        """ old: switchtoVeloMode """
        if self.moviLink.readParam(self.address,8335,0) == 2:
            self.moviLink.writeParam(self.address,8335,0,0)
        if self.moviLink.readParam(self.address,8336,0) == 3:
            self.moviLink.writeParam(self.address,8336,0,0)
        if self.moviLink.readParam(self.address,8337,0) == 1:
            self.moviLink.writeParam(self.address,8337,0,0)
        if self.moviLink.readParam(self.address,8338,0) == 4:
            self.moviLink.writeParam(self.address,8338,0,0)
        if self.moviLink.readParam(self.address,8339,0) == 5:
            self.moviLink.writeParam(self.address,8339,0,0)

        controlWord = self.moviLink.readParam(self.address,11484,0)
        self.moviLink.writeParam(self.address,11484,0,controlWord | 0x40000000) #ControlWord Reglersperre
        self.moviLink.writeParam(self.address,8574,0,16) #Betriebsart Servo
        self.moviLink.writeParam(self.address,11484,0,(controlWord & (~0x40000000))  | 0x14) #Reglersperre wieder aus, Drehrichtung rechts, Drehzahlvorgabe n11
        self.setVelocity(speed)
        
    def setVelocity(self, velocity, wait=True):
        """
        Sets the velocity command value to the specified value (Standard unit is rev/second).
        In case of positioning mode the maximum speed is set to plus minus the specified value
        """
        self.moviLink.writeParam(self.address,8489,0,velocity*1000/60) # n11

    def setModePositioning(self, enable: bool = True, position: int = None, referencePosition: int = None):
        """ old: switchtoPositionMode """
        controlWord = self.moviLink.readParam(self.address,11484,0)
        self.moviLink.writeParam(self.address,11484,0,controlWord | 0x40000000) #ControlWord Reglersperre
        self.moviLink.writeParam(self.address,8574,0,18) #Betriebsart Servo+IPOS
        #14052021 LB
        // self.moviLink.writeParam(self.address,11484,0,controlWord | 0x00040000) # Controlword Bit 18 0->1 (ActPosMot=0)
        // self.moviLink.writeParam(self.address,11484,0,0) # Controlword Bit 18 1->0
        if referencePosition != None:
        	self.setPositionReference(referencePosition)
        if position != None:
        	self.setPosition(position)
        else
          self.setPosition(self.getPosition())
        if enable:
          self.moviLink.writeParam(self.address,11484,0,controlWord & (~0x40000000)) #Reglersperre wieder aus, Drehrichtung rechts, Drehzahlvorgabe n11

    def setPositionReference(self, positionValue = 0):
        """ sets the current position to the value of positionValue (Standard unit is revolutions)"""
        controlWord = self.moviLink.readParam(self.address,11484,0)
        self.moviLink.writeParam(self.address,8626,0,8) # Referenzfahrttyp = aktuelle Position ohne Freigabe (Parameterbaum 903)
        self.moviLink.writeParam(self.address,11484,0,controlWord | 0x00040000) # Controlword Bit 18 0->1 um Referenzfahrt auszuführen (ActPosMot=0)
        self.moviLink.writeParam(self.address,11484,0,controlWord & (~0x00040000)) # Referenzfahrtausführung zurücksetzen

    def setPosition(self, position, wait=True):
        """ Instructs the drive to move to a new position (Standard unit is revolutions)."""
        self.moviLink.writeParam(self.address,11492,0,position)
        
    def setAcceleration(self, a):
        """ Standard unit is rev/second^2 """
        pass

    def getVelocity(self):
        """ Standard unit is rev/second """
        return (self.moviLink.readParam(self.address,8318,0)/1000*60)

    def isVelocity(self) -> bool:
        """ Returns if the command velocity has been reached """
        return False

    def getPosition(self):
        """ Standard unit is revolitions """
        return self.moviLink.readParam(self.address,11511,0) / 4096
        
    def getTargetPosition(self):
        """ Standard unit is revolitions """
        return self.moviLink.readParam(self.address,11492,0) / 4096

    def isInPosition(self) -> bool:
        """ Returns if the command position has been reached
        		Tolerance defined in parameter "Positionsfenster" 8635, 0 (incements)
        """
        statusWord = self.moviLink.readParam(self.address,11473,0)
        return (statusWord & 0x00080000) == 0x00080000
          
    def resetError(self):
      controlWord = self.moviLink.readParam(self.address,11484,0)
      self.moviLink.writeParam(self.address,11484,0,controlWord | 0x00001000)
      self.moviLink.writeParam(self.address,11484,0,controlWord & (~0x00001000))
      
    def getState(self):
      statusWord = self.moviLink.readParam(self.address,11473,0)
      if (statusWord & 0x00000002) != 0x00000002:
        return 0
      elif (statusWord & 0x00000006)==0x00000006:
        return 1
    
if __name__ == "__main__":

    from time import sleep
      

    print('Testing MoviLinkDrive')

    can = pyPCan()
    moviLink = pyMoviLink()
  
    drive = pyMoviLinkDrive(moviLink, 4)

    drive.setModeVelocity()
    drive.setVelocity(1200)
    sleep(5)
    drive.setVelocity(-1200)
    sleep(5)
    drive.setModePositioning(True)
    sleep(5)
    drive.moveForward(30000)

    moviLink.close()
    can.close()
    
      
    print("Done")
