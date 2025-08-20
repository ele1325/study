import sys
from time import sleep
import gbl
# import config
# from serdes_script_rate_6g import *
# from serdes_script_pt2_uart import *
from serdes.serdes_script_dp_mode import *
from serdes.serdes_script_colorbar import *
from serdes.serdes_script_checkerboard import *
from serdes.serdes_script_sio_swap import *
from serdes.serdes_script_i2c_clock import *
from serdes.pctool_SHM import AUO_Ft4222

# Pure color is based on checkerboard.
# Thus, init checkerboard is needed before init pure color.

class script_mode:
    rate_6g = 0
    pt2_uart = 1
    dp_mode = 2
    colorbar = 3
    checkerboard = 4
    black = 5
    white = 6
    red = 7
    green = 8
    blue = 9
    red_blue_ck = 10
    tp_disable = 11
    dp_mode_mq = 12
    colorbar_mg = 13
    max = 14

class c_serdes():

    SERDES_ACK = b'\xc3'
    ACK_TIMEOUT = 50   # unit: ms, 需考量pc讀取的速度(pc滿載時，讀取會變慢)
    READ_TIMEOUT = 50  # unit: ms, 需考量pc讀取的速度(pc滿載時，讀取會變慢)  
    LOCK_TIMEOUT = 1000  # ms

    def __init__(self, io=None):
        self.io = io
        self.pt2_6g_init = False
        self.pattern_mode = None

    def __del__(self):
        print('serdes destructor')
        del self

    def ack_check(self):
        ack = bytearray()
        ack_timer = gbl.mclocker()
        while ack != self.SERDES_ACK:
            if (gbl.mclocker() - ack_timer) >= self.ACK_TIMEOUT:
                print("ack timeout")
                return False
            self.io.read(ack, 1)
        return True

    def script_select(self, mode):
        if mode == script_mode.rate_6g:
            return script_rate_6g
        elif mode == script_mode.tp_disable:
            return script_TP_disable
        elif mode == script_mode.pt2_uart:
            return script_pt2_uart
        elif mode == script_mode.dp_mode:
            return script_dp_mode
        elif mode == script_mode.colorbar:
            return script_colorbar
        elif mode == script_mode.checkerboard:
            return script_checkerboard
        elif mode == script_mode.black:
            self.serdes_color_set(script_mode.black)
            return color_control
        elif mode == script_mode.white:
            self.serdes_color_set(script_mode.white)
            return color_control
        elif mode == script_mode.red:
            self.serdes_color_set(script_mode.red)
            return color_control
        elif mode == script_mode.green:
            self.serdes_color_set(script_mode.green)
            return color_control
        elif mode == script_mode.blue:
            self.serdes_color_set(script_mode.blue)
            return color_control
        elif mode == script_mode.red_blue_ck:
            self.serdes_color_set(script_mode.red_blue_ck)
            return color_control
        elif mode == script_mode.dp_mode_mq:
            return script_dp_mode_mq
        elif mode == script_mode.colorbar_mg:
            return script_colorbar_mq

    def serdes_register_get(self, addr: bytearray) -> int:
        reg = (addr[0] << 8) | addr[1]
        return reg

    def serdes_register_check(self, idx: int, reg: int, expect_data: int) -> bool:
        actual_data = self.serdes_register_read(idx, reg)
        if actual_data is not None:
            if expect_data == actual_data:
                return True
            else:
                print(f"idx:{idx:02X}, reg:{reg:04X}, expect: {expect_data:02X}, actual:{actual_data:02X}")
                return False
        else:
            return False

    def script_run(self, script):
        ret = True
        for i in range(len(script)//5):
            arr = bytearray()
            arr[:] = script[i*5: (i+1)*5]
            # print("serdes init(%d): %s" % (i, ' '.join('{:02x}'.format(x) for x in arr)))

            if arr[0] == 0x04:
                self.io.write(arr, len(arr))
                # if (self.ack_check() == False):
                #     print(i, arr)
                #     print('ack fail')
                #     ret = False                
                # reg = self.serdes_register_get(arr[2:4])
                # ret &= self.serdes_register_check(arr[1], reg, arr[5])             
            else:
                sleep_time = (arr[0] << 8 | arr[1]) / 1000
                self.io.updatelog("Sleep: %f Second."%(sleep_time))
                sleep(sleep_time)
        return ret
    
    def serdes_6g_pt2_init(self):
        print("serdes init 6g & pt2 start")
        script = self.script_select(script_mode.rate_6g)
        self.script_run(script)
        lock_timer = gbl.mclocker()
        lock_timeout_flag = 0
        print("wait for lock")
        lock_reg = 0
        while lock_reg != 0x8a:
            lock_reg = self.serdes_register_read(0x80, 0x0013)
            print(lock_reg)
            if (gbl.mclocker() - lock_timer) >= self.LOCK_TIMEOUT:
                lock_timeout_flag = 1
                break
        if lock_timeout_flag == 1:
            print("lock timeout")
        else:
            print("locked")
        script = self.script_select(script_mode.pt2_uart)
        self.script_run(script)
        print("serdes init 6g & pt2 finish")
        self.pt2_6g_init = True

    def serdes_mode_init(self, mode):
        # if self.pt2_6g_init == False:
        #     self.serdes_6g_pt2_init()
        script = self.script_select(mode)
        return self.script_run(script)            

    def serdes_default_init(self, type):
        # self.serdes_6g_pt2_init()
        if (type == 1):
            self.serdes_mode_init(script_mode.dp_mode)
        elif (type == 2):
            self.serdes_mode_init(script_mode.dp_mode_mq)
        
    def serdes_sio_swap(self): 
        self.script_run(script_sio_swap)
        
    def serdes_i2c_clock(self):
        self.script_run(script_i2c_clock)

    def serdes_color_set(self, color):
        color_dict = {
            script_mode.black: [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            script_mode.white: [0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            script_mode.red: [0xff, 0x00, 0x00, 0xff, 0x00, 0x00],
            script_mode.green: [0x00, 0xff, 0x00, 0x00, 0xff, 0x00],
            script_mode.blue: [0x00, 0x00, 0xff, 0x00, 0x00, 0xff],
            script_mode.red_blue_ck: [0xff, 0x00, 0x00, 0x00, 0x00, 0xff],
        }

        for i, value in enumerate(color_dict.get(color, [])):
            color_control[5 + 4 + 5 * i] = value
        # 6: skip "pattern generator disabled"
        # 5: index of color value
        # 6 * i: 6 register for clor
        
    def serdes_register_read(self, idx: int, reg: int) -> int:
        # SYNC, ADDR, MSB , LSB , LEN
        wbuf = bytearray([0x79, 0x00, 0x00, 0x00, 0x01])
        wbuf[1] = idx + 1    # 0x81 = SER, 0x91 = DES
        wbuf[2] = reg >> 8   # reg_H
        wbuf[3] = reg & 0xFF  # reg_L
        # ACK, DATA
        rbuf = bytearray([0, 0])
        self.io.write(wbuf, len(wbuf))
        read_timer = gbl.mclocker()
        while rbuf[0] != 0xC3:
            if (gbl.mclocker() - read_timer) >= self.READ_TIMEOUT:
                print("read timeout")
                break
            self.io.read(rbuf, 2)
            if rbuf == None:
                return None
            #print(f"read reg:{reg:02X} = {rbuf[0]:02X} {rbuf[1]:02X}")
        if len(rbuf) > 1:
            return rbuf[1]
        else:
            return None

####### for socket #########

    # ret皆為str list或是None
    
    pattern_map = {
        'EXT': script_mode.dp_mode,
        'CLB': script_mode.colorbar,
        'CKB': script_mode.checkerboard,
        'D': script_mode.black,
        'W': script_mode.white,
        'R': script_mode.red,
        'G': script_mode.green,
        'B': script_mode.blue,
        'RBC': script_mode.red_blue_ck,
    }

    def patn_set(self, str):
        if str != None:
            if self.pattern_map.get(str) != None:
                if self.serdes_mode_init(self.pattern_map[str]) == True:
                    self.pattern_mode = str
                    ret = [str]
                else:
                    ret = None
            else:
                ret = None
        else:
            ret = None
        return ret
    
    def patn_get(self):
        if self.pattern_mode != None:
            ret = [self.pattern_mode]
        else:
            ret = ["NO_PATTERN"]
        return ret
    
    def colr_set(self, str0, str1, str2, str3, str4):
        ret = None
        if str0 == 'ON' or str0 == 'OFF':
            match str1:
                case 'COLOR':
                    if (int(str2) >= 0 and int(str2) <= 255) and (int(str3) >= 0 and int(str3) <= 255) and (int(str4) >= 0 and int(str4) <= 255):
                        grayscale_R = int(str2)
                        grayscale_G = int(str3)
                        grayscale_B = int(str4)
                        ret = [str0, str1, str2, str3, str4]
                case 'W':
                    if (int(str2) >= 0 and int(str2) <= 255):
                        grayscale_R = int(str2)
                        grayscale_G = int(str2)
                        grayscale_B = int(str2)
                        ret = [str0, str1, str2]
                case 'R':
                    if (int(str2) >= 0 and int(str2) <= 255):
                        grayscale_R = int(str2)
                        grayscale_G = 0
                        grayscale_B = 0
                        ret = [str0, str1, str2]
                case 'G':
                    if (int(str2) >= 0 and int(str2) <= 255):
                        grayscale_R = 0
                        grayscale_G = int(str2)
                        grayscale_B = 0
                        ret = [str0, str1, str2]
                case 'B':
                    if (int(str2) >= 0 and int(str2) <= 255):
                        grayscale_R = 0
                        grayscale_G = 0
                        grayscale_B = int(str2)
                        ret = [str0, str1, str2]
                case _:
                    pass
        if ret != None:
            if str0 == 'ON':
                if not self.script_run(bytearray([
                    0x79, 0x80, 0x04, 0x3D, 0x01, 0x00,  #pattern generator disabled
                    0x79, 0x80, 0x04, 0x3F, 0x01, grayscale_R,
                    0x79, 0x80, 0x04, 0x40, 0x01, grayscale_G,
                    0x79, 0x80, 0x04, 0x41, 0x01, grayscale_B,
                    0x79, 0x80, 0x04, 0x42, 0x01, grayscale_R,
                    0x79, 0x80, 0x04, 0x43, 0x01, grayscale_G,
                    0x79, 0x80, 0x04, 0x44, 0x01, grayscale_B,
                    0x79, 0x80, 0x04, 0x3D, 0x01, 0x01,  #pattern generator enabled
                ])):
                    ret = None
            elif str0 == 'OFF':
                if not self.script_run(bytearray([
                    0x79, 0x80, 0x04, 0x3F, 0x01, grayscale_R,
                    0x79, 0x80, 0x04, 0x40, 0x01, grayscale_G,
                    0x79, 0x80, 0x04, 0x41, 0x01, grayscale_B,
                    0x79, 0x80, 0x04, 0x42, 0x01, grayscale_R,
                    0x79, 0x80, 0x04, 0x43, 0x01, grayscale_G,
                    0x79, 0x80, 0x04, 0x44, 0x01, grayscale_B,
                ])):
                    ret = None

        return ret

    def pattern_test(self):
        time = 0.2
        color_l = [0, 6, 10, 21, 33, 65, 91, 96, 102, 114,
                   163, 183, 216, 222, 232, 244, 255]

        self.colr_set("ON", "R", '255', "NONE", "NONE")
        sleep(time)
        self.colr_set("ON", "G", '255', "NONE", "NONE")
        sleep(time)
        self.colr_set("ON", "B", '255', "NONE", "NONE")
        sleep(time)
        for m in color_l:
            self.colr_set("ON", "W", m, "NONE", "NONE")
            sleep(time)

if __name__ == "__main__":
    # io = c_uart("COM7")
    io = AUO_Ft4222('FT4222 A')
    io.auo_i2cMaster_Init(100)
    io.auo_i2cMaster_Reset()
    serdes = c_serdes(io)
    if(sys.argv[1] == "swap"):
        serdes.serdes_sio_swap()
        sleep(0.5)
        data = b'\x00\x11'
        result = io.read(data, 1)
        print("Get 0x11: ", result)
        sleep(0.5)
        data = b'\x00\x13'
        result = io.read(data, 1)
        print("Get 0x13: ", result)
        sleep(0.5)        
        data = b'\x00\x28'
        result = io.read(data, 1)
        print("Get 0x28: ", result)
        sleep(0.5)       
        data = b'\x00\x04'
        result = io.read(data, 1)
        print("Get 0x04: ", result)        
        
        # while(1):
        #     result = io.read(data, 1)
        #     print("Get 0x13: ", result)
        #     if( int.from_bytes(result, byteorder='big') & 0x08 ) == 0x00:
        #         sleep(1)
        #     else:
        #         break
    # else:
    serdes.serdes_default_init()
    # ret = serdes.serdes_register_read(0x80, 0x6418)
    # print(hex(ret))
    # ret = serdes.serdes_register_read(0x80, 0x6419)
    # print(hex(ret))
    # ret = serdes.serdes_register_read(0x80, 0x641A)
    # print(hex(ret))
    # ret = serdes.serdes_register_read(0x80, 0x0013)
    # print(hex(ret))
