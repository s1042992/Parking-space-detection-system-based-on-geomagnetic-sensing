#!/usr/bin/python
#coding=utf-8
import time
import math

class Car:
    #set the initial value of car's coordinate of x & y, and car's speed
	def __init__(self,x_coordinate = 0.0, y_coordinate = 0.0, v_speed = 0.0):
		self.x_coordinate = x_coordinate
		self.y_coordinate = y_coordinate
		self.v_speed = v_speed
    #return the car's position    
    def get_position(self):
        return x_coordinate, y_coordinate
    
        
        