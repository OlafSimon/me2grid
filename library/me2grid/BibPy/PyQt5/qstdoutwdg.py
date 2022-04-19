# -*- coding: utf-8 -*-

#from PySide2 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTextEdit
import sys

class StdoutSignal(QObject):
  signal = pyqtSignal(str)
  
class QStdoutWdg(QTextEdit):
  def __init__(self, parent=None):
    super(QTextEdit, self).__init__(parent)
    self.newOutputSignal = StdoutSignal()
    self.newOutputSignal.signal.connect(self.onNewOutput)
    sys.stdout=self
    
  def write(self, text):
    if text!="\n":
      self.newOutputSignal.signal.emit(str(text))
    
  def flush(self):
    return

  def onNewOutput(self, text):
    self.append(text)
    
  def __destroy__(self):
    sys.stdout=sys.__stdout__
        