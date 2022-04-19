"""!
@file  smarthome.py
@brief Library for the interaction of smart home devices

@section Description

This Library provides objects to communication to smart home devices such as sensors and actuators as well as
more complex machines. It is part of the me2grid open source project. Library objects care for communication to devices, organizing devices to groups and
manage device to device communication.

@section Requirements

- bleak

Installation and usage is described at https://bleak.readthedocs.io/en/latest/installation.html

Hints for further programming:
text = "{'00:00': 17, '06:00': 23, '10:00': 17, '14:30': 27, '18:00': 17}"
import ast
temp_dict = ast.literal_eval(text)
print (temp_dict)

"""

class device():
    def __init__(self):
        pass

    def set(self, param, value):
        pass
    
    def get(self, param, value):
        pass
