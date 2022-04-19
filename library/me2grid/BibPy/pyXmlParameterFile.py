import os
import xml.etree.ElementTree as et

class pyXmlParameterFile:
  def __init__(self, fileName, appName = "application"):
    self.fileName = fileName
    self.appName = appName
    self.readDict = {}
    self.refDict = {}
    
  def write(self, force: bool = False):
    if not force and self.readDict == self.refDict:
      return
    data = et.Element(self.appName)
    params = et.SubElement(data, 'parameters')
    for k, v in self.refDict.items():
      param = et.SubElement(params, 'parameter')
      param.set(k,str(v))
    try:
      xmlFile = open(self.fileName, "wb")
    except IOError as e:
      print("Error: xmlParameterFile.write: The parameter xml-file could not be written: " + str(e))
    else:
      xmlFile.write(et.tostring(data))
      xmlFile.close()

  def read(self) -> {}:
    xmlDocument = None
    try:
      xmlFile = open(self.fileName)
    except IOError:
      print("Info : xmlParameterFile.read: Parameter file %s not found: Using standard parameter values" % self.fileName)
    else:
      try:
        xmlDocument = et.parse(xmlFile)
      except et.ParseError:
        print("Info : xmlParameterFile.read: Invalid format in %s file : Using standard parameter values" % self.fileName)
      else:  
        xmlRoot = xmlDocument.getroot()
        parameterList = xmlRoot.find('parameters')
        if parameterList:
          for elem in parameterList:
            self.readDict.update(elem.attrib)
        xmlFile.close()
      return self.readDict

  def getParameter(self, parameterName: str, parameterValue = None):
    try:
      result = eval(self.readDict[parameterName])
    except:
      result = parameterValue
    self.refDict.update({parameterName: str(result)})
    return result

  def setParameter(self, parameterName: str, parameterValue = None, write: bool = True):
    if isinstance(parameterValue, str):
        parameterValue = "'" + parameterValue + "'"
    self.refDict.update({parameterName: str(parameterValue)})
    if write:
      self.write()
    return parameterValue
    
    
if __name__ == "__main__":

  print('Testing xml parameter files')
  
  xmlFileName = os.path.join(os.path.dirname(__file__), "pyXmlParameterFile.xml")
  parameterFile = pyXmlParameterFile(xmlFileName)
  parameterFile.read()
  
  print('File content:')
  print(parameterFile.readDict)

  param1 = parameterFile.getParameter('param1', 5)
  param2 = parameterFile.getParameter('param2', 13)
  parameterFile.write()
  
  print('Program reference content:')
  print(parameterFile.refDict)
  
  param2 = parameterFile.setParameter('param2', 15)
  
  print('Program reference after setting parameter:')
  print(parameterFile.refDict)
  
  print('Program variables:')
  print("param1: %i" % param1)
  print("param2: %i" % param2)
