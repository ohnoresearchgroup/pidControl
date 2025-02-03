# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:25:39 2025

Need to install LabJackPython with:
    pip install LabJackPython


@author: peo0005
"""

import u6

class LabJackPID():
    
    def __init__(self):        
        #open the first LabJack U3 connected
        self.lj = u6.U6()
        
    def readVoltage(self,channel):
        voltage = self.lj.getAIN(channel)
        print(voltage)
