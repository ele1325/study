#  Copyright (c) 2024 AOX Technologies GmbH, Germany

import os
import struct
import sys
import time

SIL = False

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from ged4k import GED4KControl, Display

# Special setup that uses port-forwarding
ip_addr = "169.254.1.2"
port_rpc_tx = 55555
port_http_tx = 80


# GED4K TX (host) object
ged4k_tx = GED4KControl(ip_addr, port_rpc_tx, port_http_tx)

def set_target_luminance():
    # GDCN mesage attributes
    channel = 64 # Command and control low
    msg = 53     # SET_TARGET_LUMINANCE

    # Arguments to SET_TARGET_LUMINANCE
    # Arguments need to be passed as array of uint8 values as they shall be sent over GDCN
    target_luminance_display = struct.pack('>H', 120)
    damping_interior_illumination = struct.pack('>B', 2)
    change_over_day_night = struct.pack('>B', 1)

    payload = target_luminance_display + damping_interior_illumination + change_over_day_night
    payload = [int(byte) for byte in payload]

    try:
        ged4k_tx.gdcn_send(Display(3, 0, 0), channel, msg, payload)
    except Exception as e:
        print(e)
        sys.exit()

def status_sw_version():
    channel = 64
    cmd_id = 0x63
    payload = None

    if SIL:
        return [182, 81, 0, 10, 36, 18, 37, 1, 0, 0, 6, 2, 0, 10, 14, 0, 0, 0, 0, 1, 0, 0, 0, 1, 182, 81, 0, 10, 
                  182, 81, 0, 10, 36, 18, 37, 1, 36, 18, 37, 1, 0, 0, 15, 201, 0]
    
    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def sensor_ident_lesen():
    channel = 64
    cmd_id = 0x20
    payload = None
    if SIL:
        return [91, 64, 0, 255, 5, 181, 20, 70, 255, 255, 255, 255, 255, 36, 4, 48, 0, 0, 48, 57, 1, 154, 1, 146]

    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def get_display_svk():
    channel = 64
    cmd_id = 0x37
    payload = None
    if SIL:
        return [1, 0, 0, 208, 70, 182, 2, 2, 6, 0, 0, 193, 46, 182, 2, 10, 8, 0, 0, 192, 211, 182, 81, 10]

    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def get_display_id_short():
    channel = 16
    cmd_id = 0x21
    payload = None
    if SIL:
        return [32, 82, 2, 0, 2, 35]

    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def get_display_id():
    channel = 16
    cmd_id = 0x20
    payload = None
    if SIL:
        return [32, 82, 2, 0, 32, 2, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 29, 204, 12, 118, 5, 60, 
                  12, 70, 5, 0, 159, 154, 78, 196, 52, 169, 102, 98, 16, 233, 36, 82, 176, 100, 0, 0, 0, 0, 2, 
                  120, 34, 0, 20, 102, 49, 4, 128, 59, 12, 143, 0, 35, 0, 11, 0, 69, 5, 47, 0, 41, 0, 2, 0, 38, 
                  0, 9, 2, 0, 0, 0, 0, 0, 0, 0, 0, 35]

    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def get_dsc_capabilities():
    channel = 16
    cmd_id = 0x24
    payload = None
    if SIL:
        return [1, 33, 1, 9, 1, 1, 0, 3, 6, 0, 24, 0, 0]


    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def set_test_image_display(onoff, screen):
    channel = 64
    cmd_id = 51

    ON_OFF = struct.pack('>?', onoff)
    SCREEN = struct.pack('>H', screen)

    payload = ON_OFF + SCREEN
    payload = [int(byte) for byte in payload]

    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

if __name__ == "__main__":
    a = set_test_image_display(True, 3)
    print(a)
    b = status_sw_version()
    print(b)

    time.sleep(1)
    set_test_image_display(True, 1)
    time.sleep(1)
    set_test_image_display(True, 2)
    time.sleep(1)
    set_test_image_display(True, 3)
    time.sleep(1)
    set_test_image_display(True, 4)
