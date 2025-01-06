# Configurations for the expect script -- start
SIL = True
ISTEP_Index = 4
HWEL = "182.002.002"
BTLD = "182.002.010"
SWFL = "182.081.010"
GDCN4A = "6.2"
GDCN4B = "10.14.0"
CMDSEQ = 24122501
# Configurations for the expect script -- end


SW = ISTEP_Index * 100 + int(SWFL.split('.')[-1])
HW = ISTEP_Index * 100 + int(HWEL.split('.')[-1])

expected_sensor_ident_lesen = [91, 64, 0, 255, 5, 181, 20, 70, 255, 255, 255, 255, 255, None, None, None, None, None, None, None] \
                     + list(SW.to_bytes(2, byteorder='big')) \
                     + list(HW.to_bytes(2, byteorder='big'))

expected_display_svk = [1, 0, 0, 208, 70] + [int(part) for part in HWEL.split('.')] \
              + [6, 0, 0, 193, 46] + [int(part) for part in BTLD.split('.')] \
              + [8, 0, 0, 192, 211] + [int(part) for part in SWFL.split('.')]

expected_display_id_short = [32, 82, 2, 0, 2, 35]

expected_display_id = [
    32, 82, 2, 0, 32, 2, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 0, 29, 204, 12, 118, 5, 60, 12, 70, 5, 0, 159, 
    154, 78, 196, 52, 169, 102, 98, 16, 233, 36, 82, 176, 100, 0, 0, 0, 0, 2, 120, 34, 0, 20, 102, 49, 4, 128, 59, 12, 
    143, 0, 35, 0, 11, 0, 69, 5, 47, 0, 41, 0, 2, 0, 38, 0, 9, 2, 0, 0, 0, 0, 0, 0, 0, 0, 35
]

if __name__ == "__main__":
    print(SW)
    print(HW)
    print(expected_sensor_ident_lesen[:13])
    print(expected_sensor_ident_lesen[-4:])
    print(expected_display_svk)