import binascii
from me2grid.smarthome import EQ3_CC_RT_BLE_EQ


#scanner = BleScanner()
#scanner.scan()    

valve = EQ3_CC_RT_BLE_EQ("00:1A:22:12:0F:87")

print("Writing, Wait 5 s ...")
result = None # valve.getTargetTemperature()
#result = valve.request(charUUID_ReadWriteResponse, charUUID_ReadWriteRequest, b'\x41\x1d')
#result = valve.getManufacturer()
#print("Answer:", binascii.hexlify(result))
print("Answer:", result)

list = {'00:00': 17, '06:00': 23, '10:00': 17, '14:30': 27, '18:00': 17}

text = "{'00:00': 17, '06:00': 23, '10:00': 17, '14:30': 27, '18:00': 17}"
text2 = text[1:len(text)-1]
l = text2.split(',')

import ast
res = ast.literal_eval(text)
print res

print("Ready")
