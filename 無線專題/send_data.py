#!/usr/bin/env python3
import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import LoRaWAN
from LoRaWAN.MHDR import MHDR
import json,datetime

BOARD.setup()
parser = LoRaArgumentParser("LoRaWAN sender")

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
small_car = 5
big_car   = 8
x = [0]
y = [0]
z = [0]

class LoRaWANsend(LoRa):
    def __init__(self, devaddr = [], nwkey = [], appkey = [], verbose = False):
        super(LoRaWANsend, self).__init__(verbose)
        
    def on_tx_done(self):
        print("TxDone\n")
        # 切換到rx
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.set_invert_iq(1)
        self.reset_ptr_rx()
        sleep(1)
        self.set_mode(MODE.RXSINGLE)
        
    def on_rx_done(self):
        global RxDone
        RxDone = any([self.get_irq_flags()[s] for s in ['rx_done']])
        print("RxDone")
        self.clear_irq_flags(RxDone=1)
        
        # 讀取 payload
        payload = self.read_payload(nocheck=True)
        lorawan = LoRaWAN.new(nwskey, appskey)
        lorawan.read(payload)
        print("get mic: ",lorawan.get_mic())
        print("compute mic: ",lorawan.compute_mic())
        print("valid mic: ",lorawan.valid_mic())
        # 檢查mic
        if lorawan.valid_mic():
            print("ACK: ",lorawan.get_mac_payload().get_fhdr().get_fctrl()>>5&0x01)
            print("direction: ",lorawan.get_direction())
            print("devaddr: ",''.join(format(x, '02x') for x in lorawan.get_devaddr()))
            write_config()
        else:
            print("Wrong MIC")
    
    def send(self,theMSG):
        global fCnt
        lorawan = LoRaWAN.new(nwskey, appskey)
        message = theMSG
        # 資料打包,fCnt+1
        lorawan.create(MHDR.CONF_DATA_UP, {'devaddr': devaddr, 'fcnt': fCnt, 'data': list(map(ord, message)) })
        print("fCnt: ",fCnt)
        print("Send Message: ",message)
        fCnt = fCnt+1
        self.write_payload(lorawan.to_raw())
        self.set_mode(MODE.TX)
    
    def time_checking(self):
        global RxDone
        # 檢查是否超時
        TIMEOUT = any([self.get_irq_flags()[s] for s in ['rx_timeout']])
        if TIMEOUT:
            print("TIMEOUT!!")
            write_config()
            sys.exit(0)
        elif RxDone:
            print("SUCCESS!!")
            sys.exit(0)
    
    def start(self,MSG):
        self.send(MSG)
        while True:
            self.time_checking()
            sleep(1)

def binary_array_to_hex(array):
    return ''.join(format(x, '02x') for x in array)

def write_config():
    global devaddr,nwskey,appskey,fCnt
    config = {'devaddr':binary_array_to_hex(devaddr),'nwskey':binary_array_to_hex(nwskey),'appskey':binary_array_to_hex(appskey),'fCnt':fCnt}
    data = json.dumps(config, sort_keys = True, indent = 4, separators=(',', ': '))
    fp = open("config.json","w")
    fp.write(data)
    fp.close()

def read_config():
    global devaddr,nwskey,appskey,fCnt
    config_file = open('config.json')
    parsed_json = json.load(config_file)
    devaddr = list(bytearray.fromhex(parsed_json['devaddr']))
    nwskey = list(bytearray.fromhex(parsed_json['nwskey']))
    appskey = list(bytearray.fromhex(parsed_json['appskey']))
    fCnt = parsed_json['fCnt']
    print("devaddr: ",parsed_json['devaddr'])
    print("nwskey : ",parsed_json['nwskey'])
    print("appskey: ",parsed_json['appskey'],"\n")

# Init
RxDone = False
fCnt = 0
devaddr = []
nwskey = []
appskey = []
read_config()
lora = LoRaWANsend(False)

# Setup
lora.set_mode(MODE.SLEEP)
lora.set_dio_mapping([1,0,0,0,0,0])
lora.set_freq(AS923.FREQ1)
lora.set_spreading_factor(SF.SF7)
lora.set_bw(BW.BW125)
lora.set_pa_config(pa_select=1)
lora.set_pa_config(max_power=0x0F, output_power=0x0E)
lora.set_sync_word(0x34)
lora.set_rx_crc(True)

#print(lora)
assert(lora.get_agc_auto_on() == 1)

try:
    print("Sending LoRaWAN message")
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
    theMessage = "Your parking fee is" + str(price)
    lora.start(message)
except KeyboardInterrupt:
    sys.stdout.flush()
    print("\nKeyboardInterrupt")
finally:
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
    write_config()