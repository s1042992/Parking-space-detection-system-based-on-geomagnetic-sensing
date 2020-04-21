#!/usr/bin/python
#coding=utf-8
import py_qmc5883l
import time
import math
import smbus
pi   = 3.14159265359
#sensor = py_qmc5883l.QMC5883L(output_range = py_qmc5883l.RNG_8G)
#sensor.declination = declination_value

class Compass:
    declination_value = (-4.0 - (18.72 / 60.0)) / (180 / pi)
    #set the magnet declination value in Taiwan in 2020
    def __init__(self):
        sensor = py_qmc5883l.QMC5883L(output_range = py_qmc5883l.RNG_8G)
        sensor.declination = declination_value
    #sense the bearing angle by sensor
    def bearing(self):
        compass_angle = sensor.get_bearing()
        if compass_angle >= 60:
            compass_angle -= 60
        else:
            compass_angle = 365 - (60 - compass_angle)
        #round off to the 3rd decimal place
        compass_angle = round(compass_angle, 3)
    