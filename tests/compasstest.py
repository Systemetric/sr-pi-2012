import time
from systemetricRobot import SystemetricRobot

def main():
    R = SystemetricRobot()
    target = 0
    
    while True:
        heading = R.compassHeading
        
        error = target - heading 
        while error >= 180:
            error -= 360
        while error < -180:
            error += 360
            
        print heading
        R.turn(error/2)
        time.sleep(0.2)