# -*- coding: utf-8 -*-

import os, sys
import re
from shm_simulator import Ui_MainWindow
from serdes.serdes_init import *
from serdes.pctool_SHM import * 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QColor, QFont
import configparser, shutil
from datetime import datetime
import fnmatch
import ctypes

bitfield_names = {
    63: "reserved", 62: "GCPS", 61: "CADB", 60: "ABL", 59: "reserved", 58: "AUO_Thermal",
    57: "reserved", 56: "AUO_Demura", 55: "FALN(EM_PWC)", 54: "FALN(EM_STV)", 53: "POFF",
    52: "AIR(IRC)", 51: "CGM", 50: "DGC", 49: "AG", 48: "RCN",
    47: "Romcode download fail", 46: "iSP lock fail",
    45: "reserved", 44: "reserved", 43: "reserved", 42: "reserved", 41: "reserved", 40: "reserved",
    39: "SD_Fail_Flag[7]", 38: "SD_Fail_Flag[6]", 37: "SD_Fail_Flag[5]", 36: "SD_Fail_Flag[4]",
    35: "SD_Fail_Flag[3]", 34: "SD_Fail_Flag[2]", 33: "SD_Fail_Flag[1]", 32: "SD_Fail_Flag[0]",
    31: "GPIO_Fail_Flag[7]", 30: "GPIO_Fail_Flag[6]", 29: "GPIO_Fail_Flag[5]", 28: "GPIO_Fail_Flag[4]",
    27: "GPIO_Fail_Flag[3]", 26: "GPIO_Fail_Flag[2]", 25: "GPIO_Fail_Flag[1]", 24: "GPIO_Fail_Flag[0]",
    23: "GOA_Fail_Flag[7]", 22: "GOA_Fail_Flag[6]", 21: "GOA_Fail_Flag[5]", 20: "GOA_Fail_Flag[4]",
    19: "GOA_Fail_Flag[3]", 18: "GOA_Fail_Flag[2]", 17: "GOA_Fail_Flag[1]", 16: "GOA_Fail_Flag[0]",
    15: "eDP_RX1_Fail_Flag[7]", 14: "eDP_RX1_Fail_Flag[6]", 13: "eDP_RX1_Fail_Flag[5]", 12: "eDP_RX1_Fail_Flag[4]",
    11: "eDP_RX1_Fail_Flag[3]", 10: "eDP_RX1_Fail_Flag[2]", 9: "eDP_RX1_Fail_Flag[1]", 8: "eDP_RX1_Fail_Flag[0]",
    7: "eDP_RX0_Fail_Flag[7]", 6: "eDP_RX0_Fail_Flag[6]", 5: "eDP_RX0_Fail_Flag[5]", 4: "eDP_RX0_Fail_Flag[4]",
    3: "eDP_RX0_Fail_Flag[3]", 2: "eDP_RX0_Fail_Flag[2]", 1: "eDP_RX0_Fail_Flag[1]", 0: "eDP_RX0_Fail_Flag[0]",
}

Power_status_map = {
    0: "INIT",
    1: "UP", 
    2: "ON", 
    3: "NORMAL",
    4: "OFF",
    5: "DOWN",
    6: "WAIT_HOST_OFF",
    7: "MAX"
}

Cross_Pattern_map = {
    0: "OFF", 
    1: "Red",
    2: "Green",
    3: "Blue"
}

TEMP_TO_ADC_MAP = {
    -40: 3977, -39: 3967, -38: 3957, -37: 3946, -36: 3934, -35: 3922, -34: 3909, -33: 3896,
    -32: 3882, -31: 3868, -30: 3853, -29: 3837, -28: 3821, -27: 3804, -26: 3786, -25: 3767,
    -24: 3748, -23: 3728, -22: 3708, -21: 3686, -20: 3664, -19: 3642, -18: 3618, -17: 3594,
    -16: 3569, -15: 3543, -14: 3516, -13: 3489, -12: 3461, -11: 3432, -10: 3402, -9: 3372,
    -8: 3341, -7: 3309, -6: 3276, -5: 3243, -4: 3210, -3: 3175, -2: 3140, -1: 3104, 0: 3068,
    1: 3031, 2: 2994, 3: 2956, 4: 2918, 5: 2879, 6: 2840, 7: 2801, 8: 2761, 9: 2721, 10: 2681,
    11: 2640, 12: 2600, 13: 2559, 14: 2518, 15: 2477, 16: 2436, 17: 2394, 18: 2353, 19: 2312,
    20: 2271, 21: 2230, 22: 2190, 23: 2149, 24: 2109, 25: 2069, 26: 2029, 27: 1989, 28: 1950,
    29: 1911, 30: 1873, 31: 1835, 32: 1797, 33: 1760, 34: 1723, 35: 1687, 36: 1651, 37: 1615,
    38: 1580, 39: 1546, 40: 1512, 41: 1479, 42: 1446, 43: 1414, 44: 1382, 45: 1351, 46: 1320,
    47: 1290, 48: 1261, 49: 1232, 50: 1204, 51: 1176, 52: 1149, 53: 1122, 54: 1096, 55: 1070,
    56: 1045, 57: 1021, 58: 997, 59: 973, 60: 950, 61: 928, 62: 906, 63: 885, 64: 864, 65: 843,
    66: 823, 67: 804, 68: 785, 69: 766, 70: 748, 71: 731, 72: 713, 73: 697, 74: 680, 75: 664,
    76: 649, 77: 633, 78: 619, 79: 604, 80: 590, 81: 576, 82: 563, 83: 550, 84: 537, 85: 525,
    86: 513, 87: 501, 88: 489, 89: 478, 90: 467, 91: 456, 92: 446, 93: 436, 94: 426, 95: 416,
    96: 407, 97: 398, 98: 389, 99: 380, 100: 372, 101: 364, 102: 356, 103: 348, 104: 340,
    105: 333, 106: 325, 107: 318, 108: 312, 109: 305, 110: 298, 111: 292, 112: 286, 113: 280,
    114: 274, 115: 268, 116: 262, 117: 257, 118: 251, 119: 246, 120: 241
}

serdes_patterns = {
    'ColorBar': script_mode.colorbar_mg,
    'Red': script_mode.red,
    'Green': script_mode.green,
    'Blue': script_mode.blue,
    'White': script_mode.white,
    'Black': script_mode.black,
    'Checkerboard': script_mode.checkerboard
}

