#  Copyright (c) 2024 AOX Technologies GmbH, Germany

import os
import struct
import sys
import time

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

def set_test_image_display(onoff, screen):
    channel = 64
    cmd_id = 51

    ON_OFF = struct.pack('>?', onoff)
    SCREEN = struct.pack('>H', screen)

    payload = ON_OFF + SCREEN
    payload = [int(byte) for byte in payload]

    try:
        ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def get_display_id():
    channel = 16
    cmd_id = 0x20
    payload = None
    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

def sensor_ident_lesen():
    channel = 64
    cmd_id = 0x20
    payload = None
    try:
        return ged4k_tx.gdcn_send(Display(3, 0, 0), channel, cmd_id, payload)
    except Exception as e:
        print(e)
        sys.exit()

if __name__ == "__main__":
    a = sensor_ident_lesen()
    print(a)
    # get_display_id()
    # time.sleep(1)
    # set_test_image_display(True, 1)
    # time.sleep(1)
    # set_test_image_display(True, 2)
    # time.sleep(1)
    # set_test_image_display(True, 3)
    # time.sleep(1)
    # set_test_image_display(True, 4)
