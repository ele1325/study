import time

def mclocker():
    return int(time.time_ns() / 1000000)
    
def uclocker():
    return int(time.time_ns() / 1000)
