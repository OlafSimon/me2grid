# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 18:29:21 2021

@author: DESIMOLA
"""

_all_ = ['pyRealTime']

from time import time

'''
/**
 * \brief Liefert Echtzeitwerte der aktuellen Zeit ( Uhr / real time clock) als float-Wert in Sekunden
 * Der Wertebereich für Zeitpunkte liegt zwischen 0 und einem Tag (0x05265C00 ms).
 * Die Verarbeitung erfolgt nach Uhrzeit (nicht nach Programmlaufzeit)!
**/
'''
class pyRealTime:
  
  def getTime():
    return time()

  def addTime(timeA, timeB):
    return timeA + timeB

  def diffTime(timeA, timeB):
    return timeA-timeB

  def getAheadTime(deltaTime):
    return pyRealTime.addTime( pyRealTime.getTime(), deltaTime )

  def deltaTime(refTime):
    return pyRealTime.diffTime( pyRealTime.getTime(), refTime )
    
  def timePassed(refTime):
    return pyRealTime.deltaTime(refTime)>=0
    
  def timeElapsed(refTime, deltaTime):
    return pyRealTime.deltaTime(refTime) >= deltaTime
