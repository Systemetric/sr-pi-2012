import time
from lib.twowheeledrobot import TwoWheeledRobot

class CompassRobot(TwoWheeledRobot):
    class CompassThread(threading.Thread):
        def __init__(self, robot):
            threading.Thread.__init__(self)
            self.robot = robot
            self.targetHeading = 0
            self.speed = 0
            self.enabled = True
            
        def run(self):
            while True:
                if self.enabled:
                    heading = self.robot.compass.heading
                    error = float(self.targetHeading - heading)

                    correctBy = error / 2
                    
                    self.robot.drive(speed = self.speed, steer = correctBy)
                time.sleep(0.05)
                
            
        def onTarget(self, tolerance = 5):
            return math.fabs(float(self.targetHeading - heading)) < tolerance

    def __init__(self):
        TwoWheeledRobot.__init__(self)
        try:
            self.compass = Compass()
        except Exception, c:
            self.end(message = str(c))
        self.regulator = CompassThread(self)
        
    @property
    def regulate(self):
        return self.regulatorThread.enabled
        
    @regulate.setter
    def regulate(self, value):
        self.regulatorThread.enabled = value
         
    def rotateTo(self, heading):
        regulate = True;
        regulator.speed = 0
        regulator.targetHeading = heading
        
        while not regulator.onTarget():
            time.sleep(0.05)
        
    def rotateBy(self, angle):
        regulate = True
        regulator.speed = 0
        self.rotateTo(self.compass.heading + angle)
        
    def setSpeed(self, speed):
        regulate = True
        regulator.speed = speed