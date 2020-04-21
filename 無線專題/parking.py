import py_qmc5883l
import time
import math
import smbus
sensor    = py_qmc5883l.QMC5883L(output_range = py_qmc5883l.RNG_8G)
flag      = False
flag2     = True
start     = 0
end       = 0
during    = 0
i         = 0
i_store   = 100
small_car = 50
big_car   = 80
x = [0]
y = [0]
z = [0]
while (1):
    x_temp, y_temp, z_temp = sensor.get_magnet_raw()
    x.append(x_temp)
    y.append(y_temp)
    z.append(z_temp)
    print(x[i],y[i],z[i])
    if (flag is False and i > 10):
        if(x[i] - x[i-9] > 120 or y[i-9] - y[i] > 600 and z[i-9] - z[i] > 100):
            start = time.time()
            i_store = i
            print("\033[1;35m start counting \033[0m")
            start = (round(start, 3))
            flag = True;
    elif (flag is True  and i - i_store >= 20):
        if(  abs(y[i] - y[5]) < 120 and abs(z[i] - z[5]) < 120):
            end = time.time()
            end = (round(end, 3))
            break
    if flag is True:
        if(abs(x[i_store] - x[i]) > 1200 or  abs(y[i_store] - y[i]) > 1200 or  abs(z[i_store] - z[i]) > 1200):
            if(flag2 is True):
                print ("\033[1;31m the price has been raised \033[0m")
                flag2 = False
    i += 1
during = round(end - start,3)
if(flag2 is True):
    price = round(small_car * during, 1)
else:
    price = round(big_car * during, 1)
print("\033[1;35m You have stopped for \033[0m", during, "\033[1;35m second \033[0m")
print("\033[1;35m Your parking fee is \033[0m",price)



