import sys
import os
import time
import random
from serdes.socket_client_i2c import *
import ft4222
import io
import ft4222.I2CMaster
from ft4222.I2CMaster import Flag as I2C_Flag
from ft4222.GPIO import Dir, Port, Output,Trigger
from PyQt5.QtCore import QObject, QThread, pyqtSignal


# I2C FLAG Include:
'''
NONE: No start nor stopbit
START: Startbit
REPEATED_START: Repeated startbit (will not send master code in HS mode)
STOP: Stopbit
START_AND_STOP: Startbit and stopbit
'''

slave = 0x71 # address

class AUO_Ft4222(QObject):
    signal_progress_update = pyqtSignal()
    signal_update_log = pyqtSignal(str)

    def __init__(self, _string, addr=None):
        super(AUO_Ft4222, self).__init__()
        self.dev = 0
        self.devid = _string
        if (addr):
            self.slave_addr = addr
            print("Set remote address 0x%02X"%(self.slave_addr))
        self.status = 0xFF
        self.data = 0
        self.err_wrongorder = 0
        self.err_lenexceed = 0
        self.err_lenless = 0
        self.err_fragment = 0
        self.err_fileheader = 0
        self.err_fileheader_fragment = 0
        self.err_fileheader_size = 0
        self.err_fileheader_checksum = 0
        self.filetotalsize = 0
        self.filecurrentsize = 0
        print("init RDY:",_string)
        self.auo_opendevice()
        self.updatefile = None
        self.BL_state = 1
        
    def close(self):
        if self.dev != 0:
            self.dev.close()
            self.dev = 0
            print("close device")
        else:
            print("no device to close")
        
    def parse_memory_file(self, file_path):
        data_array = []
        last_address = None

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or not line.startswith('@'):
                    continue
                try:
                    address_str, value_str = line.split(' ', 1)
                    address = int(address_str[1:], 16)  # Remove '@' and convert to int
                    value = int(value_str, 16)  # Convert data to int
                except ValueError:
                    print("Invalid line in memory file:", line)
                    continue
            
                if last_address is not None and address != last_address + 1:
                    raise ValueError(f"Address gap detected: {last_address} to {address}")
                
                data_array.append(value)
                last_address = address
                
        if len(data_array) < 256:
            data_array.extend([0] * (256 - len(data_array)))  # Pad with zeros to 256 bytes
        
        return data_array
        
    def cal_rcr8(self, data):
        crc = 0
        for v in data:
            crc ^= v
        return crc
    
    def setWrongOrder(self, value):
        self.err_wrongorder = value
        print("set Wrong Order: ", self.err_wrongorder)
        
    def setLenExceed(self, value):
        self.err_lenexceed = value
        print("set Data Length exceed: ", self.err_lenexceed)
        
    def setLenLess(self, value):
        self.err_lenless = value
        print("set Data Length short: ", self.err_lenless)
        
    def setFragment(self, value):
        self.err_fragment = value
        print("set Frag offset: ", self.err_fragment)
        
    def setFileHeader(self, value):
        self.err_fileheader = value
        print("set Head File: ", self.err_fileheader)
        
    def setFileHeaderFragment(self, value):
        self.err_fileheader_fragment = value
        
    def setFileHeaderLength(self, value):
        self.err_fileheader_size = value
        
    def setFileHeaderChecksum(self, value):
        self.err_fileheader_checksum = value
        
    def setFlashptr(self, value):
        if value < 0.0 or value > 100.0:
            return
        self.signal_progress_update.emit()
        
    def updatelog(self, str):
        self.signal_update_log.emit(str)
        
    def DeviceCheck(self):
        if self.dev == 0:
            print("no device now")
            return False
        else:
            return True

    def auo_opendevice(self):
        try:
            self.dev = SocketClientI2C("localhost", 27015)  # 這裡改成你的 socket client 類別
            print("Socket client I2C connected.")
        except Exception as e:
            print("Socket client I2C connect error:", e)
        # try:
        #     self.dev = ft4222.openByDescription(self.devid)
        # except ft4222.FT2XXDeviceError as e:
        #     print(e)

    def auo_i2cMaster_Init(self, I2C_speed):
        return True
        # if self.DeviceCheck():
        #     self.dev.i2cMaster_Init(I2C_speed)
        #     self.dev.setTimeouts(2000, 2000)
        # else:
        #     print("master init error")
        #     return False
    
    def write(self, data, size):
        if self.DeviceCheck():
            addr=data[1]>>1
            buf=data[2:]
            # self.updatelog("serdes write(0x%x): %s" % (addr, ' '.join('0x{:02X}'.format(x) for x in data)))
            try: 
                # self.dev.i2cMaster_WriteEx(addr,I2C_Flag.START_AND_STOP, buf)
                self.dev.write(addr, buf)
            except:                 
                self.updatelog("Ft4222 I2C Write Error!!")
        
    def read(self, addr, buff, size):
        try:
            if self.DeviceCheck():
                # ret = self.dev.i2cMaster_WriteEx(addr, I2C_Flag.START, buff)
                # return self.dev.i2cMaster_ReadEx(addr, I2C_Flag.REPEATED_START | I2C_Flag.STOP, size)
                return self.dev.read(addr, buff, size)
            else:
                return b'\0x00'
        except: 
            self.updatelog("Ft4222 I2C Write Error!!")
            return b'\0x00'

    def auo_i2cMaster_Write(self, int_slave_address, flag ,send_data):
        try: 
            if self.DeviceCheck():
                # self.dev.i2cMaster_WriteEx(int_slave_address,flag, send_data)
                print("asdfasdfasdfsd")
                self.dev.write(int_slave_address, send_data)
        except: 
            self.updatelog("Ft4222 I2C Write Error!!")
            

    # def auo_i2cMaster_Read(self, int_slave_address, flag, bytes_to_read):
    #     try: 
    #         if self.DeviceCheck():
    #             self.data = self.dev.i2cMaster_ReadEx(int_slave_address, flag, bytes_to_read)  
    #             return self.data #self.dev.i2cMaster_ReadEx(int_slave_address, flag, bytes_to_read)
    #         else:
    #             return b'\0x00'
    #     except: 
    #         self.updatelog("Ft4222 I2C Write Error!!")
    #         return b'\0x00'   

    def auo_i2cMaster_Reset(self):
        if (self.dev == 0): 
            print("no device now")
            return False
        else:
            # self.dev.i2cMaster_Reset()
            return True
        # print('Reset done')
        
    def auo_gpio_Init(self):
        return True
        if self.DeviceCheck():
            # use GPIO2 as gpio (not suspend out)
            self.dev.setSuspendOut(False)
            # use GPIO3 as gpio (not wakeup)
            self.dev.setWakeUpInterrupt(False)
            self.dev.gpio_Init(gpio2 = Dir.OUTPUT,gpio3 = Dir.INPUT)
            self.dev.gpio_Write(Port.P2, 0)
            return True
        else:
            return False
    
    def auo_wakeup_gpio_set(self, switch):
        return True
        try:
            if self.DeviceCheck():
                if (switch == True):
                    self.dev.gpio_Write(Port.P2, 0)
                else: 
                    self.dev.gpio_Write(Port.P2, 1)
        except:
            self.updatelog("Ft4222 I2C Write Error!!")
            return 0
    
    def auo_wakeup_gpio_get(self):
        return True
        try:
            if self.DeviceCheck():
                return self.dev.gpio_Read(Port.P2)
            else:
                return 0
        except:
            self.updatelog("Ft4222 I2C Write Error!!")
            return 0
        
    def auo_INT_gpio_get(self):
        return True
        try:
            if self.DeviceCheck(): 
                return self.dev.gpio_Read(Port.P3)
            else:
                return 0
        except:
            self.updatelog("Ft4222 I2C Write Error!!")
            return 0
        
    def auo_calculate_SHM_chechsum(self,checksum_data,length):
        total = 0
        for i in range(length):
           total += checksum_data[i]
        total = (total & 0xff)
        return ((total ^ 0xff) +1) & 0xff
    
    def auo_shm_update_prograss(self):
        if(self.filetotalsize > 0): 
            ret = int((self.filecurrentsize/self.filetotalsize)*100)
        else:
            ret = 0
        return ret
    
    def auo_shm_update_get_BL_Status(self): 
        return self.BL_state
    
    def auo_shm_update_file(self, file):
        '''MCU User file : *_USER.bin'''
        '''TCON User file : C300_1392x162_Realchip_*.bin'''
        '''DeMURA file : *.design_hex_rom'''
        filename = os.path.basename(file)
        if filename.endswith(".design_hex_rom"):
            self.file_type = "DeMURA"
        elif filename.endswith(("_USER.bin", "_BOOT.bin", "_UPDATER.bin")):
            self.file_type = "MCU"
        elif "Realchip" in filename:
            self.file_type = "TCON"
        else:
            self.updatelog("Invalid file. Please select *_USER.bin or C300_1392x162_Realchip_*.bin file.")
            return
        
        self.updatefile = file
        self.filecurrentsize = 0
        self.filetotalsize = 0 
        self.BL_state = 1
    
    def auo_shm_update_process(self):
        # global slave
        
        #monitor INTB falling
        #trigger_flag = Gpio_tag.dev.gpio_GetTriggerStatus(Port.P3)
        if self.BL_state == 1:
            send_data = bytearray([0x1D, 0x00]) # Update Indication Command, Normal Write, 0x1D
            checksum = self.auo_calculate_SHM_chechsum(send_data,2)
            checksum_byte = checksum.to_bytes(1,"big")
            send_data = send_data + checksum_byte
            self.auo_i2cMaster_Write(self.slave_addr, I2C_Flag.START_AND_STOP, send_data)
            self.updatelog("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in send_data)))
            self.BL_state = 2
                
        elif self.BL_state == 2:
            # result = self.auo_INT_gpio_get()
            # self.updatelog("Wait Remote INT: %02X" % (result))
            # if result == 1:
            send_data = b'\x9C'
            Result = self.read(self.slave_addr, send_data, 2)
            self.updatelog("serdes write 0x9C, and read: %s" % (' '.join('0x{:02X}'.format(x) for x in Result)))
            if Result[0] == 0x9D and Result[1] == 0x01:
                self.BL_state = 3
            else:
                time.sleep(0.1) 

        elif self.BL_state == 3:
            #if trigger_flag > 0:
            #Device_tag.dev.gpio_ReadTriggerQueue(Port.P3,trigger_flag)
            send_data = 0x9D  # Wait Display Notification Command, Interrupt, 0x9D
            result = self.read(self.slave_addr, send_data, 1)
            self.updatelog("serdes write 0x9D, and read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
            if result == b'\x01' or result == b'\x02':
                self.BL_state = 5
                self.updatelog("## MCU has entered bootloader mode.")
            else:
                self.BL_state = 3
                self.updatelog("## Wait for the MCU to enter bootloader mode.")
                time.sleep(1)
                
        # elif self.BL_state == 4:
        #     # for reset RX i2c clock 
        #     self.BL_state = 5; 
        
        elif self.BL_state == 5:
            #open bin file and read all data
            print("file type: ", self.file_type)
            if (self.file_type == "DeMURA"):
                binfile = io.BytesIO(bytearray(self.parse_memory_file(self.updatefile)))
                self.filetotalsize = len(binfile.getvalue())
                print("DeMURA file size: ", self.filetotalsize, "bytes")
            else:
                binfile = open(self.updatefile, 'rb')
                self.filetotalsize = os.path.getsize(self.updatefile)
                
            size_data = self.filetotalsize.to_bytes(4,"big")
            print("file size: ", self.filetotalsize, "bytes")
            
            bin_data = binfile.read()         
            
            if (self.err_fileheader == 0):
                if (self.err_fileheader_size):
                    header_data = bytearray(b'\x02\x00\x01\x01\x00\x00')
                else:
                    header_data = bytearray(b'\x02\x00\x01\x01\x00\x00\x00\x00')
                
                if (self.file_type == "TCON"):
                    header_data[4]=0x01
                    self.updatelog("Update target : TCON.")
                elif (self.file_type == "DeMURA"):
                    header_data[4]=0x02
                    self.updatelog("Update tartget : DeMURA.")
                elif (self.file_type == "MCU"):
                    header_data[4]=0x00
                    self.updatelog("Update tartget : MCU.")
                    
                header_data[5] = self.cal_rcr8(bin_data)
            else:
                header_data = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
            
            #所有byte除一次要傳送的byte數量，算出要送幾次command
            if (self.filetotalsize % 128 == 0):
                updata_count = self.filetotalsize // 128
            else:
                updata_count = (self.filetotalsize // 128) + 1
            
            self.updatelog("update file : %s, size: %d bytes, crc: 0x%02X." %(self.updatefile, self.filetotalsize, header_data[5]))
            
            cmd_ID = b'\x5C' # Update Transmission Command, Split Write, 0x5C
            packet_order = list(range(1, updata_count+1))
            if(self.err_wrongorder):
                random.shuffle(packet_order)    # 打亂順序
            else:
                packet_order.sort()             # 順序傳輸
            
            # 回到檔案開頭
            binfile.seek(0)
            
            for i in packet_order:
                if i == 1:
                    #number of data 0x0000~0x0200, 2 bytes(MSB)
                    self.filecurrentsize = (i-1) * 128
                    if (self.err_fileheader_fragment):
                        frag_offset_big = b'\xFF\xFF\xFF\xFF'
                    else:
                        frag_offset_big = self.filecurrentsize.to_bytes(4,"big")
                    
                    #一次取出byte數量
                    send_data = binfile.read(128)
                    
                    #組合checksum計算內容
                    checksum_data_byte = cmd_ID + frag_offset_big + size_data + header_data + send_data
                    checksum = self.auo_calculate_SHM_chechsum(checksum_data_byte,len(checksum_data_byte))
                    if (self.err_fileheader_checksum):
                        checksum = checksum + 1
                        
                elif i > 1:
                    self.filecurrentsize = (i-1) * 128                        
                    frag_offset_big = self.filecurrentsize.to_bytes(4,"big")
                    
                    #一次取出byte數量
                    send_data = binfile.read(128)
                    
                    # 傳送過長資料
                    if (self.err_lenexceed) and (i == 2):
                        send_data += b'\x00' * 5
                        
                    # 傳送過短資料
                    if (self.err_lenless) and (i == 3): 
                        send_data = send_data[:10]
                    
                    # frag offset set to 0xFFFFFFFF
                    if (self.err_fragment) and (i == 4):
                        frag_offset_big = (0xFFFFFFFF).to_bytes(4,"big")
                    
                    checksum_data_byte = cmd_ID + frag_offset_big + send_data
                    checksum = self.auo_calculate_SHM_chechsum(checksum_data_byte,len(checksum_data_byte)) % 256
                        
                #checksum取一個byte
                checksum_byte = checksum.to_bytes(1,"big")
                #組合 command
                    
                #get back slave state
                retry = 0
                while True:
                    try:
                        send_data = checksum_data_byte + checksum_byte
                        self.auo_i2cMaster_Write(self.slave_addr, I2C_Flag.START_AND_STOP, send_data)
                        # self.updatelog("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in send_data)))
                        self.updatelog("write data & offset: 0x%06X" %(self.filecurrentsize))
                        
                        time.sleep(0.1)
                        
                        # self.updatelog("serdes write: %s" % (' '.join('{:02X}'.format(x) for x in send_data)))
                        send_data = b'\x3D'
                        result = self.read(self.slave_addr, send_data, 1)
                        # print("get back result", result, "offset", self.filecurrentsize);
                        self.updatelog("serdes write 0x3D, and read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
                        # self.updatelog("read status: %s." %(result))
                        if result == b'\x02':
                            self.updatelog("Update have error!!")
                            return 1
                        
                        elif result == b'\x00':
                            break
                        
                        else:
                            retry = retry+1
                            self.updatelog("retry: %d"%(retry))
                            if retry >= 100:
                                i = 1
                                binfile.seek(0)
                                self.updatelog("resend again.!!")
                                break 
                            time.sleep(0.1)
                            
                    except Exception as e:
                        self.updatelog("Ft4222 I2C Write Error!!")
                        return 1
                    
                self.signal_progress_update.emit()
                
            #關bin檔
            self.BL_state = 1
            self.filecurrentsize = self.filetotalsize
            self.signal_progress_update.emit()
            self.updatelog("Update Complete.")
            self.updatefile = None
            binfile.close()
            return 0



if __name__ == '__main__':

    if len(sys.argv) >= 2:
        if os.path.exists(sys.argv[1]):
            filepath=sys.argv[1]
            print("Set Bin file : ", filepath)
        else:
            filepath='C300KUC01.0_T.00.00.01_USER.bin'
            print("Set Bin file default")
    else: 
        filepath='C300KUC01.0_T.00.00.01_USER.bin'
        print("Set Bin file default")
        
    print("ft422 list: %d" % ft4222.createDeviceInfoList())
    
	#set FT4222 A for I2C Master 
    Device_tag = AUO_Ft4222('FT4222 A')
    Device_tag.auo_opendevice()
    Device_tag.auo_i2cMaster_Init(400)
    Device_tag.auo_i2cMaster_Reset()
    
    #set FT4222 B for gpio
    Gpio_tag = AUO_Ft4222('FT4222 B')
    Gpio_tag.auo_opendevice()
    Gpio_tag.auo_gpio_Init()
    
    # do a i2c transfers where full control is required
    slave = 0x44 # address
    header_data = b'\x02\x00\x01\x01\x00\x00\x00\x00'
    BL_state = 1
    
    # fllow : 
    	# host -> 0x1D 0x00 -> Slave , update start 
    	# slave jump to bootlader 
    	# slave ready in bootloader , VCU_INT info to host 
    	# host -> 0x9C -> read 2 bytes, get interrupt factor  
    	# host -> 0x9D -> read 1 byte, get reprogramming status.
    	# host -> 0x5C 
		
    while True:
        #monitor INTB falling
        #trigger_flag = Gpio_tag.dev.gpio_GetTriggerStatus(Port.P3)
        if BL_state == 1:
            send_data = b'\x1D\x00' # Update Indication Command, Normal Write, 0x1D
            checksum = Device_tag.auo_calculate_SHM_chechsum(send_data,2)
            checksum_byte = checksum.to_bytes(1,"big")
            send_data = send_data + checksum_byte
            Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START_AND_STOP, send_data)
            BL_state = 3 # wait for slave enter bootloader
            # BL_state = 2 # for test INT 
            time.sleep(1)
            
        elif BL_state == 2:
            result = Gpio_tag.dev.gpio_Read(Port.P3)
            print("Wait Remote INT ", result);
            if result == 1:          
                send_data = b'\x9C'
                Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START, send_data)
                Result = Device_tag.dev.i2cMaster_ReadEx(slave, I2C_Flag.REPEATED_START | I2C_Flag.STOP, 2)
                print("Get interrupt factor", Result)
                if Result[0] == 0x9D:
                    BL_state = 3
                else:
                    time.sleep(1)
            else: 
                time.sleep(1)                 
                
        elif BL_state == 3:
            #if trigger_flag > 0:
			#Device_tag.dev.gpio_ReadTriggerQueue(Port.P3,trigger_flag)
            time.sleep(1)
            send_data = 0x9D  # Wait Display Notification Command, Interrupt, 0x9D
            # Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START_AND_STOP, send_data)
            Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START, send_data)
            # result = Device_tag.dev.i2cMaster_ReadEx(slave, I2C_Flag.START_AND_STOP, 1)
            result = Device_tag.dev.i2cMaster_ReadEx(slave, I2C_Flag.REPEATED_START | I2C_Flag.STOP, 1)
            print("cmd 0x9D get back result", result); 
            if result == b'\x01':
            	BL_state = 4
            else:
            	BL_state = 3
            
        elif BL_state == 4:
            time.sleep(1)
            #read bin file
            # filepath='C300KUC01.0_T.00.00.01_USER.bin'
            #open bin file and read all data
            binfile = open(filepath, 'rb')
            #get all byte size
            size = os.path.getsize(filepath)
            size_data = size.to_bytes(4,"big")
            #所有byte除一次要傳送的byte數量，算出要送幾次command
            updata_count = (size/128) + 1
            updata_count = int(updata_count)
            int_count = 0
            print("update file : ", filepath)
            print("file size   : ", size, "bytes")
            cmd_ID = b'\x5C' # Update Transmission Command, Split Write, 0x5C
            for i in range(1,updata_count,1):
                if i == 1:
                    #number of data 0x0000~0x0200, 2 bytes(MSB)
                    frag_offset = (i-1) * 128
                    frag_offset_big = frag_offset.to_bytes(4,"big")
                    #一次取出byte數量
                    send_data = binfile.read(128)
                    #組合checksum計算內容
                    checksum_data_byte = cmd_ID + frag_offset_big + size_data + header_data + send_data
                    checksum = Device_tag.auo_calculate_SHM_chechsum(checksum_data_byte,145)
                    
                elif i > 1:
                    frag_offset = (i-1) * 128
                    frag_offset_big = frag_offset.to_bytes(4,"big")
                    #一次取出byte數量
                    send_data = binfile.read(128)
                    checksum_data_byte = cmd_ID + frag_offset_big + send_data
                    checksum = Device_tag.auo_calculate_SHM_chechsum(checksum_data_byte,133)
                    checksum = checksum % 256
                    
                # print("fragOffset:", frag_offset)
                #checksum取一個byte
                checksum_byte = checksum.to_bytes(1,"big")
                #組合 command
                
				#get back slave state
                retry = 0
                while True:
                    send_data = checksum_data_byte + checksum_byte
                    Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START_AND_STOP, send_data)
                    time.sleep(0.02)

                    send_data = b'\x3D'
                    # Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START_AND_STOP, send_data)
                    Device_tag.dev.i2cMaster_WriteEx(slave, I2C_Flag.START, send_data)
                    # result = Device_tag.dev.i2cMaster_ReadEx(slave, I2C_Flag.START_AND_STOP, 1)
                    result = Device_tag.dev.i2cMaster_ReadEx(slave, I2C_Flag.REPEATED_START | I2C_Flag.STOP, 1)
                    print("get back result", result, "offset", frag_offset); 
                    if result == b'\x00':
                        break
                    else:
                        retry = retry+1
                        print("retry", retry)
                        if retry >= 40:
                            i = 1
                            binfile.seek(0)
                            print("resend")
                            break 
                        time.sleep(0.1)
								
                # if i == 16:
                #     break   
            #關bin檔
            binfile.close()
            break
        else:
            break