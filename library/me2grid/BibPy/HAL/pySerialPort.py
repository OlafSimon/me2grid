# This Python file uses the following encoding: utf-8

import os
import xml.etree.ElementTree as et
from BibPy.pyXmlParameterFile import pyXmlParameterFile
from BibPy.pyXmlFile import Xml

from serial import Serial, EIGHTBITS, PARITY_ODD, PARITY_EVEN, PARITY_MARK, PARITY_SPACE, PARITY_NONE, STOPBITS_ONE
from serial.tools.list_ports import comports


class pySerialPort(Serial):
    def __init__(self, port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None, name="Port0"):
        super().__init__(port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout, exclusive)
        self.name = name
        self.parameterFile = None

        ports = comports()
        # If 'port' exists, 'port' will be used.
        checkPort = False
        for p in ports:
            if p.device == port:
                checkPort = True
                break
        if checkPort:
            print("Info : SerialPort.__init__: Using port %s from constructor" % port)
            return
        # Use config xml-file even if xml-element is used later
        xmlFileName = os.path.join(os.path.dirname(__file__), "pySerialPort.xml")
        self.parameterFile = pyXmlParameterFile(xmlFileName, "pySerialPort")
        self.parameterFile.read()
        dict = self.configDict()
        configDict={}
        foundConfigFile=True
        configDict['port'] = self.parameterFile.getParameter('port', 'noConfigFile')
        if configDict['port'] == 'noConfigFile':
          foundConfigFile=False
          configDict['port'] = None
        configDict['baudrate'] = self.parameterFile.getParameter('baudrate', self.baudrate)
        configDict['bytesize'] = self.parameterFile.getParameter('bytesize', self.bytesize)
        configDict['stopbits'] = self.parameterFile.getParameter('stopbits', self.stopbits)
        configDict['parity'] = self.parameterFile.getParameter('party', dict['parity'])
        configDict['flow'] = self.parameterFile.getParameter('flow', dict['flow'])
        configDict['waitTimeout'] = self.parameterFile.getParameter('waitTimeout', dict['waitTimeout'])
        configDict['frameTimeout'] = self.parameterFile.getParameter('frameTimeout', dict['frameTimeout'])
        self.openByDict(configDict, False)

        checkPort = False
        for p in ports:
            if p.device == self.port:
                checkPort = True
                break
        if checkPort:
            print("Info : SerialPort.__init__: Using port %s from configuration (./BibPy/HAL/pySerialPort.xml or xml-element)" % self.port)
            # self.saveConfig()
            self.open()
            # super().__init__(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout, self.xonxoff, self.rtscts, self.write_timeout, self.dsrdtr, self.inter_byte_timeout, self.exclusive)
            self.parameterFile.setParameter("port", self.port)
            self.parameterFile.write()
            return
        elif self.port is None and foundConfigFile:
            print("Info : SerialPort.__init__: No port is used according to the configuration (./BibPy/HAL/pySerialPort.xml or xml-element)")
            self.parameterFile.setParameter("port", self.port)
            self.parameterFile.write()
            return
        else:
            print("Info : SerialPort.__init__: Port from configuration (./BibPy/HAL/pySerialPort.xml or xml-element) not available on this computer")

        # If no configuration is available, check if the computer has only one serial port
        if len(ports) == 1:
            print("Info : SerialPort.__init__: Single port %s on computer used" % ports[0].device)
            self.port = ports[0].device
            # self.saveConfig()
            super().__init__(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, self.timeout, self.xonxoff, self.rtscts, self.write_timeout, self.dsrdtr, self.inter_byte_timeout, self.exclusive)
            self.parameterFile.setParameter("port", self.port)
            self.parameterFile.write()
            return
        if len(ports) == 0:
            print("Info : SerialPort.__init__: No serial port present on this computer")
            self.parameterFile.setParameter("port", self.port)
            self.parameterFile.write()
            return
        # No ports are available or it is uncertain which of several ports shall be used. Don't open any port
        print("Info : SerialPort.__init__: No port opened as no port is configured and several ports are available on this computer")
        self.parameterFile.setParameter("port", self.port)
        self.parameterFile.write()
        return

    def configDict(self) -> {}:
        params = {}
        params['port'] = self.port
        params['baudrate'] = self.baudrate
        params['bytesize'] = self.bytesize
        if self.parity == PARITY_EVEN:
            params['parity'] = 'Even'
        elif self.parity == PARITY_ODD:
            params['parity'] = 'Odd'
        elif self.parity == PARITY_MARK:
            params['parity'] = 'Mark'
        elif self.parity == PARITY_SPACE:
            params['parity'] = 'Space'
        else:
            params['parity'] = 'None'
        params['stopbits'] = self.stopbits
        params['flow'] = 'None'
        if self.xonxoff:
            params['flow'] = 'XON/XOFF'
        elif self.rtscts:
            params['flow'] = 'RTS/CTS'
        elif self.dsrdtr:
            params['flow'] = 'DSR/DTR'
        params['frameTimeout'] = self.inter_byte_timeout
        params['waitTimeout'] = self.timeout
        return params

    def openByDict(self, params: {}, open = True):
        try:
            self.port = params['port']
        except:
            pass
        try:
            self.baudrate = params['baudrate']
        except:
            pass
        try:
            self.bytesize = params['bytesize']
        except:
            pass
        if params['parity'] == 'Even':
            self.parity = PARITY_EVEN
        elif params['parity'] == 'Odd':
            self.parity = PARITY_ODD
        elif params['parity'] == 'Mark':
            self.parity = PARITY_MARK
        elif params['parity'] == 'Space':
            self.parity = PARITY_SPACE
        else:
            self.parity = PARITY_NONE
        try:
            self.stopbits = params['stopbits']
        except:
            pass
        try:
            if params['flow'] == 'XON/XOFF':
                self.xonxoff = True
            else:
                self.xonxoff = False
            if params['flow'] == 'RTS/CTS':
                self.rtscts = True
            else:
                self.rtscts = False
            if params['flow'] == 'DSR/DTR':
                self.dsrdtr = True
            else:
                self.dsrdtr = False
        except:
            pass
        try:
            self.inter_byte_timeout = params['frameTimeout']
        except:
            pass
        try:
            self.timeout = params['waitTimeout']
        except:
            pass
        self.close()
        if self.port is not None and open:
            self.open()

    def saveConfig(self):
        # if self.port is not None:
        #     self.parameterFile.setParameter('port', self.port)
        # else:
        #     self.parameterFile.setParameter('port', "none")
        # self.parameterFile.setParameter('port', self.port)
        for key, value in self.configDict().items():
             self.parameterFile.setParameter(key, value)
        self.parameterFile.write()

    def configFromElements(self, elementList: []):
        configElement = pyXmlFile.findElementByName(elementList, self.name)
        if configElement!=None:
            self.openByDict(configElement.attrib)
        else:
            print("Info : pySerialPort.configFromElements: name=%s: No matching configuration element found, using default values" % self.name)

    def subElement(self, rootElement) -> Xml.Element:
       elem = Xml.SubElement(rootElement, "pySerialPort")
       dict = self.configDict()
       dict["Name"] = self.name
       elem.attrib = dict

if __name__ == "__main__":
    print('Testing pySerialPort')
    port = pySerialPort()
    print(port)
    port.close()

