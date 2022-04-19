# -*- coding: utf-8 (ü)-*-
"""
The pyEcatDrive object describes a drive using the EhterCAT SBusPlus protocol to be controlled.
This class uses parameter access, only.
"""


try:
    from pyDrive import pyDrive
except:
    from BibPy.pyDrive import pyDrive

from enum import Enum, IntEnum
    

_all_ = ['pyEcatDrive']


class enOperationMode(Enum):
  NONE = -1
  VELOCITY = 0
  POSITIONING = 1

  
class enFCB(IntEnum):
  DISABLE = 1
  REFERENCE = 12
  VELOCITY = 5
  POSITIONING = 9
  

class pyEcatDrive(pyDrive):

    def __init__(self, ecatMaster, address: int = 0):
        self.ecat = ecatMaster
        self.address = address
        self.node = self.ecat.slaves[address]
        self.identString = self.node.sdo_read(0x1008, 0).decode()
        self.operationMode = enOperationMode.NONE
        self.deltaVelocity = 1
        self.deltaPosition = 0.01
        print("Info : pyEcatDrive.__init__: Found drive %s" % self.identString)
        # Steuerwortquelle auf 'lokaler Wert' setzen
        self.node.sdo_write(8373, 2, (0).to_bytes(4, byteorder = 'little'))
        # Sollwertquelle Drehzahl auf 'lokaler Wert' setzen
        self.node.sdo_write(8376, 11, (0).to_bytes(4, byteorder = 'little'))
        # PA-Daten aktualisieren auf 'aus'
        value = int.from_bytes(self.node.sdo_read(8367, 1), byteorder = 'little')
        self.node.sdo_write(8367, 1, (value & 0xFFFE).to_bytes(4, byteorder = 'little'))
        # Grundeinstellung Quelle auf 'lokaler Wert' setzen
        self.node.sdo_write(8366, 4, (0).to_bytes(4, byteorder = 'little'))
        # Steuerbit Vorschubfreigabe 'aus'
        value = int.from_bytes(self.node.sdo_read(8509, 2), byteorder = 'little')
        self.node.sdo_write(8509, 2, (value & 0xFFFE).to_bytes(4, byteorder = 'little'))

    def enableOperation(self):
        """ Usually enables the power electronics operation """
        if self.operationMode == enOperationMode.VELOCITY:
          # Im Steuerwort den FCB 05 (Drehzahlregelung) setzen
          self.node.sdo_write(8373, 3, enFCB.VELOCITY.to_bytes(4, byteorder = 'little'))
        elif self.operationMode == enOperationMode.POSITIONING:
          # Im Steuerwort den FCB 09 (Positionsregelung) setzen
          self.node.sdo_write(8373, 3, enFCB.POSITIONING.to_bytes(4, byteorder = 'little'))
                   
    def disableOperation(self):
        """ Usually enables the power electronics operation """
        self.node.sdo_write(8373, 3, enFCB.DISABLE.to_bytes(4, byteorder = 'little'))
        
    def setModeVelocity(self, enable: bool = True, speed = 0):
        """ old: switchtoVeloMode """
        self.operationMode = enOperationMode.VELOCITY
        # Start und Stopp Drehzahlsollwert (Minimaldrehzahl) auf 0 setzen
        self.node.sdo_write(8570, 2, (0).to_bytes(4, byteorder = 'little'))
        self.node.sdo_write(8570, 3, (0).to_bytes(4, byteorder = 'little'))
        self.setVelocity(speed)
        if enable:
          self.enableOperation()
        
    def setVelocity(self, velocity, wait=True):
        """
        Sets the velocity command value to the specified value (Standard unit is rev/second).
        In case of positioning mode the maximum speed is set to plus minus the specified value
        """
        # Festsollwert (lokal) / 1/min
        self.node.sdo_write(8376, 12, velocity.to_bytes(4, byteorder = "little", signed = True))

    def setModePositioning(self, enable: bool = True, position: int = 0, position: int = None, referencePosition: int = None):
        """ old: switchtoPositionMode """
        self.operationMode = enOperationMode.POSITIONING
        if referencePosition != None:
        	self.setPositionReference(referencePosition)
        if position != None:
        	self.setPosition(position)
        else
          self.setPosition(self.getPosition())
        if enable:
          self.enableOperation()
      
    def setPositionReference(self, positionValue = 0):
        """ sets the current position to the value of positionValue (Standard unit is revolutions)"""
        self.node.sdo_write(8373, 3, enFCB.DISABLE.to_bytes(4, byteorder = 'little'))
        self.node.sdo_write(8373, 3, enFCB.VELOCITY.to_bytes(4, byteorder = 'little'))
        self.node.sdo_write(8373, 3, enFCB.DISABLE.to_bytes(4, byteorder = 'little'))

    def setPosition(self, position, wait=True):
        """ Instructs the drive to move to a new position (Standard unit is revolutions)."""
        pos = int(position*100)
        self.node.sdo_write(8376, 2, pos.to_bytes(4, byteorder = 'little'))
        
    def setAcceleration(self, a):
        """ Standard unit is rev/second^2 """
        pass

    def getVelocity(self):
        """ Standard unit is rev/second """
        return int.from_bytes(self.node.sdo_read(8364, 47), byteorder = 'little') / 10000

    def getTargetVelocity(self):
        """ Standard unit is rev/second """
        return int.from_bytes(self.node.sdo_read(8376, 12), byteorder = 'little')

    def isVelocity(self) -> bool:
        """ Returns if the command velocity has been reached """
        return abs(self.getTargetVelocity()-self.getVelocity()) <= self.deltaVelocity

    def getPosition(self):
        """ Standard unit is revolitions """
        pos = int.from_bytes(self.node.sdo_read(8364, 25), byteorder = 'little')
        return pos/65536

    def getTargetPosition(self):
        """ Standard unit is revolitions """
        pos = int.from_bytes(self.node.sdo_read(8376, 2), byteorder = 'little')
        return pos/100

    def isInPosition(self) -> bool:
        """ Returns if the command position has been reached """
        return abs(self.getTargetPosition()-self.getPosition()) <= self.deltaPosition
    
    def resetError(self):
        self.node.sdo_write(8365, 5, (1).to_bytes(4, byteorder = 'little'))
    
    def getState(self):
        err = int.from_bytes(self.node.sdo_read(8365, 7), byteorder = 'little')
        ready = int.from_bytes(self.node.sdo_read(8332, 1), byteorder = 'little')
        if (err & 2) != 2:
            return 0
        elif (ready & 1) == 1:
            return 1
 				
    
