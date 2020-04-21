import py_qmc5883l
import time
import math
import smbus

sensor = py_qmc5883l.QMC5883L(output_range = py_qmc5883l.RNG_8G)
while (1):
	print(sensor.get_magnet_raw())
	