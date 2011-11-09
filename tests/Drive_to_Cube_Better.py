from sr import *
import time
import math
from systemetricRobot import SystemetricRobot

def main():
    R = SystemetricRobot()
    
    speed = 50
    
    while True:
        #Get only the tokens
        markers = [marker for marker in R.see() if marker.info.marker_type == MARKER_TOKEN] #getting the valid QR code
        
        if len(markers) != 0:        #if there is A valid QR there...
            print "Saw the marker"
            angle = markers[0].centre.polar.rot_y    #set the angle of the object (from center)
            if math.fabs(angle) < 10:                #set angle to an absolute value, then drive @ angle
                R.drive(speed)
            else:                                    #else, stop
                R.turn(=angle)
                #time.sleep(0.25)
                R.stop()
            
            print(angle)
            
        else:
            R.turn(20)
            sleep(0.2)
            r.stop()
            
        #else:
        #    print "No marker"
        #    R.turn(5)
        #    time.sleep(0.25)
        #    R.stop()
        