from sr import *
import time
import systemetric

def main():
    R = systemetric.Robot()
 
    R.rotateTo(0)
    time.sleep(1)
    R.driveDistance(2)
    R.stop()
    time.sleep(2)
    R.rotateTo(180)
    time.sleep(1)
    R.driveDistance(2)
    R.stop()