if __name__ == "__main__":

    from time import sleep
    import pysoem
      

    print('Testing pyEcatDrive')

    adapters = pysoem.find_adapters()
    adapterIndex = 1
    print("Info : main: Connecting EtherCAT to adapter %s" % adapters[1].desc)
    ecat = pysoem.Master()
    ecat.open(adapters[1].name)
    ecat.config_init()

    drive = pyEcatDrive(ecat, 0)

    drive.setModeVelocity()
    print("Info : main: Set positive velicity")
    drive.setVelocity(1200)
    sleep(5)
    if drive.isVelocity():
      print("Info : main: Reached velocity")
    else:
      print("Error: main: Velocity not reached")
    print(abs(drive.getTargetVelocity()-drive.getVelocity()))

    print("Info : main: Set negative velicity")
    drive.setVelocity(-1200)
    sleep(5)
    
    print("Info : main: Set position 0")
    drive.setModePositioning()
    drive.setPosition(0)
    sleep(5)
    print("Info : main: Set position 1.5 revolutions")
    drive.setPosition(1.5)
    sleep(5)
    if drive.isInPosition():
      print("Info : main: Reached Postion")
    else:
      print("Error: main: Position not reached")
    print(abs(drive.getTargetPosition()-drive.getPosition()))
    drive.disableOperation()
    
    ecat.close()

    print("Done")