class MainWindow(QtWidgets.QMainWindow):
    outputChanged = pyqtSignal(str)
    interruptMessage = pyqtSignal(str)
    updateFinished = pyqtSignal(str)
    gmsllinkMessage = pyqtSignal(str)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self._version_ = "V0.02.10"
        self._date_ = "20250819"
        self.remote_addr = 0x71
        self.txb_addr = 0x55
        self._config_log_switch = False
        self._config_MCU_Update = False   # set update page 1
        self._config_Test = False # for test
        self._config_TCON_update = False
        self._config_DeMura_update = False
        self._config_AutoRefresh = False
        self._config_AutoRefrshTime = 5
        self._config_InterruptNotify = False
        self._config_GPSTime = False
        self._config_CRC_DataSave = False
        self.AutoRefresh_Thread_Flag = False
        self.serdes_loopback_Flag = False
        self.serdes_loopback_delay = 3
        self.serdes_loopback_pattern_index = 0
        self.initial_window_size = None
        self.initial_widget_geometries = {}
        self.initial_font_sizes = {}
        self.dirConfig = os.path.dirname(os.path.realpath(sys.argv[0]))
        self._checkConfigExist()
        self._readConfig("/conf/config.ini")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 移除固定的最小尺寸，或設定一個更小的值允許縮小
        # self.setMinimumSize(992, 678) 
        # 或者，如果您希望它不能縮小到初始尺寸以下，可以保留或在resizeEvent中
        self._init_component()
        self.outputChanged.connect(self.printf)
        self.interruptMessage.connect(self.Cuation_Popup)
        self.updateFinished.connect(self.update_finish)
        self.gmsllinkMessage.connect(self.ExitProgram)
        self._updaterFile = ""
        self._bootFile = ""
        self._userFile = ""
        self._tconFile = ""
        self._demuraFile = ""
        self.continue_test_total = 0
        self.continue_test_ok = 0
        self.continue_test_ng = 0
        self.TCONFlashDataGetFlag = False
        if(self._config_log_switch == True):
            self.logFileName = datetime.now().strftime('%Y-%m-%d_%H.%M.%S') + '_log.txt'
            log_path = os.path.join('log', self.logFileName)
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            self.logFile = open(log_path, 'w')
            
        QTimer.singleShot(100, self._defer_init)
        
    def _init_component(self):
        # Main window    
        ## Central widget 
        self.ui.SerdesInit_Btn.clicked.connect(self.serdes_mode_init)
        self.ui.ClearText_Btn.clicked.connect(self.Clear_TextBrowser)
        self.ui.checkBox_3.clicked.connect(self.Wakeup_GPIO_Process)
        self.ui.checkBox_interruptNotify.clicked.connect(self.Interrupt_Notify_Set)
        ### tab widget
        #### Command tab
        ##### Power Command tab
        self.ui.label_55.setVisible(self._interval_test)
        self.ui.label_56.setVisible(self._interval_test)
        self.ui.label_60.setVisible(self._interval_test)
        self.ui.com_repeat_time.setVisible(self._interval_test)
        self.ui.com_repeat_time.setEnabled(self._interval_test)
        self.ui.com_repeat_bright_start.setVisible(self._interval_test)
        self.ui.com_repeat_bright_start.setEnabled(self._interval_test)
        self.ui.com_repeat_bright_stop.setVisible(self._interval_test)
        self.ui.com_repeat_bright_stop.setEnabled(self._interval_test)
        self.ui.checkBox_2nd_refresh.setVisible(self._interval_test)
        self.ui.checkBox_2nd_refresh.setEnabled(self._interval_test)
        self.ui.ContinuCmd_Btn.setVisible(self._interval_test)
        self.ui.ContinuCmd_Btn.setEnabled(self._interval_test)
        self.ui.continue_brightness_label.setVisible(self._interval_test)
        self.ui.continue_brightness_label.setEnabled(self._interval_test)
        
        ##### Refresh Command tab
        ##### Version Command tab
        ##### Identification tab
        ##### Supervision Frame tab
        
        #### Engineer tab
        self.ui.checkBox_2.clicked.connect(self.Engineer_Aging_Set)
        self.ui.checkBox_4.setVisible(self._config_AutoRefresh)
        self.ui.checkBox_4.setEnabled(self._config_AutoRefresh)
        self.ui.checkBox_4.clicked.connect(self.AutoRefresh_Flag_Process)
        self.ui.checkBox_3.setEnabled(True)
        self.ui.checkBox_derating.clicked.connect(self.Engineer_Derating_Set)               # derating
        self.ui.Derating_temp_Set.clicked.connect(self.Engineer_Derating_Curve_Set)    # derating curve set
        self.ui.EngSetRunCard_Btn.clicked.connect(self.Engineer_I2C_PID_Write_Process)
        self.ui.checkBox_Demura.setVisible(self._config_test_switch)
        self.ui.checkBox_Demura.clicked.connect(self.Engineer_Demura_Set)
        self.ui.checkBox_TC.setVisible(self._config_test_switch)
        self.ui.checkBox_TC.clicked.connect(self.Engineer_TC_Set)
        self.ui.checkBox_RCN.setVisible(self._config_test_switch)
        self.ui.checkBox_RCN.clicked.connect(self.Engineer_RCN_Set)
        self.ui.checkBox_gpstime.clicked.connect(self.GPSTime_Config_Set)
        self.ui.comboBox_11.currentIndexChanged.connect(self.Engineer_TCON_Flash_Get)
        self.ui.checkBox_fake_NTC.clicked.connect(self.Engineer_Derating_NTC_ADC_Set)
        self.ui.lineEdit_Fake_ADC.returnPressed.connect(self.Engineer_Derating_NTC_ADC_Set)
        
        #### Serdes tab
        self.ui.checkBox.clicked.connect(self.serdes_mode_tp)
        self.ui.comboBox_7.setEnabled(True)
        self.ui.comboBox_7.currentIndexChanged.connect(self.serdes_TeatPattern_Process)
        self.ui.checkBox_serdes_loop.clicked.connect(self.serdes_Loopback_Check_Process)

        self.ui.Serdes_Write_label.setVisible(self._serdes_register)
        self.ui.Serdes_Read_label.setVisible(self._serdes_register)
        self.ui.Serdes_write_Btn.setVisible(self._serdes_register)
        self.ui.Serdes_write_Btn.setEnabled(self._serdes_register)
        self.ui.Serdes_write_Btn.clicked.connect(self.Serdes_Register_Write)
        self.ui.serdes_write.setVisible(self._serdes_register)
        self.ui.serdes_write.returnPressed.connect(self.Serdes_Register_Write)
        self.ui.Serdes_read_Btn.setVisible(self._serdes_register)
        self.ui.serdes_read.setVisible(self._serdes_register)
        self.ui.serdes_read.setEnabled(self._serdes_register)
        self.ui.Serdes_read_Btn.clicked.connect(self.Serdes_Register_Read)
        self.ui.serdes_read.returnPressed.connect(self.Serdes_Register_Read)
        
        self.ui.serdes_write.setPlaceholderText("0x80,0x12,0x34,0x56")
        self.ui.serdes_read.setPlaceholderText("0x80,0x12,0x34")
        self.ui.Serdes_group_write_Btn.setVisible(self._serdes_register)
        self.ui.Serdes_group_write_Btn.setEnabled(self._serdes_register)
        self.ui.Serdes_group_write_Btn.clicked.connect(self.Serdes_Register_Read_Process)
        self.ui.plainTextEdit_serdes.setVisible(self._serdes_register)
        self.ui.plainTextEdit_serdes.setEnabled(self._serdes_register)
        self.ui.plainTextEdit_serdes.setPlaceholderText("Example:\n0x04,0x80,0x7A,0x14,0x01\n0x00,0x64					//DELAY\n...")

        
        #### Update tab 
        # Engineer tab 
        self.ui.lineEdit_I2CW.setPlaceholderText("0x[addr],0x[register],0x[length],0x[data...]")
        self.ui.lineEdit_I2CW.returnPressed.connect(self.Engineer_I2C_Write_Process)
        self.ui.lineEdit_I2CR.setPlaceholderText("0x[addr],0x[register],0x[length]")
        self.ui.lineEdit_I2CR.returnPressed.connect(self.Engineer_I2C_Read_Process)
        self.ui.EngRefresh_Btn.clicked.connect(self.Engineer_Refresh)
        self.ui.comboBox_8.currentIndexChanged.connect(self.Engineer_BackLight_Set)

        self.ui.reportID_Btn.clicked.connect(self.ReportIDCmd_Process)
        self.ui.displayStatus_Btn.clicked.connect(self.DisplayStatusCmd_Process)
        self.ui.label_version.setText(self._version_)
        self.ui.label_date.setText(self._date_)
        self.ui.RefershCmd_Btn.clicked.connect(self.RefershCmd_Process)
        self.ui.DiagnosisCmd_Btn.clicked.connect(self.DianosisStatusCmd_Process)
        
        self.ui.Engineer_Set_Group.setEnabled(self._config_test_switch)

        self.ui.PowerCmd_Btn.clicked.connect(self.PowerCmd_Process)
        self.ui.com_repeat_time.textChanged.connect(self.Continue_DelayTime_Process)
        # self.ui.VideoMute_Btn.clicked.connect(self.VideoMuteCmd_Process)
        self.ui.checkBox_SuperFrame.clicked.connect(self.SupervisionFrame_Switch)
        self.ui.GetVersion_Btn.clicked.connect(self.VersionCmd_Process)
        self.ui.GetID_Btn.clicked.connect(self.IdentificationCmd_Process)
        self.ui.GetFile_Btn.clicked.connect(self.UpdateCmd_SelectFile)
        self.ui.UpdateUser_Btn.clicked.connect(self.UpdateCmd_Process)
        self.ui.tab.setEnabled(self._config_TCON_update)
        self.ui.tab_3.setEnabled(self._config_MCU_Update)
        self.ui.GetUpdaterFile_Btn.clicked.connect(self._Get_UpdaterFile)
        self.ui.Update_Btn.clicked.connect(self._MCU_Update)
        self.ui.GetStatus_Btn.clicked.connect(self._Get_Target_Status)
        self.ui.StatusCmd_Btn.clicked.connect(self.StatusCmd_Process)
        
        if (self._config_TCON_update == False):
            self.ui.tabWidget_3.removeTab(self.ui.tabWidget_3.indexOf(self.ui.tab))
            self.ui.tab.setVisible(False)
            self.ui.tab.setEnabled(False)
            self.ui.label_28.setVisible(False)
            self.ui.label_file_tcon.setVisible(False)
            self.ui.ClearFlag_Btn.setVisible(False)
            self.ui.GetFile_TCON_Btn.setVisible(False)
            self.ui.Update_TCON_Btn.setVisible(False)
        else:
            self.ui.ClearFlag_Btn.clicked.connect(self.ClearFlag_Process)        
            self.ui.GetFile_TCON_Btn.clicked.connect(self.UpdateCmd_SelectFile)
            self.ui.Update_TCON_Btn.clicked.connect(self.UpdateCmd_Process)
        
        if (self._config_DeMura_update == False):
            self.ui.tabWidget_3.removeTab(self.ui.tabWidget_3.indexOf(self.ui.tab_4))
            self.ui.label_file_demura.setVisible(False)
            self.ui.label_29.setVisible(False)
            self.ui.tab_4.setVisible(False)
            self.ui.tab_4.setEnabled(False)
        else:
            self.ui.GetFile_DEMURA_Btn.clicked.connect(self.UpdateCmd_SelectFile)
            self.ui.Update_DEMURA_Btn.clicked.connect(self.UpdateCmd_Process)
            self.ui.Demura_Table_Btn.setVisible(True)
            self.ui.Demura_Table_Btn.clicked.connect(self._Get_DG_Table)
        
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)
        self.ui.UpdateStop_Btn.clicked.connect(self.UpdateStop_Process)
        
        # for test UI
        self.ui.ContinuCmd_Btn.setVisible(self._config_test_switch)
        self.ui.ContinuCmd_Btn.clicked.connect(self.ContinueCmd_Process) 
        self.ui.checkBox_update_wrongorder.setVisible(self._config_test_switch)
        self.ui.checkBox_update_wrongorder.clicked.connect(self.Update_Test_WrongOrder)
        self.ui.checkBox_update_datalenexceed.setVisible(self._config_test_switch)
        self.ui.checkBox_update_datalenexceed.clicked.connect(self.Update_Test_Length_Exceed)
        self.ui.checkBox_update_datalenless.setVisible(self._config_test_switch)
        self.ui.checkBox_update_datalenless.clicked.connect(self.Update_Test_Length_Short)
        self.ui.checkBox_update_fragerror.setVisible(self._config_test_switch)
        self.ui.checkBox_update_fragerror.clicked.connect(self.Update_Test_FragOffset_Error)
        self.ui.checkBox_update_FileHeader.setVisible(self._config_test_switch)
        self.ui.checkBox_update_FileHeader.clicked.connect(self.Update_Test_Header_Error)
        self.ui.checkBox_update_FileHeader_FragErr.setVisible(self._config_test_switch)
        self.ui.checkBox_update_FileHeader_FragErr.clicked.connect(self.Update_Test_Header_Frag_Error)
        self.ui.checkBox_update_FileHeader_length.setVisible(self._config_test_switch)
        self.ui.checkBox_update_FileHeader_length.clicked.connect(self.Update_Test_Header_Length_Error)
        self.ui.checkBox_update_FileHeader_checksum.setVisible(self._config_test_switch)
        self.ui.checkBox_update_FileHeader_checksum.clicked.connect(self.Update_Test_Header_Checksum_Error)

        if(self._tcon_asil == False):
            self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.tab_TconASIL))
            self.ui.tab_TconASIL.setVisible(False)
            self.ui.tab_TconASIL.setEnabled(False)
        else:
            self.ui.tab_TconASIL.setEnabled(self._tcon_asil)
            self.ui.ASILRefresh_Btn.clicked.connect(self.Engineer_TCON_ASIL_Get)
            # 設定 tableFailFlag 欄位縮放: Description 欄位自動延展，其餘欄位符合內容
            self.ui.tableFailFlag.setHorizontalHeaderLabels(["Bit", "Description", "Value"])
            header_fail_flag = self.ui.tableFailFlag.horizontalHeader()
            header_fail_flag.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            header_fail_flag.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            header_fail_flag.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            # 設定 powerbit_table 欄位縮放: 所有欄位平均分配寬度
            self.ui.powerbit_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        if(self._tcon_register == False):
            self.ui.tabWidget.removeTab(self.ui.tabWidget.indexOf(self.ui.tab_TconRegister))
            self.ui.tab_TconRegister.setVisible(False)
            self.ui.tab_TconRegister.setEnabled(False)
        else:
            self.ui.addr_input.setPlaceholderText("0xE7800060")
            self.ui.plainTextEdit.setPlaceholderText("Example:\n0xE7800060,0x00006E00\nE7800064,00006ED0\n0x00,0x64 //delay\n...")
            self.ui.TCON_RegGet_Btn.clicked.connect(self.Engineer_TCON_Register_Get)
            self.ui.bit_table.setRowCount(1)
            self.ui.bit_table.setColumnCount(32)
            self.ui.bit_table.setHorizontalHeaderLabels([str(i) for i in reversed(range(32))])
            self.ui.bit_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            for i in range(32):
                item = QTableWidgetItem('0')
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.bit_table.setItem(0, i, item)
        
            self.ui.bit_table.cellChanged.connect(self.update_combined_value)
            self.ui.addr_input.returnPressed.connect(self.Engineer_TCON_Register_Get)
            self.ui.TCON_RegWrite_Btn.clicked.connect(self.Engineer_TCON_Register_Set)
            self.ui.TCON_RegSend_Btn.clicked.connect(self.Engineer_TCON_Register_Send_Process)
            self.ui.TCON_RegSave_Btn.clicked.connect(self.Engineer_TCON_Register_Save_Process)
            self.ui.TCON_RegLoad_Btn.clicked.connect(self.Engineer_TCON_Register_Load_Process)
        
        self.ui.asil_input_edit.returnPressed.connect(self.Engineer_TCON_ASIL_MenuInput)
        self.ui.asil_input_edit.setPlaceholderText("0x6F 0x06... 13 bytes,Then Press Enter.")
        
        self.ui.EEPROM_refresh_Btn.clicked.connect(self.update_eeprom_display)
        # 設定 eeprom_table 欄位縮放: 所有欄位平均分配寬度
        self.ui.eeprom_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.ui.DTC_log_Btn.clicked.connect(self.Diagnosis_log_get)
        self.ui.dtc_log_index_edit.returnPressed.connect(self.Diagnosis_log_request)
        self.ui.DTC_log_clear_btn.clicked.connect(self.Diagnosis_log_clear)
        self.ui.DTC_log_request_btn.clicked.connect(self.Diagnosis_log_request)
        
        self.ui.comboBox_crosspattern.currentIndexChanged.connect(self.Engineer_cross_pattern_set)

        self.ui.progressBar.setStyleSheet('''
                                          QProgressBar {
                                              border: 2px solid #000;
                                              border-radius: 5px; 
                                              text-align:center; 
                                              hight: 50px; 
                                              width: 80px; 
                                              }
                                              QProgressBar::chunk {
                                                  background: #09c;
                                                  width: 1px;
                                            }
                                            ''')
        # Allow tabWidget_2 to be resizable by overriding its size constraints.
        # Set a very small minimum size to allow shrinking.
        self.ui.tabWidget_2.setMinimumSize(QtCore.QSize(10, 10))
        # Set a very large maximum size to allow expanding.
        self.ui.tabWidget_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
    
    def _defer_init(self):
        self._init_ft4222()
        self._init_serdes()
        self._init_threads()
        # 在UI完全初始化後記錄初始幾何資訊
        # 使用QTimer.singleShot確保在事件循環處理完初始顯示後再執行
        QtCore.QTimer.singleShot(0, self._store_initial_geometries_and_fonts)
        
    def _store_initial_geometries_and_fonts(self):
        """記錄主視窗和所有相關子元件的初始尺寸和字型大小。"""
        if self.initial_window_size is None and self.isVisible():
            self.initial_window_size = self.size()
            
            widgets_to_process = []
            # 收集 self.ui 中的所有 QWidget
            for name in dir(self.ui):
                widget = getattr(self.ui, name)
                if isinstance(widget, QtWidgets.QWidget) and widget != self.ui.centralwidget:
                    widgets_to_process.append(widget)

            # 遞歸收集所有子孫 QWidget
            all_widgets = []
            queue = widgets_to_process[:]
            visited_widgets = set() # To avoid processing widgets multiple times if they appear in multiple hierarchies

            while queue:
                current_widget = queue.pop(0)
                if current_widget in visited_widgets:
                    continue
                visited_widgets.add(current_widget)
                all_widgets.append(current_widget)
                # Find direct children and add to queue
                for child in current_widget.findChildren(QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
                    if child not in visited_widgets:
                         queue.append(child)
            
            # Platform-specific font scaling factor
            font_platform_scale = 1.0
            if sys.platform == "win32":
                # 範例：Windows 上的字型可能需要稍微大一點才能達到與 macOS 上相似的視覺效果。
                # 這個值可能需要根據實際效果進行調整。
                font_platform_scale = 0.9 # 例如，縮小10%
            elif sys.platform == "darwin": # macOS
                font_platform_scale = 1.0 # macOS 作為基準
            # elif sys.platform.startswith("linux"):
                # font_platform_scale = 1.0 # Linux 可能也需要調整
            
            # 去重並儲存
            for widget in all_widgets: # Already unique due to visited_widgets
                if widget:
                    self.initial_widget_geometries[widget] = widget.geometry()
                    if hasattr(widget, 'font') and callable(getattr(widget, 'font')):
                        current_font = widget.font()
                        original_size = -1
                        is_point_size_type = True # True for pointSize, False for pixelSize

                        if current_font.pointSize() > 0:
                            original_size = current_font.pointSize()
                        elif current_font.pixelSize() > 0:
                            original_size = current_font.pixelSize()
                            is_point_size_type = False
                        
                        if original_size > 0:
                            # 套用平台特定的縮放因子到原始大小
                            adjusted_initial_size = int(round(original_size * font_platform_scale))
                            if adjusted_initial_size < 1: # 確保最小合理大小
                                adjusted_initial_size = 1 
                            
                            # 將此調整後的大小應用於 widget
                            new_font = QtGui.QFont(current_font) # 創建新的字型物件進行修改
                            if is_point_size_type:
                                new_font.setPointSize(adjusted_initial_size)
                            else:
                                new_font.setPixelSize(adjusted_initial_size)
                            widget.setFont(new_font)
                            
                            # 儲存這個經過平台調整的初始大小，供 resizeEvent 使用
                            self.initial_font_sizes[widget] = adjusted_initial_size
                        else:
                            # 如果沒有有效的原始大小，則儲存一個預設值或跳過
                            self.initial_font_sizes[widget] = 8 # 預設回退值

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super(MainWindow, self).resizeEvent(event)

        if not self.initial_window_size or self.initial_window_size.width() == 0 or self.initial_window_size.height() == 0:
            if self.isVisible():
                 QtCore.QTimer.singleShot(0, self._store_initial_geometries_and_fonts)
            if not self.initial_window_size or self.initial_window_size.width() == 0 or self.initial_window_size.height() == 0:
                 return

        current_size = event.size()
        scale_w = current_size.width() / self.initial_window_size.width()
        scale_h = current_size.height() / self.initial_window_size.height()

        for widget, initial_geom in self.initial_widget_geometries.items():
            try:
                if not widget or not widget.parent(): # 檢查 widget 是否仍然有效且有父物件
                    continue
                new_x = int(initial_geom.x() * scale_w)
                new_y = int(initial_geom.y() * scale_h)
                new_width = max(1, int(initial_geom.width() * scale_w))
                new_height = max(1, int(initial_geom.height() * scale_h))
                widget.setGeometry(new_x, new_y, new_width, new_height)

                if widget in self.initial_font_sizes and self.initial_font_sizes[widget] > 0:
                    font_scale_factor = min(scale_w, scale_h) # 或者 (scale_w + scale_h) / 2.0
                    new_point_size = int(self.initial_font_sizes[widget] * font_scale_factor)
                    if new_point_size > 1:
                        font = widget.font()
                        font.setPointSize(new_point_size)
                        widget.setFont(font)
            except RuntimeError: 
                pass # Widget might have been deleted
            except Exception as e:
                # self.outputChanged.emit(f"Error resizing widget {type(widget).__name__}: {e}")
                pass

    def showEvent(self, event: QtGui.QShowEvent):
        super(MainWindow, self).showEvent(event)
        if self.initial_window_size is None:
            QtCore.QTimer.singleShot(0, self._store_initial_geometries_and_fonts)

    def _init_ft4222(self):
        # FT4222 module, GPIO
        self.ft4222_io = AUO_Ft4222('FT4222 B')
        result = self.ft4222_io.auo_gpio_Init()
        if (result == False):
            self.ExitProgram("FT4222 Init Error")
                    
        # FT4222 module , I2C 
        self.ft422_i2c = AUO_Ft4222('FT4222 A', self.remote_addr)
        result = self.ft422_i2c.auo_i2cMaster_Init(400)
        # result = self.ft422_i2c.auo_i2cMaster_Init(1000)
        if (result == False):
            self.ExitProgram("FT4222 Init Error")
        
    def _init_threads(self):
        # thread 
        ## Supervision thread 
        self.Supervision_thread = QThread()
        self.Supervision_thread.run = self.SupervisionFrameCmd_Process
        self._Supervision_thread_flag = False
        
        ## update thread 
        # self.update_thread = threading.Thread(target=self.UpdateProcess_thread)
        self.update_thread_flag = False
        self.update_thread = QThread()
        self.update_thread.run = self.UpdateProcess_thread
        
        ## update prograssbar thread        
        # self.UpdatePrograssbar_thread = threading.Thread(target=self.UpdatePrograssbar_Process)
        # self.UpdatePrograssbar_thread = QThread()
        # self.UpdatePrograssbar_thread.run = self.UpdatePrograssbar_Process
        
        self.GMSL_Link_Thread_process()
        
        self.WKUP_thread_Count = 0
        self.WKUP_thread_flag = False
        
        self.Main_thread_flag = True
        self.Main_thread = QThread()
        self.Main_thread.run = self.Main_thread_Process
        self.Main_thread.start()
        
    def GMSL_Link_Thread_process(self):
        self.gmsllink_thread_flag = True
        self.gmsllink_thread =QThread()
        self.gmsllink_thread.run = self.GSMLLink_Process
        self.gmsllink_thread.start()
    
    def update_finish(self, str):
        self.ui.progressBar.setValue(0)
        self.GMSL_Link_Thread_process()   
    
    def _init_serdes(self):
        # serdes init 
        self.serdes = c_serdes(self.ft422_i2c)
        if (self.serdes.io):
            self.serdes.serdes_sio_swap()
            
        self.ft422_i2c.signal_progress_update.connect(self.UpdatePrograssbar_Process)
        self.ft422_i2c.signal_update_log.connect(self.printf)
        # self.ft422_i2c.signal_update_text_update.connect()

    # Get Target Status, use Customer protocol 
    def _Get_Target_Status(self): 
        ''' use Command to get Wakeup Pin state form MCU '''
        cmd = bytearray([0xFD])
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        state = self.ft422_i2c.read(self.remote_addr, cmd, 1)
        self.outputChanged.emit("result: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        return state[0]
    
    def _Get_DG_Table(self):
        ''' get DG table '''
        cmd = bytearray([0xFC])
        result = self.ft422_i2c.read(self.remote_addr, cmd, 256)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.outputChanged.emit("result: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        return result[0]
    
    def ClearFlag_Process(self):
        cmd = bytearray([0xFD, 0x00, 0x00])
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 3))
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    # Get Wakeup Pin Process, use command to ask MCU, Wakeup pin state.  
    def Wakeup_GPIO_State_Get(self):
        ''' use Command to get Wakeup Pin state form MCU '''
        cmd = bytearray([0xFF,0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        result = self.ft422_i2c.read(self.txb_addr, cmd, 5)
        self.outputChanged.emit("serdes Read: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.outputChanged.emit("result: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        return result[0]

    # Set Wakeup Pin Process, use command to require MCU, wakeup pin state. 
    def Wakeup_GPIO_Process(self):
        ''' Use Command to Set Wakeup Pin state to MCU '''        
        cmd = bytearray([0xFF,0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
        if(self.ui.checkBox_3.isChecked()):
            cmd[2] = 0x01
        else:  
            cmd[2] = 0x02
        self.ft4222_io.auo_wakeup_gpio_set(cmd[2])
        self.ft422_i2c.auo_i2cMaster_Write(self.txb_addr, I2C_Flag.START_AND_STOP, cmd)
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))

    def Interrupt_Notify_Set(self):
        if (self.ui.checkBox_interruptNotify.isChecked()):
            self._config_InterruptNotify = True
        else:
            self._config_InterruptNotify = False

    def Wakup_interfere(self):
        self.outputChanged.emit("Wakeup interfere.")
            
    def Sleep_interfere(self):
        self.outputChanged.emit("Sleep interfere.")

    # print string on textBrowser, and save logo to file. 
    def printf(self, args): 
        curtime = datetime.now().strftime('%y/%m/%d %H:%M:%S.%f')[:-3]
        text = curtime + ' # ' + args
        self.ui.textBrowser.append(text)
        my_cursor = self.ui.textBrowser.textCursor()
        self.ui.textBrowser.moveCursor(my_cursor.End)
        QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents)
        if(self._config_log_switch == True):
            self.logFile.write(text+'\r\n')
            self.logFile.flush()
            
    # Clear TextBrowser content         
    def Clear_TextBrowser(self):
        self.ui.textBrowser.clear()
        
    # Main thread     
    def Main_thread_Process(self):
        cmd = bytearray([0xFF,0xFE, 0x00, 0x00, 0x00, 0x00, 0x00])
        times = 0
        # RX_INT_State = 0
        
        # 加入每個子任務的的timer
        last_int_check_time = time.time()
        last_auto_refresh_time = time.time()
        last_wakeup_check_time = time.time()
        last_gpstime_check_time = time.time()
        last_serdes_loopback_time = time.time()
        
        while self.Main_thread_flag:
            
            now = time.time()
            
            ## update thread 
            if (self.update_thread_flag == True):
                pass
                # self.ft422_i2c.auo_shm_update_process()
                # value = self.ft422_i2c.auo_shm_update_prograss()
                # if (value >= 100):
                #     self.update_thread_flag = False
                #     self.ui.GetFile_Btn.setEnabled(True)
                #     break; 

                #     self.ui.GetFile_Btn.setEnabled(True)
                #     self.gmsllink_thread_flag = True
                #     self.gmsllink_thread.start()
                
            ## Normal 
            else:
                ## Get INT GPIO Status
                if (self._config_InterruptNotify == True):
                    if now - last_int_check_time >= 0.1:
                        last_int_check_time = now
                        RX_INT_State_now = self.ft4222_io.auo_INT_gpio_get()
                        if (RX_INT_State_now == 1):
                                                        
                            try:
                                result = self.ReportIDCmd_Process()
                                if (result[0] != 0xFF) and (result[1] != 0xFF):
                                    if (result[0] == 0x9D and result[1] == 0x01) or (result[0] == 0x88 and result[1] == 0x02):
                                        if (result[0] == 0x9D):
                                            state = self.DisplayStatusCmd_Process()
                                        else:
                                            state = self.StatusCmd_Process()
                                        result_str = ' '.join('0x{:02X}'.format(x) for x in result)
                                        state_str = ' '.join('0x{:02X}'.format(x) for x in state)
                                        s = f"{result_str}\n content: {state_str}"
                                    else:
                                        s = "%s" % (' '.join('0x{:02X}'.format(x) for x in result))
                
                                    # send interrupt event to popup window
                                    self.interruptMessage.emit(s)
                                    self.outputChanged.emit("Received Interrupt Message.!!" + s)
                                    
                            except Exception as e:
                                self.outputChanged.emit("Error: %s" % (str(e)))
                                pass

                ## Supervision frame start
                # if (self._Supervision_thread_flag == True):
                
                if (self._config_GPSTime == True):
                    if now - last_gpstime_check_time >= 1:
                        last_gpstime_check_time = now
                        self.GPSTimeCmd_Process()
            
                ## Supervision frame end


                ## Serdes loopback
                if (self.serdes_loopback_Flag == True):
                    if now - last_serdes_loopback_time >= self.serdes_loopback_delay:
                        last_serdes_loopback_time = now
                        self.serdes_Loopback_Process()

                ## AutoRefresh
                if (self.AutoRefresh_Thread_Flag == True) and (now - last_auto_refresh_time >= self._config_AutoRefrshTime):
                    last_auto_refresh_time = now
                    
                    self.Engineer_Thermal_Get()         # 9        
                    time.sleep(20/1000)
                    self.Engineer_Diagnosis_Get()       # A
                    time.sleep(20/1000)
                    self.Engineer_Serdes_State_Get()    # B
                    time.sleep(20/1000)
                    self.Engineer_TCON_State_Get()      # C
                    time.sleep(20/1000)
                    self.Engineer_Sensors_Get()         # D
                    time.sleep(20/1000)
                    self.Engineer_Brightness_Get()
                    self.Engineer_TCON_ASIL_Get()     
            
                ## Wakeup Test start start
                if(self.WKUP_thread_flag == True) and (now - last_wakeup_check_time >= 0.5):
                    last_wakeup_check_time = now
                    
                    if ((self.WKUP_thread_Count%6) == 0):
                        self.WKUP_thread_Count = 0
                        supervision_cmd = bytearray([0x3C])
                        state = self.ft422_i2c.read(self.remote_addr, supervision_cmd, 1)
                        if (state == b'\xA5'):
                            self.outputChanged.emit(" %04d, MCU OK, Receive 0xA5."%(times)) 
                        else: 
                            if (cmd[2] == 0x00):
                                self.outputChanged.emit(" %04d, MCU NO Response"%(times))
                        
                        if (cmd[2] == 0x00):
                            cmd[2] = 0x01
                            # self.outputChanged.emit(" %04d, Set Sleep Mode"%(times))  
                        else:
                            times += 1 
                            cmd[2] = 0x00
                            self.outputChanged.emit(" %04d, Set Wakeup Mode"%(times))           
                                
                        self.ft422_i2c.auo_i2cMaster_Write(self.txb_addr, I2C_Flag.START_AND_STOP, cmd)
                        
                        self.WKUP_thread_Count += 1
                    ## Wakup Test end
                
                time.sleep(0.001)

    '''' 主要更新線程 '''
    def UpdateProcess_thread(self):
        ## terminate other thread process , and wait Process close  
        while self.Supervision_thread.isRunning():
            self.outputChanged.emit("Wait Supervision thread stop...")
            time.sleep(1)
        while self.gmsllink_thread.isRunning(): 
            self.outputChanged.emit("GMSL Link thread stop...")
            time.sleep(1)

        ## only update user file 
        if self.ui.tabWidget_3.currentIndex() == 0:
            self.outputChanged.emit("Update User File...")
            self.ui.UpdatingFile_label.setText(self.ui.label_file.text())
            self.ui.GetFile_Btn.setEnabled(False)
            self.ui.UpdateUser_Btn.setEnabled(False)
            
            self.ft422_i2c.auo_shm_update_file(self._userFile)
            
            while True:
                try:
                    if (self.ft422_i2c.auo_shm_update_process() > 0):
                        break;
                     
                    value = self.ft422_i2c.auo_shm_update_prograss()
                    
                    if (value >= 100):
                        break;
                    
                    time.sleep(0.5)
                except:
                    pass
                            
        ## update TCON file    
        elif (self.ui.tabWidget_3.currentIndex() == 2):
            self.outputChanged.emit("Update TCON File...")
            self.ui.UpdatingFile_label.setText(self.ui.label_file_tcon.text())
            self.ui.GetFile_TCON_Btn.setEnabled(False)
            self.ui.Update_TCON_Btn.setEnabled(False)
            self.ui.ClearFlag_Btn.setEnabled(False)
            
            self.ft422_i2c.auo_shm_update_file(self._tconFile)
            
            while True:
                try:
                    if (self.ft422_i2c.auo_shm_update_process() > 0):
                        break; 
                    
                    value = self.ft422_i2c.auo_shm_update_prograss()

                    if (value >= 100):
                        break;
                    
                    time.sleep(0.5)
                except:
                    pass
            
        ## update Demura file
        elif (self.ui.tabWidget_3.currentIndex() == 3):
            self.outputChanged.emit("Update Demura File...")
            self.ui.UpdatingFile_label.setText(self.ui.label_file_demura.text())
            self.ui.GetFile_DEMURA_Btn.setEnabled(False)
            self.ui.Update_DEMURA_Btn.setEnabled(False)
            self.ui.Demura_Table_Btn.setEnabled(False)
            
            self.ft422_i2c.auo_shm_update_file(self._demuraFile)
            
            while True:
                try:
                    if (self.ft422_i2c.auo_shm_update_process() > 0):
                        break;
                    
                    value = self.ft422_i2c.auo_shm_update_prograss()

                    if (value >= 100):
                        break; 
                    
                    time.sleep(0.5)
                except:
                    pass
                            
        ## update whole MCU
        else: 
            self.ui.Update_Btn.setEnabled(False) 
            self.ui.GetUpdaterFile_Btn.setEnabled(False)
            self.ui.GetStatus_Btn.setEnabled(False)      
            
            # get RX status, check in Bootloader status(0x04). 
            state = self._Get_Target_Status()
            if state == 0x04: 
                self.ui.UpdatingFile_label.setText(self.ui.UpdaterFile_label.text())
                self.ft422_i2c.auo_shm_update_file(self._updaterFile)
                
                while True:
                    self.ft422_i2c.auo_shm_update_process()
                    value = self.ft422_i2c.auo_shm_update_prograss()
                    if (value >= 100):
                        break; 
                    time.sleep(0.5)
                    
            time.sleep(1)
            state = self._Get_Target_Status()
            ''' add status 0x00 for CV phase '''
            if state == 0x02 or state == 0x00:
                self.ui.UpdatingFile_label.setText(self.ui.BootFile_label.text())
                self.ft422_i2c.auo_shm_update_file(self._bootFile)
            
                while True:
                    self.ft422_i2c.auo_shm_update_process()
                    value = self.ft422_i2c.auo_shm_update_prograss()
                    if (value >= 100):
                        break; 
                    time.sleep(0.5)
            
            time.sleep(1)
            state = self._Get_Target_Status()
            ''' add status 0x00 for CV phase'''
            if state == 0x01 or state == 0x00:
                self.ui.UpdatingFile_label.setText(self.ui.AppFile_label.text())
                self.ft422_i2c.auo_shm_update_file(self._userFile)
                
                while True:
                    self.ft422_i2c.auo_shm_update_process()
                    value = self.ft422_i2c.auo_shm_update_prograss()
                    if (value >= 100):
                        break; 
                    time.sleep(0.5)
                    
        self.ui.UpdatingFile_label.setText("Updating File :")
        if self.ui.tabWidget_3.currentIndex() == 0:
            self.ui.GetFile_Btn.setEnabled(True)
            self.ui.UpdateUser_Btn.setEnabled(True)
            
        elif (self.ui.tabWidget_3.currentIndex() == 2):
            self.ui.GetFile_TCON_Btn.setEnabled(True)
            self.ui.Update_TCON_Btn.setEnabled(True)
            self.ui.ClearFlag_Btn.setEnabled(True)              
        
        elif (self.ui.tabWidget_3.currentIndex() == 3):
            self.ui.GetFile_DEMURA_Btn.setEnabled(True)
            self.ui.Update_DEMURA_Btn.setEnabled(True)
            self.ui.Demura_Table_Btn.setEnabled(True)                  
                      
        else:
            self.ui.Update_Btn.setEnabled(True) 
            self.ui.GetUpdaterFile_Btn.setEnabled(True)
            self.ui.GetStatus_Btn.setEnabled(True)
        
        self.updateFinished.emit("Update Finished")
        
    def UpdatePrograssbar_Process(self):
        ''' Update PrograssBar '''
        value = self.ft422_i2c.auo_shm_update_prograss()
        self.ui.progressBar.setValue(value)
        
    def GSMLLink_Process(self):
        MediaBar_Wakeup = True      
        while (self.gmsllink_thread_flag):
            cmd = bytearray([0x00, 0x13])
            ## check GMSL link status
            ## 0x00: GMSL link status, 0x13: GMSL link status
            result = self.ft422_i2c.read(0x40, cmd, 1)
            if (len(result) != 1):
                self.gmsllink_thread_flag = False
                self.gmsllinkMessage.emit("FT4222 GMSLlink Error")
                continue
            
            # self.outputChanged.emit(f"GMSL link status: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
            if(result[0]&0x08) and (result[0]!=0xFF): 
                self.ui.label_gmsllinkstate.setStyleSheet("color:green")
                self.ui.label_gmsllinkstate.setText("GMSL LINK LOCKED.")
                
                ## MediaBar wakeup from sleep mode
                if (MediaBar_Wakeup == False):
                    MediaBar_Wakeup = True
                    if(self.ui.checkBox.isChecked()):
                        self.serdes_mode_tp()
                    else:
                        self.serdes_mode_init()        
            else:
                self.ui.label_gmsllinkstate.setStyleSheet("color:red")
                self.ui.label_gmsllinkstate.setText("GMSL LINK NOT LOCKED.")
                MediaBar_Wakeup = False
                ## GMSL LINK LOSS, check the checkbox 
                if(self.ui.checkBox_3.isChecked()):
                    self.serdes.serdes_sio_swap()
                    # get wakeup pin status from MCU
                    state = self.Wakeup_GPIO_State_Get()
                    # check wakeup pin status, is need issue command ? 
                    if (state == 0x02) or (state == 0xFF):
                        # self.ui.label_gmsllinkstate.setStyleSheet("color:green")
                        # self.ui.label_gmsllinkstate.setText("GMSL LINK LOCKED.")
                        self.Wakeup_GPIO_Process()
                        
            time.sleep(1)
        
    def AutoRefresh_Flag_Process(self):
        if(self.ui.checkBox_4.isChecked()):
            self.AutoRefresh_Thread_Flag = True
        else:
            self.AutoRefresh_Thread_Flag = False
        
    def serdes_mode_init(self):
        self.serdes.serdes_sio_swap()
        if (self.ui.CVTable_Btn.isChecked()):
            self.serdes.serdes_default_init(1)  ## CV table 
        elif (self.ui.MQTable_Btn.isChecked()):
            self.serdes.serdes_default_init(2)  ## MQ table
        
    def serdes_mode_tp(self):
        if (self.ui.checkBox.isChecked()):
            self.ui.comboBox_7.setEnabled(True)
            self.ui.comboBox_7.setCurrentIndex(0)
            self.serdes_TeatPattern_Process()
        else: 
            self.serdes.serdes_mode_init(script_mode.tp_disable)
            # self.ui.comboBox_7.setEnabled(False)
        
    def serdes_TeatPattern_Process(self):
        pattern_name = self.ui.comboBox_7.currentText()
        # self.printf("New item: %s"%(item))
        self.outputChanged.emit("New item:%s"%(pattern_name))
        pattern = serdes_patterns[pattern_name]

        # set pattern
        if pattern:
            self.serdes.serdes_mode_init(pattern)
            return 'OK',[]
        else:
            self.outputChanged.emit("Unknown pattern.")
            return 'ERR',['PARAMS_ERR']

    def serdes_Loopback_Check_Process(self):
        if (self.ui.checkBox_serdes_loop.isChecked()):
            if not self.ui.checkBox.isChecked():
                self.outputChanged.emit(self._Textbrowser_Color(1, "Please enable Test Pattern first."))
                self.ui.checkBox_serdes_loop.setChecked(False)
                return
            self.serdes_loopback_Flag = True
            self.serdes_loopback_pattern_index = self.ui.comboBox_7.currentIndex()
            self.outputChanged.emit("Serdes Loopback Start")
        else:
            self.serdes_loopback_Flag = False
            self.outputChanged.emit("Serdes Loopback Stop")

        custom_repeat_str = self.ui.lineEdit_serdes_loop_time.text().strip()
        if custom_repeat_str:
            try:
                self.serdes_loopback_delay = int(custom_repeat_str)
            except ValueError:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid loop time, use default 5 second."))
                self.ui.lineEdit_serdes_loop_time.setText("5")
                self.serdes_loopback_delay = 5  # Default to 5 seconds if invalid input
        else:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid loop time, use default 5 second."))
            self.ui.lineEdit_serdes_loop_time.setText("5")
            self.serdes_loopback_delay = 5  # Default to 5 seconds if no input

    def serdes_Loopback_Process(self):                   
        # get current pattern
        pattern_keys = list(serdes_patterns.keys())
        
        if self.serdes_loopback_pattern_index >= len(pattern_keys):
            self.serdes_loopback_pattern_index = 0
            
        pattern_name = pattern_keys[self.serdes_loopback_pattern_index]
        pattern_enum = serdes_patterns[pattern_name]
        
        self.outputChanged.emit(f"Serdes Loopback Pattern: {pattern_name}")
        self.serdes.serdes_mode_init(pattern_enum)

        self.serdes_loopback_pattern_index = (self.serdes_loopback_pattern_index+1) % len(pattern_keys)

                
    # Customer Protocol : Power Command
    def PowerCmd_Process(self):
        ''' Power Command '''
        cmd = bytearray([0x14, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # check AID checkbox state 
        if(self.ui.checkBox_aid.isChecked()): 
            # print("aid is checked")
            cmd[1] = cmd[1] | 0x80
        else: 
            # print("aid not be checked")
            cmd[1] = cmd[1] & 0x7F
        # check day/night mode state
        if (self.ui.checkBox_daymode.isChecked()): 
            # print("Night Mode")
            cmd[1] = cmd[1] | 0x08
        else:
            # print("day mode")
            cmd[1] = cmd[1] & 0xF7
        # check LCD On/OFF state
        if (self.ui.checkBox_LCD.isChecked()):
            # print("LCD ON")
            cmd[1] = cmd[1] & 0xFB
        else: 
            # print("LCD Off")
            cmd[1] = cmd[1] | 0x04
        # get Illumination control step index 
        value = self.ui.comboBox.currentText()
        if(int(value, 16) == 255):
            cmd[2] = 255
        else: 
            cmd[2] = int(value)
        # print("Illumination Step: " , cmd[2])
        
        # get Brightness control step index 
        value = self.ui.comboBox_2.currentText().strip() # remove space
        try: 
            if value.startswith("0x") or value.startswith("0X"): # remove 0x
                num_value = int(value, 16)
            elif value.isdigit():
                num_value = int(value)
            else:
                raise ValueError(f"Invalid value: {value}") # raise error
            
            if num_value == 255:
                cmd[3] = 255
            else:
                cmd[3] = num_value
                
        except ValueError as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Error: {e}"))
        
        # get Back light luminance control step text
        value_low_str = self.ui.comboBox_3.currentText().strip()
        value_high_str = self.ui.comboBox_9.currentText().strip()
        try: 
            num_value_low = int(value_low_str, 0)
            num_value_high = int(value_high_str, 0)
            
            if not (0 <= num_value_low <= 255) or not (0 <= num_value_high <= 255):
                raise ValueError(f"Invalid value: {value_low_str} or {value_high_str}")
            
            cmd[4] = 255 if num_value_low == 255 else num_value_low
            cmd[5] = 255 if num_value_high == 255 else num_value_high
                
        except ValueError as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Error: {e}"))
        
        # cal checksum 
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 14))
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

    def Continue_DelayTime_Process(self):
        self.continue_test_total = 0
        self.continue_test_ok = 0
        self.continue_test_ng = 0
        self.ui.continue_brightness_label.setStyleSheet("")
        self.ui.continue_brightness_label.setText("Brightness Step: -, Result: None \n Total: 0, OK: 0, NG: 0.")

    def ContinueCmd_Process(self): 
        ''' Continue Command '''
        refresh_cmd = bytearray([0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\
                                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xFF, 0x00, 0xFF, \
                                0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        power_cmd = bytearray([0x14, 0xC0, 0xFF, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        brightness = [0x0A, 0x09]
        repeat_time = int(self.ui.com_repeat_time.text().strip(), 10)/1000
        brightness[0] = int(self.ui.com_repeat_bright_start.text().strip(), 10)
        brightness[1] = int(self.ui.com_repeat_bright_stop.text().strip(), 10)
        
        self.continue_test_total = self.continue_test_total + 1
        
        for index, value in enumerate(brightness):
            start = time.perf_counter()
            
            ## first send power command
            if (index == 0):
                power_cmd[3] = value
                power_cmd[14] = self.ft422_i2c.auo_calculate_SHM_chechsum(power_cmd, 14)
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, power_cmd)
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in power_cmd)))
            else:
                ## second send refresh command
                if (self.ui.checkBox_2nd_refresh.isChecked()):
                    refresh_cmd[19] = value
                    refresh_cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(refresh_cmd, 29))
                    self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, refresh_cmd)
                    self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in refresh_cmd)))
                else:
                    power_cmd[3] = value
                    power_cmd[14] = self.ft422_i2c.auo_calculate_SHM_chechsum(power_cmd, 14)
                    self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, power_cmd)
                    self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in power_cmd)))
            
            while (time.perf_counter() - start) < repeat_time:
                pass
        
        ''' Brightness State Get '''
        cmd = bytearray([0xFF, 0xA4, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.02)
        response = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        get_brightness = int(response[0]) + 10
        
        if (repeat_time <= (30/1000)):
            if self.ui.checkBox_2nd_refresh.isChecked():
                result = 'OK' if (get_brightness) == int(brightness[1] * 10) else 'NG'
            else:
                result = 'OK' if (get_brightness) == int(brightness[0] * 10) else 'NG'
        else:
            result = 'OK' if (get_brightness) == int(brightness[1] * 10) else 'NG'

        if (result == 'OK'):
            self.ui.continue_brightness_label.setStyleSheet("color:green")
            self.continue_test_ok = self.continue_test_ok + 1
        elif(result == 'NG'):
            self.ui.continue_brightness_label.setStyleSheet("color:red")
            self.continue_test_ng = self.continue_test_ng + 1
        self.ui.continue_brightness_label.setText("Brightness Step: %d, Result: %s \n Total: %d, OK: %d, NG: %d." % (get_brightness, result, self.continue_test_total, self.continue_test_ok, self.continue_test_ng))
        self.outputChanged.emit("Brightness read: %d, Result: %s" % (get_brightness, result))

    def GPSTime_Config_Set(self):
        if (self.ui.checkBox_gpstime.isChecked()):
            self._config_GPSTime = True
        else:
            self._config_GPSTime = False

    def GPSTimeCmd_Process(self):
        ''' GPS Time Command '''
        # create command: [0x1A, year, month, day, hour, minute, second]
        cmd = bytearray([0x1A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # get current time
        now = datetime.now()
        # set command value
        cmd[1] = now.year - 2000
        cmd[2] = now.month
        cmd[3] = now.day
        cmd[4] = now.hour
        cmd[5] = now.minute
        cmd[6] = now.second
        # cal checksum
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 7))
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def VideoMuteCmd_Process(self): 
        ''' VideoMute Command '''
        cmd = bytearray([0x19, 0x00, 0x00, 0x00, 0x00])
        # # check mute state
        if (self.ui.checkBox_mute.isChecked()):
            cmd[1] = 0x01
        else: 
            cmd[1] = 0x00            
        # cal checksum 
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 5))
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Update_Test_WrongOrder(self): 
        if (self.ui.checkBox_update_wrongorder.isChecked()): 
            self.ft422_i2c.setWrongOrder(True)
        else: 
            self.ft422_i2c.setWrongOrder(False)
            
    def Update_Test_Length_Exceed(self):
        if (self.ui.checkBox_update_datalenexceed.isChecked()): 
            self.ft422_i2c.setLenExceed(True)
        else: 
            self.ft422_i2c.setLenExceed(False)
            
    def Update_Test_Length_Short(self):
        if (self.ui.checkBox_update_datalenless.isChecked()): 
            self.ft422_i2c.setLenLess(True)
        else: 
            self.ft422_i2c.setLenLess(False)
            
    def Update_Test_FragOffset_Error(self):
        if (self.ui.checkBox_update_fragerror.isChecked()): 
            self.ft422_i2c.setFragment(True)
        else: 
            self.ft422_i2c.setFragment(False)
            
    def Update_Test_Header_Error(self):
        if (self.ui.checkBox_update_FileHeader.isChecked()): 
            self.ft422_i2c.setFileHeader(True)
        else: 
            self.ft422_i2c.setFileHeader(False)
            
    def Update_Test_Header_Frag_Error(self):
        if (self.ui.checkBox_update_FileHeader_FragErr.isChecked()):
            self.ft422_i2c.setFileHeaderFragment(True)
        else:
            self.ft422_i2c.setFileHeaderFragment(False)
            
    def Update_Test_Header_Length_Error(self):
        if (self.ui.checkBox_update_FileHeader_length.isChecked()):
            self.ft422_i2c.setFileHeaderLength(True)
        else:
            self.ft422_i2c.setFileHeaderLength(False)
            
    def Update_Test_Header_Checksum_Error(self):
        if (self.ui.checkBox_update_FileHeader_checksum.isChecked()):
            self.ft422_i2c.setFileHeaderChecksum(True)
        else:
            self.ft422_i2c.setFileHeaderChecksum(False)
    
    def SupervisionFrame_Switch(self):
        if(self.ui.checkBox_SuperFrame.isChecked()):
            #thread start
            # print("thread start")
            self.ui.textBrowser.clear()
            self._Supervision_thread_flag = True
            self.Supervision_thread.start()
        else: 
            #thread stop
            # print("thread stop")
            self._Supervision_thread_flag = False
            self.ui.connectstate.setText("Connect Status")
        
    def SupervisionFrameCmd_Process(self):
        while self._Supervision_thread_flag: 
            #define Command 
            cmd = bytearray([0x3C])
            # cal checksum 
            # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
            # print("serdes write: %s" % (' '.join('{:02X}'.format(x) for x in cmd)))
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            state = self.ft422_i2c.read(self.remote_addr, cmd, 1)
            if (state == b'\xA5'):
                self.ui.connectstate.setText("Connected.")
            else: 
                self.ui.connectstate.setText("Disconnect.")
            # print("Supervision Get ", state)
            self.outputChanged.emit("Supervision Get %s"%(state))
            time.sleep(0.5)

    def VersionCmd_Process(self): 
        #define Command 
        cmd = bytearray([0x30])
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
        self.outputChanged.emit("serdes write(0x%02X): %s" % (self.remote_addr, ' '.join('0x{:02X}'.format(x) for x in cmd)))
        state = self.ft422_i2c.read(self.remote_addr, cmd, 16)
        try:
            if state and len(state) == 16:
                self.ui.label_versiondata.setText(' '.join('{:02X}'.format(x) for x in state))
                self.ui.lable_HWVersion.setText("%02X %02X"%(state[0], state[1]))
                self.ui.lable_SWVersion.setText("%02X %02X"%(state[2], state[3]))
                self.ui.lable_EEPROMVersion.setText("%02X %02X"%(state[8], state[9]))
                self.ui.lable_TCONVersion.setText("%02X %02X"%(state[12], state[13]))
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
            else:
                self.outputChanged.emit("Error read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        except Exception as e:
            self.outputChanged.emit("Error read: %s" % (e + ' '.join('0x{:02X}'.format(x) for x in state)))

    def IdentificationCmd_Process(self):
        #define Command 
        cmd = bytearray([0x31])
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        state = self.ft422_i2c.read(self.remote_addr, cmd, 30)
        self.ui.label_id.setText(' '.join('{:02X}'.format(x) for x in state))
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        
        # main no.
        self.ui.label_ID_main_data.setText(' '.join('{:02X}'.format(x) for x in state[0:5])) 
        
        # Parts no.
        self.ui.label_ID_parts_data.setText(' '.join('{:02X}'.format(x) for x in state[5:8]))
        
        # identification no.
        self.ui.label_ID_id_data.setText(' '.join('{:02X}'.format(x) for x in state[8:12]))
        
        # amendment no.
        self.ui.label_ID_amendment_data.setText(' '.join('{:02X}'.format(x) for x in state[12:14]))
        
        # serial no. 
        self.ui.label_ID_serial_data.setText(' '.join('{:02X}'.format(x) for x in state[22:26]))
        
        # year/date.  
        self.ui.label_ID_date_data.setText(' '.join('{:02X}'.format(x) for x in state[18:22]))

    def Cuation_Popup(self, str):
        mbox = QtWidgets.QMessageBox(self.ui.centralwidget)
        mbox.setText('Received Interrupt Message.\n' + "ID & Length: " + str)
        mbox.setIcon(3)
        mbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mbox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        return mbox.exec_()
    
    def Update_Popup(self): 
        mbox = QtWidgets.QMessageBox(self.ui.centralwidget)
        mbox.setText('                         Caution !!\n This will update machine\'s Firmware.')
        mbox.setIcon(3)
        mbox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Yes)
        mbox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        return mbox.exec_()
    
    def UpdateCmd_SelectFile(self):
        filename, filetype = QFileDialog.getOpenFileName(self, 'Open Update File', os.getcwd(), 'Supported Files (*.bin *.design_hex_rom);;All Files (*)')
        
        if not filename:    # 未選擇檔案
            return
        
        ### Application File
        if (self.ui.tabWidget_3.currentIndex() == 0):
            self._userFile = filename # 儲存選擇檔案
            if fnmatch.fnmatch(os.path.basename(self._userFile), "*_USER.bin"):
                self.ui.label_file.setText(os.path.basename(self._userFile))
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid file. Please select *_USER.bin file."))
                self._userFile = ""
                
        ### TCON File
        elif (self.ui.tabWidget_3.currentIndex() == 2):
            self._tconFile = filename # 儲存選擇檔案
            if fnmatch.fnmatch(os.path.basename(self._tconFile), "C300_1392x162_Realchip_*.bin"):
                self.ui.label_file_tcon.setText(os.path.basename(self._tconFile))
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid file. Please select C300_1392x162_Realchip_*.bin file."))
                self._tconFile = ""
        
        ### DeMURA File
        elif (self.ui.tabWidget_3.currentIndex() == 3):
            self._demuraFile = filename # 儲存選擇檔案
            if fnmatch.fnmatch(os.path.basename(self._demuraFile), "*rom"):
                self.ui.label_file_demura.setText(os.path.basename(self._demuraFile))
                binfile = io.BytesIO(bytearray(self.ft422_i2c.parse_memory_file(self._demuraFile)))
                binfile_size = len(binfile.getvalue())
                print("File Size: ", binfile_size)
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid file. Please select *rom file."))
                self._demuraFile = ""
                
        ### progress bar
        self.ui.progressBar.setValue(0)
                
    def UpdateStop_Process(self):
        self.update_thread_flag = False
        self.update_thread.terminate()
        self.update_thread.wait()
        
        while self.update_thread.isRunning():
            time.sleep(0.1)
        
        self.ui.progressBar.setValue(0)
        self.ui.UpdatingFile_label.setText("Updating File :")
        self.ui.GetFile_Btn.setEnabled(True)
        self.ui.UpdateUser_Btn.setEnabled(True)  
    
    def UpdateCmd_Process(self):
        
        if (self.ui.tabWidget_3.currentIndex() == 0):
            ''' MCU User Firmware Update '''
            if not hasattr(self, "_userFile") or not self._userFile:
                self.outputChanged.emit(self._Textbrowser_Color(1, "No file selected. Please choose a file first."))
                return
            
            if fnmatch.fnmatch(os.path.basename(self._userFile), "*_USER.bin"):
                if (self.Update_Popup() == QtWidgets.QMessageBox.Yes):
                    self.gmsllink_thread_flag = False
                    self._Supervision_thread_flag = False
                    self.ui.textBrowser.clear()
                    self.ui.checkBox_SuperFrame.setChecked(False)      
                    self.ft422_i2c.auo_shm_update_file(self._userFile)
                    self.update_thread.start()
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, " Please Select *_USER.bin file."))
        
        elif (self.ui.tabWidget_3.currentIndex() == 2):
            ''' TCON Firmware Update '''
            if not hasattr(self, "_tconFile") or not self._tconFile:
                self.outputChanged.emit(self._Textbrowser_Color(1, "No file selected. Please choose a file first."))
                return
                      
            if fnmatch.fnmatch(os.path.basename(self._tconFile), "C300_1392x162_Realchip_*.bin"):
                if (self.Update_Popup() == QtWidgets.QMessageBox.Yes):
                    self.gmsllink_thread_flag = False
                    self._Supervision_thread_flag = False
                    self.ui.textBrowser.clear()
                    self.ui.checkBox_SuperFrame.setChecked(False)      
                    self.ft422_i2c.auo_shm_update_file(self._tconFile)
                    self.update_thread.start()
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, " Please Select C300_1392x162_Realchip_*.bin file."))
        
        elif (self.ui.tabWidget_3.currentIndex() == 3):
            ''' DeMURA Firmware Update '''
            if not hasattr(self, "_demuraFile") or not self._demuraFile:
                self.outputChanged.emit(self._Textbrowser_Color(1, "No file selected. Please choose a file first."))
                return
                      
            if fnmatch.fnmatch(os.path.basename(self._demuraFile), "*rom"):
                if (self.Update_Popup() == QtWidgets.QMessageBox.Yes):
                    self.gmsllink_thread_flag = False
                    self._Supervision_thread_flag = False
                    self.ui.textBrowser.clear()
                    self.ui.checkBox_SuperFrame.setChecked(False)      
                    self.ft422_i2c.auo_shm_update_file(self._demuraFile)
                    self.update_thread.start()
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, " Please Select DeMURA_*rom file."))
                
    ## Get Updater, Boot and User file
    def _Get_UpdaterFile(self):
        folder_path = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder_path:
            self.ui.label_folder.setText(f"Selected Folder : {folder_path}")  # 更新顯示資料夾路徑
            patterns = {
                "updater": re.compile(r"CN30UYX0\d\.0_U\.\d+\.\d+\.\d+_UPDATER\.bin"),
                "boot": re.compile(r"CN30UYX0\d\.0_B\.\d+\.\d+\.\d+_BOOT\.bin"),
                "application": re.compile(r"CN30UYX0\d\.0_T\.\d+\.\d+\.\d+_USER\.bin")
            }
            found_files = {"updater": "None", "boot": "None", "application": "None"}
            
            # 使用 os.walk() 遞迴搜尋所有子目錄
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    for key, pattern in patterns.items():
                        if pattern.match(file_name):
                            found_files[key] = os.path.join(root, file_name)
            
            self.ui.UpdaterFile_label.setText(os.path.basename(found_files["updater"]))
            self.ui.BootFile_label.setText(os.path.basename(found_files["boot"]))
            self.ui.AppFile_label.setText(os.path.basename(found_files["application"]))
            self._updaterFile = found_files["updater"]
            self._bootFile = found_files["boot"]
            self._userFile = found_files["application"]
            
            if all(value != "None" for value in found_files.values()):
                pass
            else:
                self.outputChanged.emit(self._Textbrowser_Color(1, " Please check has select Updater, Boot and User file."))
             
    def _MCU_Update(self): 
        if self.ui.UpdaterFile_label.text() != "None" and self.ui.BootFile_label.text() != "None" and self.ui.AppFile_label.text() != "None": 
            self.outputChanged.emit(self._Textbrowser_Color(4, " Already have select Updater, Boot and User file."))
            if (self.Update_Popup() == QtWidgets.QMessageBox.Yes):
                self.gmsllink_thread_flag = False
                self._Supervision_thread_flag = False
                self.ui.textBrowser.clear()
                self.ft422_i2c.auo_shm_update_file(self._updaterFile)
                self.update_thread.start()            
        else:
            self.outputChanged.emit(self._Textbrowser_Color(1, " Please check has select Updater, Boot and User file."))
        
    def StatusCmd_Process(self):
        #define Command 
        cmd = bytearray([0x88])
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))

        state = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        try:
            if state and len(state) == 2:
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
                self.ui.label_StatusCmd.setText(' '.join('{:02X}'.format(x) for x in state))
                if((state[0]&0x80)==0):
                    self.ui.label_tempprotect.setText('OK')
                else:
                    self.ui.label_tempprotect.setText('NG')
                    
                if((state[0]&0x20)==0):
                    self.ui.label_displaystatus.setText('Displayed')
                else:
                    self.ui.label_displaystatus.setText('Can not Display')
                    
                if((state[0]&0x10)==0):
                    self.ui.label_centerdisplaymute.setText('OFF')
                else:
                    self.ui.label_centerdisplaymute.setText('ON')
            else:
                self.outputChanged.emit("Error read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        except Exception as e:
            self.outputChanged.emit("Error read: %s" % (e + ' '.join('0x{:02X}'.format(x) for x in state))) 
            
        return state   

    def DianosisStatusCmd_Process(self):
        #define Command 
        cmd = bytearray([0x6C])
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd))) 
        state = self.ft422_i2c.read(self.remote_addr, cmd, 27)
        try:
            if state and len(state) == 27:
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        
                # Product ID(Serial Number)
                self.ui.label_Dia_PID.setText(' '.join('{:02X}'.format(x) for x in state[0:4]))
    
                # lvds ic 
                if(state[8]&0x80):
                    # self.ui.label_Dia_LVDSIC.setStyleSheet("color:red")
                    self.ui.label_Dia_LVDSIC.setText("NG")
                else:
                    # self.ui.label_Dia_LVDSIC.setStyleSheet("color:black")
                    self.ui.label_Dia_LVDSIC.setText("OK")
            
                # EEPROM
                if (state[8]&0x08):
                    # self.ui.label_Dia_EEPROM.setStyleSheet("color:red")
                    self.ui.label_Dia_EEPROM.setText("NG")
                else:
                    # self.ui.label_Dia_EEPROM.setStyleSheet("color:black")
                    self.ui.label_Dia_EEPROM.setText("OK")
            
                # Power circuit 
                if (state[8]&0x02):
                    # self.ui.label_Dia_Power.setStyleSheet("color:red")
                    self.ui.label_Dia_Power.setText("NG")
                else: 
                    # self.ui.label_Dia_Power.setStyleSheet("color:black")
                    self.ui.label_Dia_Power.setText("OK")
                    
                # LVDS Connection 
                if (state[9]&0x80): 
                    # self.ui.label_Dia_LVDSConnect.setStyleSheet("color:red")
                    self.ui.label_Dia_LVDSConnect.setText("NG")
                else:
                    # self.ui.label_Dia_LVDSConnect.setStyleSheet("color:black")
                    self.ui.label_Dia_LVDSConnect.setText("OK")
        
                # Derating 
                if (state[9]&0x20): 
                    # self.ui.label_Dia_Derating.setStyleSheet("color:red")
                    self.ui.label_Dia_Derating.setText("De-rating")
                else: 
                    # self.ui.label_Dia_Derating.setStyleSheet("color:black")
                    self.ui.label_Dia_Derating.setText("OK")
            
                # Battery 
                if (state[9]&0x10):
                    # self.ui.label_Dia_Battery.setStyleSheet("color:red")
                    self.ui.label_Dia_Battery.setText("6-9V")
                else: 
                    # self.ui.label_Dia_Battery.setStyleSheet("color:black")
                    self.ui.label_Dia_Battery.setText("OK")
            
                # TCON IC
                if (state[9]&0x08):
                    # self.ui.label_Dia_TCONIC.setStyleSheet("color:red")
                    self.ui.label_Dia_TCONIC.setText("NG")
                else: 
                    # self.ui.label_Dia_TCONIC.setStyleSheet("color:black")
                    self.ui.label_Dia_TCONIC.setText("OK")
                
                # TCON GOA
                if (state[9]&0x02):
                    # self.ui.label_Dia_TCONGOA.setStyleSheet("color:red")
                    self.ui.label_Dia_TCONGOA.setText("NG")
                else: 
                    # self.ui.label_Dia_TCONGOA.setStyleSheet("color:black")
                    self.ui.label_Dia_TCONGOA.setText("OK")
                
                # TCON COF
                if (state[9]&0x01):
                    # self.ui.label_Dia_TCONCOF.setStyleSheet("color:red")
                    self.ui.label_Dia_TCONCOF.setText("NG")
                else: 
                    # self.ui.label_Dia_TCONCOF.setStyleSheet("color:black")
                    self.ui.label_Dia_TCONCOF.setText("OK")
            
                # temperature 
                if(state[10]&0x80):
                    sign = '-'
                    value = state[10]-128
                else:
                    sign = '+'
                    value = state[10]
                    
                # AID 
                if (state[16]&0x80):
                    # self.ui.label_Dia_AID.setStyleSheet("color:red")
                    self.ui.label_Dia_AID.setText("Enable")
                else: 
                    # self.ui.label_Dia_AID.setStyleSheet("color:black")
                    self.ui.label_Dia_AID.setText("Disable")
            
                # Illumi Cancel
                if (state[16]&0x40):
                    # self.ui.label_Dia_IllumiCencel.setStyleSheet("color:red")
                    self.ui.label_Dia_IllumiCencel.setText("OFF")
                else: 
                    # self.ui.label_Dia_IllumiCencel.setStyleSheet("color:black")
                    self.ui.label_Dia_IllumiCencel.setText("ON")
                    
                # Day/Night
                if (state[16]&0x08):
                    # self.ui.label_Dia_daynight.setStyleSheet("color:red")
                    self.ui.label_Dia_daynight.setText("Night")
                else: 
                    # self.ui.label_Dia_daynight.setStyleSheet("color:black")
                    self.ui.label_Dia_daynight.setText("Day")

                # LCD ON/OFF
                if (state[16]&0x04):
                    # self.ui.label_Dia_lcd.setStyleSheet("color:red")
                    self.ui.label_Dia_lcd.setText("OFF")
                else: 
                    # self.ui.label_Dia_lcd.setStyleSheet("color:black")
                    self.ui.label_Dia_lcd.setText("ON")

                # Illumination Step 
                if (state[17] == 0xFF):
                    # self.ui.label_Dia_IllumiStep.setStyleSheet("color:red")
                    self.ui.label_Dia_IllumiStep.setText("0xFF")
                else: 
                    # self.ui.label_Dia_IllumiStep.setStyleSheet("color:black")
                    self.ui.label_Dia_IllumiStep.setText("%d"%(state[17]))   
                
                # Brightness Step 
                if (state[18] == 0xFF):
                    # self.ui.label_Dia_BrightnessStep.setStyleSheet("color:red")
                    self.ui.label_Dia_BrightnessStep.setText("0xFF")
                else: 
                    # self.ui.label_Dia_BrightnessStep.setStyleSheet("color:black")
                    self.ui.label_Dia_BrightnessStep.setText("%d"%(state[18]))    
                    
                # Brightness Step 
                if (state[19] == 0xFF):
                    # self.ui.label_Dia_BacklightStep.setStyleSheet("color:red")
                    self.ui.label_Dia_BacklightStep.setText("0xFF")
                else: 
                    # self.ui.label_Dia_BacklightStep.setStyleSheet("color:black")
                    self.ui.label_Dia_BacklightStep.setText("%d"%(state[19]))  
            
                self.ui.label_Dia_Temp.setText("%c%02d °C"%(sign, value))
                self.ui.label_Dianosis.setText(' '.join('{:02X}'.format(x) for x in state))
            else:
                self.outputChanged.emit("Error read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        except Exception as e:
            self.outputChanged.emit("Error read: %s" % (e + ' '.join('0x{:02X}'.format(x) for x in state)))
        
    def RefershCmd_Process(self): 
        # define Command 
        cmd = bytearray([0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\
                                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, \
                                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        # check AID checkbox state 
        if(self.ui.checkBox_ref_aid.isChecked()): 
            # print("aid is checked")
            cmd[17] = cmd[17] | 0x80
        else: 
            # print("aid not be checked")
            cmd[17] = cmd[17] & 0x7F
            
        # check day/night mode state
        if (self.ui.checkBox_ref_daymode.isChecked()): 
            # print("Night Mode")
            cmd[17] = cmd[17] | 0x08
        else:
            # print("day mode")
            cmd[17] = cmd[17] & 0xF7
            
        # check LCD On/OFF state
        if (self.ui.checkBox_ref_LCD.isChecked()):
            # print("LCD ON")
            cmd[17] = cmd[17] & 0xFB
        else: 
            # print("LCD Off")
            cmd[17] = cmd[17] | 0x04
            
        # get Illumination control step index 
        value = self.ui.comboBox_4.currentText()
        if (int(value, 16) == 255):
            cmd[18] = 255
        else:
            cmd[18] = int(value)
        # print("Illumination Step: " , cmd[18])
        
        # get Brightness control step index 
        value = self.ui.comboBox_5.currentText().strip() # remove space
        try: 
            if value.startswith('0x') or value.startswith('0X'): # check if the string starts with '0x' or '0X'
                num_value = int(value, 16)  # convert the string to a hexadecimal number
            elif value.isdigit():
                num_value = int(value)
            else:
                raise ValueError(f"Invalid value: {value}") # raise an exception if the string is not a valid number
            
            if (num_value == 255):
                cmd[19] = 255
            else:
                cmd[19] = num_value
        except ValueError as e:
            self.outputChanged.emit(f"Error: {e}")  
        
        # get Back light luminance control step text
        value_low_str = self.ui.comboBox_6.currentText().strip() # remove space
        value_high_str = self.ui.comboBox_10.currentText().strip() # remove space
        try:
            num_value_low = int(value_low_str, 0)
            num_value_high = int(value_high_str, 0)
            
            if not (0 <= num_value_low <= 255) or not (0 <= num_value_high <= 255):
                raise ValueError(f"Invalid value: {value_low_str} or {value_high_str}")
            
            cmd[20] = 255 if (num_value_low == 255) else num_value_low
            cmd[21] = 255 if (num_value_high == 255) else num_value_high
        
        except ValueError as e:
            self.outputChanged.emit(f"Error: {e}")
        
        # cal checksum 
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 29))
        
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)        

    def ReportIDCmd_Process(self):
        #define Command 
        cmd = bytearray([0x9C])
        
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
            
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            
        state = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        self.ui.label_reportID.setText(' '.join('{:02X}'.format(x) for x in state))
        
        self.ui.label_CmdID.setText("0x%02X"%(state[0]))
        self.ui.label_DataLen.setText("0x%02X"%(state[1]))
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        
        if state[0] == 0x6C:
            self.DianosisStatusCmd_Process()
        elif state[0] == 0x88:
            self.StatusCmd_Process()
        elif state[0] == 0x9D:
            self.DisplayStatusCmd_Process()
            
        return state
        
    def DisplayStatusCmd_Process(self):
        #define Command 
        cmd = bytearray([0x9D])
        
        # cal checksum 
        # cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 1))
            
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            
        state = self.ft422_i2c.read(self.remote_addr, cmd, 1)
        self.ui.label_DisplayStatus.setText(' '.join('{:02X}'.format(x) for x in state))
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in state)))
        
        return state
        
    def Engineer_Refresh(self):
        if(self.ui.checkBox_3.isChecked()):
            self.Engineer_Aging_Get()       # 1
            time.sleep(100/1000)
            self.Engineer_Battery_Voltage_Get() # 2
            time.sleep(100/1000)
            self.Engineer_PCBA_Version_Get()    # 4
            time.sleep(100/1000)
            self.Engineer_TCON_Version_Get()    # 5
            time.sleep(100/1000)
            self.Engineer_User_Version_Get()    # 6
            time.sleep(100/1000)
            self.Engineer_Boot_Version_Get()    # 7 
            time.sleep(100/1000)
            self.Engineer_PID_Get()             # 8
            time.sleep(100/1000)
            self.Engineer_Thermal_Get()         # 9        
            time.sleep(100/1000)
            self.Engineer_Diagnosis_Get()       # A
            time.sleep(100/1000)
            self.Engineer_Serdes_State_Get()    # B
            time.sleep(100/1000)
            self.Engineer_TCON_State_Get()      # C
            time.sleep(100/1000)
            self.Engineer_Sensors_Get()         # D
            time.sleep(100/1000)
            self.Engineer_Derating_Get()
            time.sleep(100/1000)
            self.Engineer_Derating_Curve_Get()
            time.sleep(100/1000)
            self.Engineer_Demura_Get()
            time.sleep(100/1000)
            self.Engineer_TC_Get()
            time.sleep(100/1000)
            self.Engineer_Brightness_Get()   
            time.sleep(100/1000)
            self.Engineer_RCN_Get()
            time.sleep(100/1000)
            self.Engineer_mcu_crc_get()
            time.sleep(100/1000)
            self.Engineer_cross_pattern_get()
                
        self.Engineer_TXB_Voltage_Get()
        time.sleep(100/1000)
        self.Engineer_TXB_Current_Get()
    
    ## Engineer Function ###
    def Engineer_Aging_Set(self):
        ''' Aging state Set '''
        cmd = bytearray([0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        if (self.ui.checkBox_2.isChecked()):
            cmd[2] = 0x00
        else: 
            cmd[2] = 0x02
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_Aging_Get(self):
        ''' Aging State Get '''
        cmd = bytearray([0xFF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.01)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0x00):
            self.ui.label_AgainSt.setText("Start")
        elif (result[0] == 0x02):
            self.ui.label_AgainSt.setText("Stop")
        
    def Engineer_Battery_Voltage_Get(self): 
        ''' Battery voltage Get '''
        cmd = bytearray([0xFF, 0x02, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        output = "%02X.%d%02XV"%(result[0], result[1], result[2])
        self.ui.label_BatterVol.setText(output)  
        
    def Engineer_BackLight_Set(self): 
        ''' Backlight set '''        
        if (not self.ui.checkBox_4.isChecked()):
            cmd = bytearray([0xFF, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            index = int(self.ui.comboBox_8.currentText())
            hundreds = index // 100
            tens = (index % 100) // 10
            digital = int(index % 10)
            value = (tens << 4) | digital
            cmd[2] = hundreds
            cmd[3] = value
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_PCBA_Version_Get(self): 
        ''' PCBA Version Get '''
        cmd = bytearray([0xFF, 0x04, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        self.ui.label_PCBA_Ver.setText("%c%02X"%(result[0], result[1]))
        
    def Engineer_TCON_Version_Get(self): 
        ''' TCON Version Get '''
        cmd = bytearray([0xFF, 0x05, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        self.ui.label_TCON_Ver.setText("%02X%02X%02X"%(result[0], result[1], result[2]))
        
    def Engineer_User_Version_Get(self):
        ''' MUC User Version Get '''
        cmd = bytearray([0xFF, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5+12)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        date_text = ''.join(chr(c) for c in result[6:18] if c != 0x00) if len(result) >= 6 else ''
        if date_text:
            self.ui.label_User_Ver.setText("%c%01X%01X, %s"%(result[0], result[1], result[2], date_text))
        else:
            self.ui.label_User_Ver.setText("%c%01X%01X"%(result[0], result[1], result[2]))

    def Engineer_Boot_Version_Get(self):
        ''' MCU Boot Version Get '''
        cmd = bytearray([0xFF, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        output = "%c%01X%02X"%(result[0], result[1], result[2])
        self.ui.label_Boot_Ver.setText(output)   
        
    def Engineer_PID_Get(self):
        cmd = bytearray([0xFF, 0x08, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 32)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        # self.ui.label_Part_No.setText("%c%c%c%c%c%c"%(result[0], result[1], result[2], result[3], result[4], result[5]))
        self.ui.label_Part_No.setText("%c%c%c%c%c%c%c%c%c%c%c"%(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10]))
        
    def Engineer_Thermal_Get(self): 
        '''Get Thermal from RX'''
        # set command 
        cmd = bytearray([0xFF, 0x09, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # print command data to textbrowser 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # sent command out to RX 
        result = bytearray(self.ft422_i2c.read(self.remote_addr, cmd, 5))
        # print Receive Data to textbrowser 
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if(result[0]&0x80):
            sign = '-'
        else:
            sign = '+'
        # result[1] = 0x85
        # result[2] = 0x00
        # result[3] = 0x41
        # result[4] = 0x95
        output = "%X%02X°C, %X.%02X%02XV"%(result[0]&0x0F, result[1], result[2], result[3], result[4])
        self.ui.label_NTC.setText(sign+output)
        
    def Engineer_Diagnosis_Get(self):
        ''' Diagnostic Get '''
        cmd = bytearray([0xFF, 0x0A, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        self.ui.label_AgainState.setText("%02X%02X"%(result[0], result[1]))
        
    def Engineer_Serdes_State_Get(self):
        ''' Serdes state Get '''
        cmd = bytearray([0xFF, 0x0B, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0]&0x01):
            self.ui.label_DES_St.setText("NG")
        else:
            self.ui.label_DES_St.setText("OK")
        
    def Engineer_TCON_State_Get(self):
        ''' TCON State Get '''
        cmd = bytearray([0xFF, 0x0C, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0]&0x01): 
            self.ui.label_TCON_St.setText("NG")
        else:
            self.ui.label_TCON_St.setText("OK")       

    def Engineer_I2C_Read_Process(self):
        cmd = bytearray([0xFF, 0x0D, 0x60, 0x00, 0x00, 0xFF, 0xFF])
        try:
            input_str = self.ui.lineEdit_I2CR.text().strip()
            parts = [p.strip() for p in input_str.split(',')]
            if len(parts) != 3:
                raise ValueError("輸入格式錯誤，應為 '位址, 暫存器, 長度' " + str(len(parts)))
            
            device_addr = int(parts[0], 16)
            register_addr = int(parts[1], 16)
            read_length = int(parts[2], 16)
            
            if not (0 <= device_addr <= 0xFF and 0 <= register_addr <= 0xFF):
                raise ValueError("設備位址與暫存器位址必須介於 0x00 和 0xFF 之間")
            if read_length <= 0:
                raise ValueError("讀取長度必須是正數")

            cmd[2] = device_addr
            cmd[3] = register_addr
            cmd[4] = read_length
            self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
            time.sleep(0.1)
            result = self.ft422_i2c.read(self.remote_addr, cmd, read_length)
            self.outputChanged.emit("Read I2C 0x%02X from 0x%02X: %s" % (device_addr, register_addr, ' '.join('0x{:02X}'.format(x) for x in result)))

        except (ValueError, IndexError, TypeError) as e:
            # 6. 如果發生任何錯誤 (格式錯誤、數值轉換失敗等)，在UI上顯示錯誤訊息
            error_message = f"Input Error, Please Check Again!! ({e})"
            self.outputChanged.emit(self._Textbrowser_Color(1, error_message))

    def Engineer_I2C_Write_Process(self):
        ''' Read lineEdit_I2CW command and data '''
        cmd_head = bytearray([0xFF, 0x0E])
        # Read input string from UI.
        input_str = self.ui.lineEdit_I2CW.text()
        
        # Check if input string is empty.
        if not input_str:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Input Error, Please Check again!!."))
            return
        
        try:
            # Split the input string into parts.
            parts = [part.strip() for part in input_str.split(',')]
            # Check if the number of parts is valid.
            if len(parts) < 4:
                raise ValueError("Invalid format. Expected at least 4 parts: 0x[addr],0x[register],0x[length],0x[data]" + str(len(parts)))
            if len(parts) > 5:
                raise ValueError("Invalid format. Expected at most 5 parts: 0x[addr],0x[register],0x[length],0x[data00],0x[data01]")

            # Convert each part to an integer.
            int_value = [int(part, 16) for part in parts]

            # Check if the values are within the valid range.
            device_address = int_value[0]
            register_address = int_value[1]
            data_length = int_value[2]
            data_values = int_value[3:]

            # Check if the data length is correct.
            if len(data_values) != data_length:
                raise ValueError("Data length mismatch. Expected %d bytes, but got %d bytes." % (data_length, len(data_values)))

            # combine command parts
            cmd_payload = bytearray([device_address, register_address, data_length] + data_values)
            cmd = cmd_head + cmd_payload
            # Print command data to textbrowser
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            # Send command to I2C
            self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

        except (ValueError, IndexError, TypeError) as e:
            # 6. 如果發生任何錯誤 (格式錯誤、數值轉換失敗等)，在UI上顯示錯誤訊息
            error_message = f"Input Error, Please Check Again!! ({e})"
            self.outputChanged.emit(self._Textbrowser_Color(1, error_message))
        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Unexpected Error: {e}"))

    def Engineer_I2C_PID_Write_Process(self):
        ''' I2C PID Write '''
        cmd = bytearray([0xFF, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]) 
        
        ### pop up message to confirm clear
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Set Run Card PID',
            'Are you sure you want to set Run Card information?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.No:
            return
        
        input_str = self.ui.textEdit.toPlainText().strip()
        
        if len(input_str) > 11: 
            self.outputChanged.emit(self._Textbrowser_Color(1, "Input Error, only 11 byte, Please Check again!!"))
            return
        
        try: 
            if all(c in "0123456789ABCDEF" for c in input_str) and len(input_str)%2 == 0:
                byte_data = bytes.fromhex(input_str)
            else:
                byte_data = input_str.encode('ascii', 'ignore')
        except ValueError:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid input, please check again!"))
            return
        
        cmd[2:2+len(byte_data)] = byte_data[:11]
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_Sensors_Get(self): 
        '''Get Sensors from RX'''
        # set command 
        cmd = bytearray([0xFF, 0x10, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # print command data to textbrowser 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # sent command out to RX 
        result = self.ft422_i2c.read(self.remote_addr, cmd, 12)
        # print Receive Data to textbrowser 
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        output = "%02d°C, %02d°C, %02d°C, %02d°C"%(result[0]-0x37, result[1]-0x37, result[2]-0x37, result[3]-0x37)
        self.ui.label_Sensors.setText(output)
        self.outputChanged.emit("TCON Temperature: %s" % output)
        self.outputChanged.emit(" Hex: 0x%02X%02X, 0x%02X%02X, 0x%02X%02X, 0x%02X%02X" % (result[4], result[5], result[6], result[7], result[8], result[9], result[10], result[11]))
                
    ### Engineer -- TXB Current ###
    def Engineer_TXB_Current_Get(self): 
        ''' I2C Command '''
        cmd = bytearray([0xFF, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.txb_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0xFF) and (result[1] == 0xFF) and (result[2] == 0xFF) and (result[3] == 0xFF):
            pass
        else:
            if(self.ui.checkBox_3.isChecked()):
                if(result[0] == 0x00) and (result[1] == 0x00):
                    output = "0.%02X%02X"%(result[2], result[3])
                else:
                    if (result[0] == 0x00) and (result[1] != 0x00):
                        output = "%d.%02X%02X"%(result[1], result[2], result[3])
                    else: 
                        output = "%d%02X.%02X%02X"%(result[0], result[1], result[2], result[3])
                output = output + "A"
            else:
                output = "%X%02X.%02X%02X"%(result[0], result[1], result[2], result[3])
                output = output + 'uA'
            self.ui.label_TXBCurrent.setText(output)        
        
        
    def Engineer_TXB_Voltage_Get(self):
        ''' I2C Command '''
        cmd = bytearray([0xFF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # sent out
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        result = self.ft422_i2c.read(self.txb_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0xFF) and (result[1] == 0xFF) and (result[2] == 0xFF) :
            pass
        else:        
            output = "%02X.%02X%02XV"%(result[0], result[1], result[2])
            self.ui.label_TXBVol.setText(output)             

    def Engineer_Derating_Set(self):
        ''' Aging state Set '''
        cmd = bytearray([0xFF, 0x20, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        if (self.ui.checkBox_derating.isChecked()):
            cmd[2] = 0x01
        else: 
            cmd[2] = 0x00
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_Derating_Get(self):
        ''' Aging State Get '''
        cmd = bytearray([0xFF, 0x21, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.01)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0x00):
            self.ui.checkBox_derating.setChecked(False)
        elif (result[0] == 0x01):
            self.ui.checkBox_derating.setChecked(True)
            
            
    def Engineer_Derating_Curve_Set(self):
        ''' Aging State Get '''
        cmd = bytearray([0xFF, 0x22, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        temp1 = self.ui.lineEdit_Derating_temp1.text().strip()
        temp2 = self.ui.lineEdit_Derating_temp2.text().strip()
        try:
            cmd[2] = int(temp1, 10)
            cmd[3] = int(temp2, 10)
        except ValueError:
            self.outputChanged.emit("Error: Input is not a number.")

        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

    def Engineer_Derating_Curve_Get(self):
        ''' Aging State Get '''
        cmd = bytearray([0xFF, 0x23, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.01)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        self.ui.lineEdit_Derating_temp1.setText(str(result[0]))
        self.ui.lineEdit_Derating_temp2.setText(str(result[1]))
        
    def Engineer_Derating_NTC_ADC_Set(self):
        ''' Set NTC ADC Value by Temperature'''
        cmd = bytearray([0xFF, 0x24, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        
        # get checkBox_fake_NTC status, if checked, change cmd[2] to 0x01, else 0x00
        if self.ui.checkBox_fake_NTC.isChecked():
            cmd[2] = 0x01
        else: 
            cmd[2] = 0x00
        
        # If the checkbox is checked, get the temperature from the line edit and convert it to an ADC value
        if self.ui.checkBox_fake_NTC.isChecked():
            temp_str = self.ui.lineEdit_Fake_ADC.text().strip()
            try:
                # Convert the input string to an integer temperature
                temperature = int(temp_str)
                
                # Look up the ADC value from the map
                if temperature in TEMP_TO_ADC_MAP:
                    adc_value = TEMP_TO_ADC_MAP[temperature]
                    self.outputChanged.emit(f"Temperature {temperature}°C converted to ADC value: {adc_value} (0x{adc_value:04X})")
                else:
                    # If temperature is not in the map, raise a KeyError to be caught below
                    raise KeyError(f"Temperature {temperature}°C not found in the conversion table.")

                # Split the 16-bit ADC value into two bytes (high and low)
                adc_low = adc_value & 0xFF        # Lower byte (bits 0-7)
                adc_high = (adc_value >> 8) & 0xFF  # Higher byte (bits 8-15)

                cmd[3] = adc_low
                cmd[4] = adc_high
            except (ValueError, KeyError) as e:
                # Catch errors from int() conversion or map lookup
                error_message = f"Invalid input: '{temp_str}'. {e}"
                if isinstance(e, ValueError):
                    error_message = f"Invalid temperature: '{temp_str}'. Please enter a valid integer temperature (e.g. 25, -10)."
                
                self.outputChanged.emit(self._Textbrowser_Color(1, error_message))
                return # Stop execution if the input is invalid
        
        # send cmd out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_Demura_Set(self):
        ''' Demura State Get '''
        cmd = bytearray([0xFF, 0xA0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        if (self.ui.checkBox_Demura.isChecked()):
            cmd[2] = 0x01
        else: 
            cmd[2] = 0x00
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_Demura_Get(self):
        ''' Demura State Get '''
        cmd = bytearray([0xFF, 0xA1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.02)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0x00):
            self.ui.checkBox_Demura.setChecked(False)
        elif (result[0] == 0x01):
            self.ui.checkBox_Demura.setChecked(True)

    def Engineer_TC_Set(self):
        ''' TC State Get '''
        cmd = bytearray([0xFF, 0xA2, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        if (self.ui.checkBox_TC.isChecked()):
            cmd[2] = 0x01
        else: 
            cmd[2] = 0x00
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_TC_Get(self):
        ''' TC State Get '''
        cmd = bytearray([0xFF, 0xA3, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.02)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0x00):
            self.ui.checkBox_TC.setChecked(False)
        elif (result[0] == 0x01):
            self.ui.checkBox_TC.setChecked(True)

    def Engineer_Brightness_Get(self):
        ''' Brightness State Get '''
        cmd = bytearray([0xFF, 0xA4, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.02)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        self.ui.brightness_label.setText("%d%%"%(result[0]))
        
    def Engineer_TCON_Flash_Get(self):
        index = self.ui.comboBox_11.currentIndex()
        self.outputChanged.emit(f"Selected index: {index}")
        if (index == 0):
            self.TCONFlashDataGetFlag = False
        elif(index == 1):
            self.Engineer_AG_Data_Get()
            self.TCONFlashDataGetFlag = True
        elif(index == 2):
            self.Engineer_AG_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 3):
            self.Engineer_DGTable_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 4):
            self.Engineer_DGTable_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 5):
            self.Engineer_RCN_1_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 6):
            self.Engineer_RCN_1_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 7):
            self.Engineer_RCN_2_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 8):
            self.Engineer_RCN_2_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 9):
            self.Engineer_DMC_1_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 10):
            self.Engineer_DMC_1_checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 11):
            self.Engineer_DMC_2_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 12):
            self.Engineer_DMC_2_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 13):
            self.Engineer_DMC_3_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 14):
            self.Engineer_DMC_3_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 15):
            self.Engineer_THERMAL_1_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 16):
            self.Engineer_THERMAL_1_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 17):
            self.Engineer_THERMAL_2_data_Get()
            self.TCONFlashDataGetFlag = True
        elif (index == 18):
            self.Engineer_THERMAL_2_Checksum_Get()
            self.TCONFlashDataGetFlag = True
        
    def Engineer_AG_Data_Get(self):
        ''' AG Data Get raw data '''
        self.outputChanged.emit("Starting AG data get.")
        checksum = 0
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB2, 0x00, 0x00, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.05)
        read_data = self.ft422_i2c.read(self.remote_addr, cmd, 256)
        self.outputChanged.emit("serdes read: ")
        for i in range(0, len(read_data), 16):
            line = ''.join(f' 0x{x:02X}' for x in read_data[i:i+16])
            self.outputChanged.emit(line)
            
        # Calculate Checksum 
        checksum += sum(read_data[:45]) # 
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"calculated checksum (0x{checksum:04X}): ")
        
        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("AG_data.bin", "wb") as f:
                    f.write(read_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "Analog Gamma data saved to AG_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save Analog Gamma data to file: {e}"))        
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result        
            
    def Engineer_AG_Checksum_Get(self):            
        ''' AG Checksum get '''
        self.outputChanged.emit("Starting AG checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB2, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit(f"serdes read checksum : ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
            
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_ag_crc.setText(f"{result[1]:02X}{result[0]:02X}")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result
        
    def Engineer_DGTable_Get(self):
        ''' DGTable State Get '''
        self.outputChanged.emit("Starting DGTable data get.")
        start_time = time.time()
        checksum = 0
        cmd = bytearray([0xFF, 0xB3, 0x00, 0x00, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.05)
        read_data = self.ft422_i2c.read(self.remote_addr, cmd, 256)
        self.outputChanged.emit("serdes read: ")
        for i in range(0, len(read_data), 16):
            line = ''.join(f' 0x{x:02X}' for x in read_data[i:i+16]) 
            self.outputChanged.emit(line)
        # self.ui.comboBox_8.setCurrentIndex(result[0])
        
        # Calculate Checksum
        checksum += sum(read_data[:192])
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"calculated checksum (0x{checksum:04X}): ")
        
        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("DG_data.bin", "wb") as f:
                    f.write(read_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "Digital Gamma data saved to DG_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save Digital Gamma data to file: {e}"))          
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result
        
    def Engineer_DGTable_Checksum_Get(self):
        ''' DG Data Checksum get '''
        self.outputChanged.emit("Starting DGTable checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB3, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_dgc_crc.setText(f"{result[1]:02X}{result[0]:02X}")     
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result    
        
    def Engineer_RCN_1_data_Get(self):
        ''' RCN-1 data Get, start : 0x0000, length : 16384 (0x3FDE) bytes / 256 = 41268 packages.'''
        TOTAL_SIZE = 3398 #16384
        CHUNK_SIZE = 256
        num_blocks = (TOTAL_SIZE + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.outputChanged.emit(f"Starting RCN-1 data get. Total size: {TOTAL_SIZE} bytes, Chunk size: {CHUNK_SIZE} bytes.")
          
        all_data = bytearray()
        checksum = 0
        
        self.TCONFlashDataGetFlag = True
        start_time = time.time()
        try:
            for block in range(num_blocks):
                # Prepare the command
                block_low = block & 0xFF
                block_high = (block >> 8) & 0xFF
                cmd = bytearray([0xFF, 0xB7, block_low, block_high, 0xFF, 0xFF, 0xFF])
                
                # Write the command to the device
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                
                time.sleep(0.1)
                
                # Read the chunk of data
                read_data = self.ft422_i2c.read(self.remote_addr, cmd, CHUNK_SIZE)

                if not read_data:
                    self.outputChanged.emit(self._Textbrowser_Color(1, f"Error reading block {block}. No data received."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time taken: {elapsed_time:.2f} seconds")
                    return
                
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in read_data)))

                if (self.TCONFlashDataGetFlag == False):
                    self.outputChanged.emit(self._Textbrowser_Color(1, "TCON Flash Data Get Flag is False, please check again."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
                    return

                # Handle the last chunk which might be smaller
                if (len(all_data) + len(read_data)) > TOTAL_SIZE:
                    bytes_to_read = TOTAL_SIZE - len(all_data)
                    read_data = read_data[:bytes_to_read]

                all_data.extend(read_data)

                # Report progress every 100 blocks
                if (block + 1) % 100 == 0 or (block + 1) == num_blocks:
                    progress = (len(all_data) / TOTAL_SIZE) * 100
                    self.outputChanged.emit(f"Read block {block+1}/{num_blocks}. Offset: 0x{len(all_data):X}. Progress: {progress:.2f}%")
                    QtWidgets.QApplication.processEvents() # Keep UI responsive

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"An error occurred: {e}"))
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")            
            return

        self.outputChanged.emit("RCN 1 data read complete.")
        
        # cmd = bytearray([0xFF, 0xA9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd) 
        
        # Calculate and display checksum
        checksum_size = TOTAL_SIZE #TOTAL_SIZE = 3398
        checksum = sum(all_data[:checksum_size])  # Exclude the last two bytes for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"Total data received: {len(all_data)} bytes.")
        self.outputChanged.emit(f"Checksum (2 bytes): 0x{checksum:04X}, calculated from first {checksum_size} bytes.")

        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("RCN_1_data.bin", "wb") as f:
                    f.write(all_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "RCN-1 data saved to RCN_1_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save RCN-1 data to file: {e}"))
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_RCN_1_Checksum_Get(self):
        ''' RCN-1 Checksum get '''
        self.outputChanged.emit(f"Starting RCN-1 checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB7, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_rcn_1_crc.setText(f"{result[1]:02X}{result[0]:02X}")  
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_RCN_2_data_Get(self):
        ''' RCN-2 data Get, start : 0x4000, length : 16384 (0x3FDE) bytes / 256 = 64 packages.'''
        TOTAL_SIZE = 3231 #16384
        CHUNK_SIZE = 256
        num_blocks = (TOTAL_SIZE + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.outputChanged.emit(f"Starting RCN-2 data get. Total size: {TOTAL_SIZE} bytes, Chunk size: {CHUNK_SIZE} bytes.")
          
        all_data = bytearray()
        checksum = 0
        
        self.TCONFlashDataGetFlag = True
        start_time = time.time()
        try:
            for block in range(num_blocks):
                # Prepare the command
                block_low = block & 0xFF
                block_high = (block >> 8) & 0xFF
                cmd = bytearray([0xFF, 0xB8, block_low, block_high, 0xFF, 0xFF, 0xFF])
                
                # Write the command to the device
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                
                time.sleep(0.1)
                
                # Read the chunk of data
                read_data = self.ft422_i2c.read(self.remote_addr, cmd, CHUNK_SIZE)

                if not read_data:
                    self.outputChanged.emit(self._Textbrowser_Color(1, f"Error reading block {block}. No data received."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time taken: {elapsed_time:.2f} seconds")
                    return
                
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in read_data)))

                if (self.TCONFlashDataGetFlag == False):
                    self.outputChanged.emit(self._Textbrowser_Color(1, "TCON Flash Data Get Flag is False, please check again."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
                    return

                # Handle the last chunk which might be smaller
                if (len(all_data) + len(read_data)) > TOTAL_SIZE:
                    bytes_to_read = TOTAL_SIZE - len(all_data)
                    read_data = read_data[:bytes_to_read]

                all_data.extend(read_data)

                # Report progress every 100 blocks
                if (block + 1) % 100 == 0 or (block + 1) == num_blocks:
                    progress = (len(all_data) / TOTAL_SIZE) * 100
                    self.outputChanged.emit(f"Read block {block+1}/{num_blocks}. Offset: 0x{len(all_data):X}. Progress: {progress:.2f}%")
                    QtWidgets.QApplication.processEvents() # Keep UI responsive

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"An error occurred: {e}"))
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")            
            return

        self.outputChanged.emit("RCN 2 data read complete.")
        
        # cmd = bytearray([0xFF, 0xA9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd) 
        
        # Calculate and display checksum
        checksum_size = TOTAL_SIZE #TOTAL_SIZE = 3231
        checksum = sum(all_data[:checksum_size])  # Exclude the last two bytes for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"Total data received: {len(all_data)} bytes.")
        self.outputChanged.emit(f"Checksum (2 bytes): 0x{checksum:04X}, calculated from first {checksum_size} bytes.")

        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("RCN_2_data.bin", "wb") as f:
                    f.write(all_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "RCN-2 data saved to RCN_2_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save RCN-2 data to file: {e}"))

        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_RCN_2_Checksum_Get(self):
        ''' RCN-2 Checksum get '''
        self.outputChanged.emit(f"Starting RCN-2 checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB8, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_rcn_2_crc.setText(f"{result[1]:02X}{result[0]:02X}")      
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_DMC_1_data_Get(self):
        ''' DMC-1 data get '''
        self.outputChanged.emit(f"Starting DMC-1 data get.")
        checksum = 0
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB4, 0x00, 0x00, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        read_data = self.ft422_i2c.read(self.remote_addr, cmd, 256)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(read_data), 16):
            line = ''.join(f' 0x{x:02X}' for x in read_data[i:i+16])
            self.outputChanged.emit(line)
            
        checksum = sum(read_data[6:]) # Exclude the first 6 bytes for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"calculated checksum (0x{checksum:04X}): ")            
            
        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("DMC_1_data.bin", "wb") as f:
                    f.write(read_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "DMC LUT 1 data saved to DMC_1_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save DMC LUT 1 data to file: {e}"))              
            
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
            
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_DMC_1_checksum_Get(self):
        ''' DMC-1 Checksum get '''
        self.outputChanged.emit(f"Starting DMC-1 checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB4, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_dmc_1_crc.setText(f"{result[1]:02X}{result[0]:02X}") 
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_DMC_2_data_Get(self):
        ''' DMC-2 data Get, start : 0x900100 , length : 86018 (0x15002) bytes / 256 = 336 packages. '''
        TOTAL_SIZE = 86018
        CHUNK_SIZE = 256
        num_blocks = (TOTAL_SIZE + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.outputChanged.emit(f"Starting DMC-2 data get. Total size: {TOTAL_SIZE} bytes, Chunk size: {CHUNK_SIZE} bytes.")
          
        all_data = bytearray()
        checksum = 0
        
        self.TCONFlashDataGetFlag = True
        start_time = time.time()
        try:
            for block in range(num_blocks):
                # Prepare the command
                block_low = block & 0xFF
                block_high = (block >> 8) & 0xFF
                cmd = bytearray([0xFF, 0xB5, block_low, block_high, 0xFF, 0xFF, 0xFF])
                
                # Write the command to the device
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                
                time.sleep(0.1)
                
                # Read the chunk of data
                read_data = self.ft422_i2c.read(self.remote_addr, cmd, CHUNK_SIZE)

                if not read_data:
                    self.outputChanged.emit(self._Textbrowser_Color(1, f"Error reading block {block}. No data received."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time taken: {elapsed_time:.2f} seconds")
                    return
                
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in read_data)))

                if (self.TCONFlashDataGetFlag == False):
                    self.outputChanged.emit(self._Textbrowser_Color(1, "TCON Flash Data Get Flag is False, please check again."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
                    return

                # Handle the last chunk which might be smaller
                if (len(all_data) + len(read_data)) > TOTAL_SIZE:
                    bytes_to_read = TOTAL_SIZE - len(all_data)
                    read_data = read_data[:bytes_to_read]

                all_data.extend(read_data)

                # Report progress every 100 blocks
                if (block + 1) % 100 == 0 or (block + 1) == num_blocks:
                    progress = (len(all_data) / TOTAL_SIZE) * 100
                    self.outputChanged.emit(f"Read block {block+1}/{num_blocks}. Offset: 0x{len(all_data):X}. Progress: {progress:.2f}%")
                    QtWidgets.QApplication.processEvents() # Keep UI responsive

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"An error occurred: {e}"))
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")            
            return

        self.outputChanged.emit("DMC data read complete.")
        
        # cmd = bytearray([0xFF, 0xA9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd) 
        
        # Calculate and display checksum
        checksum = sum(all_data[2:])  # Exclude the first two bytes for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"Total data received: {len(all_data)} bytes.")
        self.outputChanged.emit(f"Checksum (2 bytes): 0x{checksum:04X}")

        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("DMC_2_data.bin", "wb") as f:
                    f.write(all_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "DMC LUT 2 data saved to DMC_2_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save DMC LUT 2 data to file: {e}"))
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_DMC_2_Checksum_Get(self):
        ''' DMC-2 Checksum get '''
        self.outputChanged.emit(f"Starting DMC-2 checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB5, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_dmc_2_crc.setText(f"{result[1]:02X}{result[0]:02X}")    
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result         
        
    def Engineer_DMC_3_data_Get(self):
        ''' DMC-3 data Get, start : 0x916100, length : 1036802 (0xFD202) bytes / 256 =  4051 chunks '''
        TOTAL_SIZE = 1036802
        CHUNK_SIZE = 256
        num_blocks = (TOTAL_SIZE + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.outputChanged.emit(f"Starting DMC data get. Total size: {TOTAL_SIZE} bytes, Chunk size: {CHUNK_SIZE} bytes.")
        
        # cmd = bytearray([0xFF, 0xB7, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)        
    
        all_data = bytearray()
        checksum = 0
        
        self.TCONFlashDataGetFlag = True
        start_time = time.time()
        try:
            for block in range(num_blocks):
                # Prepare the command
                block_low = block & 0xFF
                block_high = (block >> 8) & 0xFF
                cmd = bytearray([0xFF, 0xB6, block_low, block_high, 0xFF, 0xFF, 0xFF])
                
                # Write the command to the device
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                
                time.sleep(0.1)
                
                # Read the chunk of data
                read_data = self.ft422_i2c.read(self.remote_addr, cmd, CHUNK_SIZE)

                if not read_data:
                    self.outputChanged.emit(self._Textbrowser_Color(1, f"Error reading block {block}. No data received."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time taken: {elapsed_time:.2f} seconds")
                    return
                
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in read_data)))

                if (self.TCONFlashDataGetFlag == False):
                    self.outputChanged.emit(self._Textbrowser_Color(1, "TCON Flash Data Get Flag is False, please check again."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
                    return

                # Handle the last chunk which might be smaller
                if (len(all_data) + len(read_data)) > TOTAL_SIZE:
                    bytes_to_read = TOTAL_SIZE - len(all_data)
                    read_data = read_data[:bytes_to_read]

                all_data.extend(read_data)

                # Report progress every 100 blocks
                if (block + 1) % 100 == 0 or (block + 1) == num_blocks:
                    progress = (len(all_data) / TOTAL_SIZE) * 100
                    self.outputChanged.emit(f"Read block {block+1}/{num_blocks}. Offset: 0x{len(all_data):X}. Progress: {progress:.2f}%")
                    QtWidgets.QApplication.processEvents() # Keep UI responsive

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"An error occurred: {e}"))
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")            
            return

        self.outputChanged.emit("DMC data read complete.")
        
        # cmd = bytearray([0xFF, 0xA9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd) 
        
        # Calculate and display checksum
        checksum = sum(all_data[2:])  # TOTAL_SIZE = 1036802, 2 ~ 1036802 for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"Total data received: {len(all_data)} bytes.")
        self.outputChanged.emit(f"Checksum (2 bytes): 0x{checksum:04X}")

        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("DMC_3_data.bin", "wb") as f:
                    f.write(all_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "DMC LUT 3 data saved to DMC_3_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save DMC LUT 3 data to file: {e}"))
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result
        
    def Engineer_DMC_3_Checksum_Get(self):
        ''' DMC_3 Checksum get '''
        self.outputChanged.emit(f"DMC_3_Checksum_Get")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB6, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_dmc_3_crc.setText(f"{result[1]:02X}{result[0]:02X}")       
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result
        
    def Engineer_THERMAL_1_data_Get(self):
        ''' THERMAL-1 data get '''
        self.outputChanged.emit(f"THERMAL_1_data_Get")
        start_time = time.time()
        checksum = 0
        cmd = bytearray([0xFF, 0xB0, 0x00, 0x00, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        read_data = self.ft422_i2c.read(self.remote_addr, cmd, 256)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(read_data), 16):
            line = ''.join(f' 0x{x:02X}' for x in read_data[i:i+16])
            self.outputChanged.emit(line)
        
        # Calculate Checksum
        checksum = sum(read_data[6:])  # 6 ~ 256 for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"calculated checksum (0x{checksum:04X}): ")        
        
        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("Thermal_1_data.bin", "wb") as f:
                    f.write(read_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "Thermal 1 data saved to Thermal_1_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save Thermal 1 data to file: {e}"))          
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result 
        
    def Engineer_THERMAL_1_Checksum_Get(self):
        ''' THERMAL-1 Checksum get '''
        self.outputChanged.emit(f"THERMAL_1_Checksum_Get")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB0, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_thermal_1_crc.setText(f"{result[1]:02X}{result[0]:02X}")    
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result         
        
    def Engineer_THERMAL_2_data_Get(self):
        ''' Thermal 2 data Get, start : 0x4E100, stop: 0x52093, length : 16276 (0x3F94) bytes / 256 = 41268 packages. '''
        TOTAL_SIZE = 16276
        CHUNK_SIZE = 256
        num_blocks = (TOTAL_SIZE + CHUNK_SIZE - 1) // CHUNK_SIZE

        self.outputChanged.emit(f"Starting THERMAL-2 data get. Total size: {TOTAL_SIZE} bytes, Chunk size: {CHUNK_SIZE} bytes.")
          
        all_data = bytearray()
        checksum = 0
        
        self.TCONFlashDataGetFlag = True
        start_time = time.time()
        try:
            for block in range(num_blocks):
                # Prepare the command
                block_low = block & 0xFF
                block_high = (block >> 8) & 0xFF
                cmd = bytearray([0xFF, 0xB1, block_low, block_high, 0xFF, 0xFF, 0xFF])
                
                # Write the command to the device
                self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                
                time.sleep(0.1)
                
                # Read the chunk of data
                read_data = self.ft422_i2c.read(self.remote_addr, cmd, CHUNK_SIZE)

                if not read_data:
                    self.outputChanged.emit(self._Textbrowser_Color(1, f"Error reading block {block}. No data received."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time taken: {elapsed_time:.2f} seconds")
                    return
                
                self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in read_data)))

                if (self.TCONFlashDataGetFlag == False):
                    self.outputChanged.emit(self._Textbrowser_Color(1, "TCON Flash Data Get Flag is False, please check again."))
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
                    return

                # Handle the last chunk which might be smaller
                if (len(all_data) + len(read_data)) > TOTAL_SIZE:
                    bytes_to_read = TOTAL_SIZE - len(all_data)
                    read_data = read_data[:bytes_to_read]

                all_data.extend(read_data)

                # Report progress every 100 blocks
                if (block + 1) % 100 == 0 or (block + 1) == num_blocks:
                    progress = (len(all_data) / TOTAL_SIZE) * 100
                    self.outputChanged.emit(f"Read block {block+1}/{num_blocks}. Offset: 0x{len(all_data):X}. Progress: {progress:.2f}%")
                    QtWidgets.QApplication.processEvents() # Keep UI responsive

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"An error occurred: {e}"))
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")            
            return

        self.outputChanged.emit("Thermal-2 data read complete.")

        # cmd = bytearray([0xFF, 0xA9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # # Write the command to the device
        # self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        # self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd) 
        
        # Calculate and display checksum
        checksum = sum(all_data[26:])  # TOTAL_SIZE = 16276, 26 ~ 16276 for checksum calculation
        checksum &= 0xFFFF # 2-byte checksum
        self.outputChanged.emit(f"Total data received: {len(all_data)} bytes.")
        self.outputChanged.emit(f"Checksum (2 bytes): 0x{checksum:04X}")

        # Save data to file
        if self._config_CRC_DataSave == True:
            try:
                with open("Thermal_2_data.bin", "wb") as f:
                    f.write(all_data)
                self.outputChanged.emit(self._Textbrowser_Color(2, "Thermal 2 data saved to Thermal_2_data.bin"))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save thermal 2 data to file: {e}"))
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result         
        
        
    def Engineer_THERMAL_2_Checksum_Get(self):
        ''' THERMAL-2 Checksum get '''
        self.outputChanged.emit(f"Starting THERMAL-2 checksum get.")
        start_time = time.time()
        cmd = bytearray([0xFF, 0xB1, 0xFF, 0xFF, 0x01, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.1)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 2)
        # self.outputChanged.emit("serdes Read Checksum: %s" % (' '.join('0x{:02X}'.format(x) for x in result[:2])))
        self.outputChanged.emit("serdes read checksum: ")
        for i in range(0, len(result), 16):
            line = ''.join(f' 0x{x:02X}' for x in result[i:i+16])
            self.outputChanged.emit(line)
        
        self.TCONFlashDataGetFlag = False  # Reset flag after operation
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.outputChanged.emit(f"Execution time: {elapsed_time:.2f} seconds.")
        
        self.ui.label_thermal_2_crc.setText(f"{result[1]:02X}{result[0]:02X}") 
                
        self.ui.comboBox_11.setCurrentIndex(0)  # Update the combo box with the first byte of the result         
        
    def Engineer_TCON_ASIL_Get(self, result=None):
        ''' TCON ASIL Get '''
        if not isinstance(result, (bytes, bytearray)):
            cmd = bytearray([0xFF, 0x31, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
            result = self.ft422_i2c.read(self.remote_addr, cmd, 14)
            self.outputChanged.emit("TCON ASIL : %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
            
        try:
            self.ui.asilcode_label.setText("ASIL Code: 0x%s" % (''.join('{:02X}'.format(x) for x in result[4:12])))
            if result and isinstance(result, (bytes, bytearray)) and len(result) >= 10:
                value = int.from_bytes(result[4:12], byteorder='big')
            else:
                value = 0
        except Exception as e:
            self.outputChanged.emit(f"Error: {e}")
            value = 0
        try:
            header = self.ui.tableFailFlag.horizontalHeader()
            if header is not None:
                header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        except Exception as e:
            self.outputChanged.emit(f"Error: {e}")

        table = self.ui.tableFailFlag
        for bit in range(63, -1, -1):
            row = 63 - bit
            desc = bitfield_names.get(bit, f"Unknown {bit}")
            val = (value >> bit) & 1
            
            # Bit 
            bit_item = QTableWidgetItem(str(bit))
            bit_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, bit_item)

            # Description
            desc_item = QTableWidgetItem(desc)
            desc_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, desc_item)
            
            # Value 
            val_item = QTableWidgetItem(str(val))
            val_item.setTextAlignment(Qt.AlignCenter)            
            if val == 1:
                val_item.setBackground(QColor(255, 0, 0))
                val_item.setFont(QFont("Arial", 10, QFont.Bold))
                
            table.setItem(row, 2, val_item)
            
        if isinstance(result, (bytes, bytearray)) and len(result) >= 14:
            self.ui.powerByte_label.setText("Power Circuit: 0x%02X" % result[13])
            for i in range(7):
                bit = (result[13] >> (6-i)) & 0x01
                item = QTableWidgetItem(str(bit))
                item.setTextAlignment(Qt.AlignCenter)
                if bit == 0:
                    item.setBackground(QColor(255, 0, 0))
                self.ui.powerbit_table.setItem(0, i, item)
       
    def Engineer_TCON_ASIL_MenuInput(self):
        ''' TCON ASIL Menu Input '''
        try:
            # get the input from the user
            input_str = self.ui.asil_input_edit.text().strip()
            # 將 0x6F 0x06 .... 拆成hex整數列表
            byte_list = [int(b, 16) for b in input_str.replace('0x', '').split()]
            
            if len(byte_list) != 13:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Input Error, Expecting 13 Bytes, Please Check again!!."))
                return
            
            # convert to bytearray
            result = bytes(byte_list)
            self.Engineer_TCON_ASIL_Get(result)
            
        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Input Error: {str(e)}"))
            return
        
        # self.ui.comboBox_8.setCurrentIndex(result[0])
    def Engineer_RCN_Set(self):
        ''' TC State Get '''
        cmd = bytearray([0xFF, 0x32, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        if (self.ui.checkBox_RCN.isChecked()):
            cmd[2] = 0x01
        else: 
            cmd[2] = 0x00
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

    def Engineer_RCN_Get(self):
        ''' RCN State Get '''
        cmd = bytearray([0xFF, 0x33, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        time.sleep(0.02)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        if (result[0] == 0x00):
            self.ui.checkBox_RCN.setChecked(False)
        elif (result[0] == 0x01):
            self.ui.checkBox_RCN.setChecked(True)

    def Engineer_TCON_Register_Get(self):
        ''' TCON Register Get '''
        cmd = bytearray([0xFF, 0x34, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        add_str = self.ui.addr_input.text().strip()
        try:
            address = int(add_str, 16) if add_str.lower().startswith('0x') else int(add_str, 16)
            address_bytes = bytearray([(address >> 24) & 0xFF, (address >> 16) & 0xFF, (address >> 8) & 0xFF, address & 0xFF])
            cmd[2:6] = address_bytes          
        
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
            time.sleep(0.02)
            result = self.ft422_i2c.read(self.remote_addr, cmd, 4)
            self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
            
            value = (result[0] << 24) | (result[1] << 16) | (result[2] << 8) | result[3]
            bits = f"{value:032b}"
            self.ui.bit_table.blockSignals(True)
            for i in range(32):
                item = self.ui.bit_table.item(0, i)
                if item is not None:
                    item.setText(bits[i])
            self.ui.bit_table.blockSignals(False)
            self.update_combined_value()
        except ValueError:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Input Error, Please Check again!!."))
            return

    def Engineer_TCON_Register_Set(self):
        ''' TCON Register Set '''
        cmd = bytearray([0xFF, 0x35, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        add_str = self.ui.addr_input.text().strip()
        try:
            address = int(add_str, 16) if add_str.lower().startswith('0x') else int(add_str, 16)
            bits = ''.join([self.ui.bit_table.item(0, i).text() for i in range(32)])
            if not all(bit in ('0', '1') for bit in bits):
                raise ValueError("Invalid binary input")
            value = int(bits, 2)
            address_bytes = bytearray([(address >> 24) & 0xFF, (address >> 16) & 0xFF, (address >> 8) & 0xFF, address & 0xFF])
            value_bytes = bytearray([(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])
            cmd[2:6] = address_bytes
            cmd[6:10] = value_bytes
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        except ValueError:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Input Error, Please Check again!!."))
            return
        
    def update_combined_value(self):
        bits = ''.join(self.ui.bit_table.item(0, i).text() if self.ui.bit_table.item(0, i) else '0' for i in range(32))
        if all(bit in ('0', '1') for bit in bits):
            value = int(bits, 2)
            self.ui.current_value_display.setText(f"0x{value:08X}")
        else:
            self.ui.current_value_display.setText("Invalid input")
            
    def Engineer_TCON_Register_Send_Process(self):
        ''' TCON Register Send '''
        cmd = bytearray([0xFF, 0x35, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        raw_text = self.ui.plainTextEdit.toPlainText()
        lines = raw_text.strip().split('\n')

        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                self.outputChanged.emit(self._Textbrowser_Color(4, line))
                addr_str, value_str = line.split(',')
                address = int(addr_str, 16) if addr_str.lower().startswith('0x') else int(addr_str, 16)
                value = int(value_str, 16) if value_str.lower().startswith('0x') else int(value_str, 16)
                parsed.append((address, value))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Skipping invalid line: {line}!."))
        custom_delay_str = self.ui.lineEdit_RegRepeat_time.text().strip()
        custom_delay_ms = 0
        if custom_delay_str:
            try:
                custom_delay_ms = int(custom_delay_str)
            except ValueError:
                self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid custom delay time, please enter a valid integer."))
                return

        if parsed:
            while True:
                for address, value in parsed:
                    if custom_delay_ms > 0:
                        time.sleep(custom_delay_ms / 1000)  # Delay in milliseconds
                        self.outputChanged.emit(f"Delay: {custom_delay_ms} ms")
                    elif address == 0x00:
                        time.sleep(value / 1000)  # Delay in milliseconds
                        self.outputChanged.emit(f"Delay: {value} ms")
                        continue
                    
                    address_bytes = bytearray([(address >> 24) & 0xFF, (address >> 16) & 0xFF, (address >> 8) & 0xFF, address & 0xFF])
                    value_bytes = bytearray([(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])
                    cmd[2:6] = address_bytes
                    cmd[6:10] = value_bytes
                    self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
                    self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
                    
                    if custom_delay_ms <= 0 and address != 0x00:
                        time.sleep(0.01)

                if not self.ui.checkBox_RegRepeat.isChecked():
                    break
                
                QtWidgets.QApplication.processEvents()  # Keep UI responsive
                if custom_delay_ms <= 0 and address != 0x00:
                    time.sleep(0.1)  # Avoid busy loop
                
    def Engineer_TCON_Register_Save_Process(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Registers Data", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.ui.plainTextEdit.toPlainText())
                self.outputChanged.emit(self._Textbrowser_Color(2, f"Registers data saved to {filename}."))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to save registers data: {e}."))

    def Engineer_TCON_Register_Load_Process(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Registers Data", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = f.read()
                self.ui.plainTextEdit.setPlainText(data)
                self.outputChanged.emit(self._Textbrowser_Color(2, f"Registers data loaded from {filename}."))
            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Failed to load registers data: {e}."))

    def Serdes_Register_Write(self):
        raw_str = self.ui.serdes_write.text().strip()
        try:
            data_bytes = bytearray(int(raw_str, 16) for raw_str in raw_str.split(','))
            if len(data_bytes) != 4:
                raise ValueError("Invalid input, please enter 4 bytes separated by commas.")
            
            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in data_bytes)))
            self.ft422_i2c.auo_i2cMaster_Write((data_bytes[0] >> 1), I2C_Flag.START_AND_STOP, data_bytes[1:])

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Input Error, Please Check again!! {e}."))
            return
    
    def Serdes_Register_Read(self):
        raw_str = self.ui.serdes_read.text().strip()
        try:
            data_bytes = bytearray(int(raw_str, 16) for raw_str in raw_str.split(','))
            if len(data_bytes) != 3:
                raise ValueError("Invalid input, please enter 3 bytes separated by commas.")

            self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in data_bytes)))
            result = self.ft422_i2c.read((data_bytes[0] >> 1), data_bytes[1:], 1)
            self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
            if len(result) != 1:
                raise ValueError("Invalid response length, expected 1 byte.")
            self.ui.Serdes_Read_label.setText("Read :  0x%02X" % result[0])

        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Input Error, Please Check again!! {e}."))
            return
    

    def Serdes_Register_Read_Process(self):
        raw_text = self.ui.plainTextEdit_serdes.toPlainText()
        lines = raw_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = line.split('//')[0].strip()  # Remove comments
            if not line:
                continue
            
            self.outputChanged.emit(self._Textbrowser_Color(4, line))
            try:
                data_bytes = bytearray(int(x.strip(), 16) for x in line.split(',') if x.strip())
                data_length = len(data_bytes)
                
                if data_length != 5 and data_length != 2:
                    raise ValueError("Invalid input, please enter 5 or 2 bytes separated by commas.")
                
                if (data_length == 2):
                    delay_time = int(data_bytes[1])
                    time.sleep(delay_time/1000)
                    self.outputChanged.emit("delay: %d ms" % delay_time)
                else:
                    self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in data_bytes)))
                    self.ft422_i2c.write(data_bytes, len(data_bytes))

            except Exception as e:
                self.outputChanged.emit(self._Textbrowser_Color(1, f"Skipping invalid line: {e}!."))
                
    def update_eeprom_display(self):
        ''' EEPROM DATA DISPLAY '''
        cmd = bytearray([0xFF, 0x40, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        try:
            raw_data = self.ft422_i2c.read(self.remote_addr, cmd, 36)
            if len(raw_data) != 36:
                raise Exception("Invalid response length, expected 36 bytes.")
            
            self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in raw_data)))
            
            self.ui.label_eeprom_version.setText("Data Version: %s" % ('0x%02X' % raw_data[0]))
            self.ui.label_eeprom_status.setText("EEPROM Status: %s" % ('OK' if raw_data[1] == 0x00 else 'NG'))
            self.ui.label_eeprom_checksum.setText("Checksum: %s" % ('0x%02X' % raw_data[2]))
            
            for i in range(3, 36):
                idx = i - 3
                row = (idx // 8)
                col = (idx % 8)
                item = QTableWidgetItem(f"0x{raw_data[i]:02X},('{chr(raw_data[i])}')")
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.eeprom_table.setItem(row, col, item)
        except Exception as e:
            self.ui.label_eeprom_status.setText("EEPROM Status: %s" % 'NG')
            self.ui.label_eeprom_version.setText("Data Version: %s" % '0x00')
            self.ui.label_eeprom_checksum.setText("Checksum: %s" % '0x00')

            self.ui.eeprom_table.clearContents()
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Error: {e}"))
            
    def Diagnosis_log_get(self):
        ''' Diagnosis Log Get '''
        # creat customer cmd
        # cmd = bytearray([0x86])
        # self.outputChanged.emit("serdes write(0x%02X): %s" % (self.remote_addr, ' '.join('0x{:02X}'.format(x) for x in cmd)))
        # result = self.ft422_i2c.read(self.remote_addr, cmd, 69)        
        
        # creat auo's diagnostic cmd
        cmd = bytearray([0xFF, 0x41, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        result = self.ft422_i2c.read(self.remote_addr, cmd, 38)
        self.outputChanged.emit("serdes write(0x%02X): %s" % (self.remote_addr, ' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))

        if len(result) < 38 or result[0] > 0x10:
            self.outputChanged.emit(self._Textbrowser_Color(1, "Invalid response length or index out of range."))
            self.ui.dtc_log_index_edit.setText("N/A")
            self.ui.dtc_log_err_code.setText("Error Code : N/A")
            self.ui.dtc_log_timestamp.setText("Timestamp : N/A")
            self.ui.dtc_log_power_state.setText("Power Status : N/A")
            self.ui.dtc_log_temperature.setText("Temperature : N/A")
            self.ui.dtc_log_voltage.setText("Voltage : N/A")
            self.ui.dtc_log_extra_info.setText("Diagnosis Code : N/A")
            self.ui.dtc_log_boost_pg.setText("BUCK BOOST PG : N/A")
            self.ui.dtc_log_hv_pg.setText("HV BUCK PG : N/A")
            self.ui.dtc_log_lv_pg.setText("LV BUCK PG : N/A")
            self.ui.dtc_log_ldo_pg.setText("LV LDO PG : N/A")
            self.ui.dtc_log_gmsl_pwdnb.setText("GMSL PWDNB : N/A")
            self.ui.dtc_log_gmsl_lock.setText("GMSL LOCK : N/A")
            self.ui.dtc_log_gmsl_errb.setText("GMSL ERRB : N/A")
            self.ui.dtc_log_tcon_state.setText("TCON Status : N/A")
            self.ui.dtc_log_tcon_led_pg.setText("TCON LED PG : N/A")
            self.ui.dtc_log_tcon_tft_pg.setText("TCON TFT PG : N/A")
            self.ui.dtc_log_tcon_db_pg.setText("TCON DB PG : N/A")
            self.ui.dtc_log_tcon_display.setText("TCON Display : N/A")
            self.ui.dtc_log_tcon_goa.setText("TCON GOA : N/A")
            self.ui.dtc_log_tcon_cof.setText("TCON COF : N/A")
            self.ui.dtc_log_tcon_rx.setText("TCON RX : N/A")
            return
        # Error Index 4 bytes : 0 ~ 3
        error_index = self.bytes_to_uint_le(result[0:2])
        self.ui.dtc_log_index_edit.setText(str(error_index))
        error_count = self.bytes_to_uint_le(result[2:4])
        self.ui.dtc_log_err_count.setText(f"Error Count : {error_count}")
        # Error or not 1 byte : 4
        _is_error = result[4]
        #timestamp 6 bytes  : 5 ~ 10
        if result[9] == 0x00 and result[10] == 0x00:
            timestamp = self.bytes_to_uint_le(result[5:11])
            self.ui.dtc_log_timestamp.setText(f"Timestamp : {timestamp}")
        else:
            year = int(result[5]) + 2000
            month = int(result[6])
            day = int(result[7])
            hour = int(result[8])
            minute = int(result[9])
            second = int(result[10])
            self.ui.dtc_log_timestamp.setText(f"Timestamp : {year}/{month}/{day} {hour}:{minute}:{second}")
        # diagnostic code 2 bytes : 11 ~ 12
        self.ui.dtc_log_err_code.setText(f"Error Code : 0x{result[12]:02X}{result[11]:02X}")
        # power status 1 byte : 13
        status_byte = result[13]
        status_str = Power_status_map.get(status_byte, f"Unknown({status_byte})")
        self.ui.dtc_log_power_state.setText(f"Power Status : {status_str} ({status_byte})")
        # temperature 1 byte : 14
        temperature = ctypes.c_int8(result[14]).value
        self.ui.dtc_log_temperature.setText(f"Temperature : {temperature} °C")
        # voltage 2 bytes : 15 ~ 16
        voltage = self.bytes_to_uint_le(result[15:17])/1000
        self.ui.dtc_log_voltage.setText(f"Voltage : {voltage} V")
        # extra info 2 bytes : 17 ~ 18
        self.ui.dtc_log_extra_info.setText(f"Diagnosis Code : 0x{result[18]:02X}{result[17]:02X}")
        ## Power Status
        self.ui.dtc_log_boost_pg.setText(f"BUCK BOOST PG : {'OK' if (result[19] & 0x01) else 'NG'}")
        self.ui.dtc_log_hv_pg.setText(f"HV BUCK PG : {'OK' if (result[19] & 0x02) else 'NG'}")
        self.ui.dtc_log_lv_pg.setText(f"LV BUCK PG : {'OK' if (result[19] & 0x04) else 'NG'}")
        self.ui.dtc_log_ldo_pg.setText(f"LV LDO PG : {'OK' if (result[19] & 0x08) else 'NG'}")
        ## GMSL Status
        self.ui.dtc_log_gmsl_pwdnb.setText(f"GMSL PWDNB : {'OK' if (result[20] & 0x01) else 'NG'}")
        self.ui.dtc_log_gmsl_lock.setText(f"GMSL LOCK : {'LOCKED' if (result[20] & 0x02) else 'UNLOCKED'}")
        self.ui.dtc_log_gmsl_errb.setText(f"GMSL ERRB : {'OK' if (result[20] & 0x04) else 'NG'}")
        ## TCON Status
        self.ui.dtc_log_tcon_state.setText(f"TCON Status : {'NG' if (result[21] & 0x01) else 'OK'}")
        self.ui.dtc_log_tcon_led_pg.setText(f"TCON LED PG : {'OK' if (result[21] & 0x02) else 'NG'}")
        self.ui.dtc_log_tcon_tft_pg.setText(f"TCON TFT PG : {'OK' if (result[21] & 0x04) else 'NG'}")
        self.ui.dtc_log_tcon_db_pg.setText(f"TCON DB PG : {'OK' if (result[21] & 0x08) else 'NG'}")
        self.ui.dtc_log_tcon_display.setText(f"Display Status : {'Can not Display' if (result[21] & 0x10) else 'Displayed'}")
        self.ui.dtc_log_tcon_goa.setText(f"TCON GOA Status : {'NG' if (result[21] & 0x20) else 'OK'}")
        self.ui.dtc_log_tcon_cof.setText(f"TCON COF Status : {'NG' if (result[21] & 0x40) else 'OK'}")
        self.ui.dtc_log_tcon_rx.setText(f"TCON RX Status : {'NG' if (result[21] & 0x80) else 'OK'}")
        self.ui.dtc_log_tcon_asil.setText(f"TCON ASIL code : %s" % (' '.join('0x{:02X}'.format(x) for x in result[22:35])))
        self.ui.dtc_log_max25121.setText(f"MAX25121 [5, 6] : %s" % (' '.join('0x{:02X}'.format(x) for x in result[35:37])))

    def Diagnosis_log_clear(self):
        ''' Diagnosis Log Process '''
        cmd = bytearray([0xFF, 0x41, 0x00, 0xFF, 0xFF, 0xFF, 0xFF])
        
        ### pop up message to confirm clear
        reply = QtWidgets.QMessageBox.question(
            self, 
            'Clear Diagnosis Log',
            'Are you sure you want to clear all diagnostics log?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.No:
            return
        
        # send command to clear log                          
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))

    def Diagnosis_log_request(self):
        ''' Diagnosis Log Request '''
        cmd = bytearray([0xFF, 0x41, 0x01, 0xFF, 0xFF, 0xFF, 0xFF])
        index_str = self.ui.dtc_log_index_edit.text().strip()
        try:
            index_value = int(index_str) & 0xFF  # Ensure index is between 0 and 255
            if index_value < 0 or index_value > 255:
                raise ValueError("Index must be between 0 and 255.")
            cmd[3] = index_value
        except ValueError:
            cmd[3] = 0x00  # Default to 0 if input is invalid
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

    def Diagnosis_log_request_latest(self):
        ''' Diagnosis Log Request Latest '''
        cmd = bytearray([0xFF, 0x41, 0x02, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)

    def Engineer_mcu_crc_get(self):
        ''' Diagnosis Log Get '''
        cmd = bytearray([0xFF, 0xB9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        try:
            raw_data = self.ft422_i2c.read(self.remote_addr, cmd, 4)
            if len(raw_data) != 4:
                raise Exception("Invalid response length, expected 36 bytes.")
            raw_str = ''.join('{:02X}'.format(x) for x in raw_data)
            self.ui.label_mcu_crc.setText("%s" % raw_str)
            self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in raw_data)))
        except Exception as e:
            self.outputChanged.emit(self._Textbrowser_Color(1, f"Error: {e}"))

    def Engineer_cross_pattern_set(self):
        ''' Cross Pattern Set '''
        cmd = bytearray([0xFF, 0xA5, 0x00, 0xFF, 0xFF, 0xFF, 0xFF])
        item = self.ui.comboBox_crosspattern.currentText()
        if item == "OFF":
            cmd[2] = 0x00
        elif item == "Red":
            cmd[2] = 0x01
        elif item == "Green":
            cmd[2] = 0x02
        elif item == "Blue":
            cmd[2] = 0x03
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
        
    def Engineer_cross_pattern_get(self):
        ''' Cross Pattern Get '''
        cmd = bytearray([0xFF, 0xA6, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)        
        time.sleep(0.02)
        result = self.ft422_i2c.read(self.remote_addr, cmd, 5)
        self.outputChanged.emit("serdes read: %s" % (' '.join('0x{:02X}'.format(x) for x in result)))
        status_byte = result[0]
        status_str = Cross_Pattern_map.get(status_byte, f"Unknown({status_byte})")
        self.ui.label_67.setText("Cross Pattern: %s" % status_str)
        
    @staticmethod
    def bytes_to_uint_le(b: bytes) -> int:
        """ Convert little-edian byte array to unsigned integger. """
        return int.from_bytes(b, byteorder='little', signed=False)

    def _ConvertHexChar(self, ch): 
        if((ch >= 0x30) and (ch <= 0x39)):
            return ch-0x30
        elif(ch >= 0x41) and (ch <= 0x46):
            return ch-0x41+10
        elif(ch >= 0x61) and (ch <= 0x66): 
            return ch-0x61+10
        else:
            return(-1)
            
    def _Textbrowser_Color(self, color, str):
        if(color == 1):
            out_str = '<span style=\" color: red;\">%s</span> <span style=\" color: black;\"> </span>'%(str)
        elif (color == 2):
            out_str = '<span style=\" color: green;\">%s</span> <span style=\" color: black;\"> </span>'%(str)
        elif (color == 3):
            out_str = '<span style=\" color: blue;\">%s</span> <span style=\" color: black;\"> </span>'%(str)
        elif (color == 4):
            out_str = '<span style=\" color: white;\">%s</span> <span style=\" color: black;\"> </span>'%(str)
        else:
            out_str = '<span style=\" color: black;\">%s</span>'%(str)
        return out_str
    
    def ErrorLog_RequestCmd(self):
        ''' Error Log Request Command '''
        cmd = bytearray([0x11, 0x00, 0x00])         
        # cal checksum 
        cmd.append(self.ft422_i2c.auo_calculate_SHM_chechsum(cmd, 3))
        # sent out 
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
        self.ft422_i2c.auo_i2cMaster_Write(self.remote_addr, I2C_Flag.START_AND_STOP, cmd)
    
    def ErrorLog_Information(self): 
        #define Command 
        cmd = bytearray([0x86])
            
        self.outputChanged.emit("serdes write: %s" % (' '.join('0x{:02X}'.format(x) for x in cmd)))
            
        state = self.ft422_i2c.read(self.remote_addr, cmd, 69)
        self.ui.label_ErrorLogData.setText(' '.join('{:02X}'.format(x) for x in state))
        self.outputChanged.emit("serdes read:%s"%(' '.join('0x{:02X}'.format(x) for x in state)))
        
    def str2bool(self, val):
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1', 'enable'):
            return True
        elif val in ('n', 'no', 'f', 'false', 'off', '0', 'disable'):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))

    def bcd_to_decimal(self, bcd_byte):
        """ Convert BCD byte to decimal integer. """
        return (bcd_byte >> 4) * 10 + (bcd_byte & 0x0F)

    def _checkConfigExist(self):
        self.dirname = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        targDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        targPath = targDir + "/conf/config.ini"
        if not os.path.isfile(targPath):
            os.mkdir(targDir + '/conf')
            shutil.copyfile((self.dirname + "/conf/config.ini"), (targDir + "/conf/config.ini"))

    def _readConfig(self, path:str): 
        config = configparser.ConfigParser()
        config.read(self.dirConfig+path)
        # Remote I2C Address
        if config['I2C']['Remote_Address'] != 'null':
            self.remote_addr = int(config['I2C']['Remote_Address'], 16)
            
        if config['LOG']['Log_Switch'] != 'null':
            self._config_log_switch = self.str2bool(config['LOG']['Log_Switch'])
            
        try: 
            if config['UPDATE']['MCU_Boot_Update'] != 'null':
                self._config_MCU_Update = self.str2bool(config['UPDATE']['MCU_Boot_update'])
                self._config_TCON_update = self.str2bool(config['UPDATE']['TCON_update'])
                self._config_DeMura_update = self.str2bool(config['UPDATE']['DeMura_update'])
        except:    
            self._config_MCU_Update = False
            self._config_TCON_update = False
            self._config_DeMura_update = False
            
        try:
            if config['ENGINEER']['Test_Switch'] != 'null':
                self._config_test_switch = self.str2bool(config['ENGINEER']['Test_Switch'])
                self._config_AutoRefresh = self.str2bool(config['ENGINEER']['Auto_Refresh'])
                self._config_AutoRefrshTime = int(config["ENGINEER"]['Refresh_Time'])
                self._config_CRC_DataSave = self.str2bool(config['ENGINEER']['CRC_Data_Save'])         
        except:
            self._config_test_switch = False
            self._config_AutoRefresh = False
            self._config_AutoRefrshTime = 1
            self._config_CRC_DataSave = False
            
        try:
            if config['COMMAND'] != 'null':
                self._interval_test = self.str2bool(config['COMMAND']['INTERVAL_TEST'])
        except:
            self._interval_test = False
            
        try:
            if config['SERDES'] != 'null':
                self._serdes_register = self.str2bool(config['SERDES']['SERDES_REGISTER'])
        except:
            self._serdes_register = False
                
        try:
            if config['TCON_ASIL'] != 'null':
                self._tcon_asil = self.str2bool(config['TCON_ASIL']['TCON_ASIL'])
        except:
            self._tcon_asil = False
            
        try:
            if config['TCON_REGISTER'] != 'null':
                self._tcon_register = self.str2bool(config['TCON_REGISTER']['TCON_REGISTER'])
        except:
            self._tcon_register = False
            
    def ExitProgram(self, str):
        if (str == "FT4222 Init Error"):
            QtWidgets.QMessageBox.critical(None, "Device Init Error", "FT4222 I2C Device Init Error!! \n Please check FT4222 connection.")
        elif (str == "FT4222 GMSLlink Error"):
            QtWidgets.QMessageBox.critical(None, "FT4222 Device Error", "FT4222 I2C Device Error!! \n Please Restart the Application.")
        # app.quit()             
            
    def closeEvent(self, event):
        
        self.release_resources()
        
        event.accept()
        
    def release_resources(self):
        if self.Main_thread_flag:
            self.Main_thread_flag = False
            self.thread = None
                    
        # if self.ft4222_io:
        #     self.ft4222_io.close()
        #     self.ft4222_io = None
            
        if self.ft422_i2c:
            self.ft422_i2c.close()
            self.ft422_i2c = None

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
