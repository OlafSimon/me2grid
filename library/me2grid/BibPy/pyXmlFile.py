import sys
import xml.etree.ElementTree as Xml

class pyXmlFile:
    def __init__(self, fileName: str = "pyXmlFile.xml", rootName: str = "pyXmlFile"):
        self.fileName = fileName
        self.setRootName = rootName
    
    def read(self) -> Xml.Element:
        xmlRoot = None
        try:
            xmlFile = open(self.fileName)
        except IOError:
            print("Info : pyXmlFile.read: %s could not be opened" % self.fileName)
            pass
        else:
            try:
                xmlDocument = Xml.parse(xmlFile)
            except Xml.ParseError:
                print("Error: pyXmlFile.read: Parsing file %s failed" % self.fileName, file=sys.stderr)
                pass
            else:
                xmlRoot = xmlDocument.getroot()
        return xmlRoot

    def write(self, element: Xml.Element):
        try:
          xmlFile = open(self.fileName, "wb")
        except IOError as e:
          print("Error: xmlParameterFile.write: The parameter xml-file could not be written: " + str(e), file=sys.stderr)
        else:
          xmlFile.write(Xml.tostring(element))
          xmlFile.close()

    def findElementByName(elementList: [], instanceName: str) -> Xml.Element:   
       config = None; 
       for elem in elementList:
           if elem.get("Name") == instanceName:
               config = elem
               break
       return config

if __name__ == "__main__":
    class MyObject:
       def __init__(self, name: str):
            self.name = name
            self.data = 0

       def configFromElements(self, elementList: []):
           configElement = pyXmlFile.findElementByName(elementList, self.name)
           if configElement!=None:
               parameterContent = configElement.get("Data")
               if parameterContent!=None:
                  self.data = int(parameterContent)
               else:
                   print("Info : MyObject.configFromElements: name=%s, parameter %s not found, using default value" % (self.name, "Data"))
           else:
               print("Info : MyObject.configFromElements: name=%s: No matching configuration element found, using default values" % self.name)

       def subElement(self, rootElement) -> Xml.Element:
          elem = Xml.SubElement(rootElement, "MyObject")
          elem.set("Name", self.name)
          elem.set("Data", str(self.data))

    ob1 = MyObject("ob1")
    ob2 = MyObject("ob2")
    configFile = pyXmlFile()
    
    
    def createFile():
        rootElement = Xml.Element("MyApplication")
        myObjectsElements = Xml.SubElement(rootElement, "MyObjects")
        ob1.subElement(myObjectsElements)    
        ob2.subElement(myObjectsElements)    
        configFile.write(rootElement)

    def configureFromFile():
        rootElement = configFile.read()
        myObjectsElement = rootElement.find("MyObjects")
        ob1.configFromElements(myObjectsElement)
        ob2.configFromElements(myObjectsElement)

    print('Testing xml files')
    ob1.data = 10
    ob2.data = 11
    # createFile()
    configureFromFile()
    print("ob1.data = %s" % ob1.data)
    print("ob2.data = %s" % ob2.data)
    
