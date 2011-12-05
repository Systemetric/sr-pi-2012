import sys
import math
import os
import time
import sr
from collections import namedtuple
import json

from libs.pyeuclid import *
from compassrobot import CompassRobot
from compass import Compass

config = json.load(open('config.json'))

Marker = namedtuple("Marker", "vertices normal location")
Markers = namedtuple("Markers", "tokens robots arena buckets")
Token = namedtuple("Token", "markers id timestamp location")

#info about the markers. Used in sr.vision
MarkerInfo = namedtuple( "MarkerInfo", "code marker_type offset size" )

DIE_HORRIBLY = config.get('killCode') or 228 #special marker

class Robot(CompassRobot):
	'''A class derived from the base 'Robot' class provided by soton'''	 
	def __init__(self):
		#Get the motors set up
		CompassRobot.__init__(self)
		
		#set up the serial connection to the mbed
		try:
			self.compass = Compass()
		except Exception, c:
			self.end(message = str(c))
		
		#Camera orientation							
		self.cameraMatrix = Matrix4.new_rotate_euler(	# https://github.com/dov/pyeuclid/blob/master/euclid.txt (line 385)
			heading = 0,								 # rotation around the y axis
			attitude = -10,							  # rotation around the x axis
			bank = 0									 # rotation around the z axis
		) 
		
		sr.vision.marker_luts['dev'][DIE_HORRIBLY] = MarkerInfo(
			code = DIE_HORRIBLY,
			marker_type = None,
			offset = None,
			size = 1 #Errors if 0
		)
		#Position and orientation of the robot
		self.robotMatrix = Matrix3()
	
   
	#deprecated
	@property 
	def compassHeading(self):
		return self.compass.heading
	
	def getMarkersById(self, *args, **kargs):
		'''Get all the markers, grouped by id.
		For example, to get the token with id 1, use:
		
			markers = R.getMarkersById()
			
			# Check if token 0 is visible
			if 0 in markers.tokens:
				markersOnFirstToken = markers.tokens[0]
		'''
		markers = self.see(*args, **kargs)
		markersById = Markers(tokens={}, arena={}, robots={}, buckets={})
		
		for marker in markers:
			id = marker.info.offset
			type = marker.info.marker_type
			
			# What type of marker is it?
			if type == sr.MARKER_TOKEN:
				list = markersById.tokens
			elif type == sr.MARKER_ARENA:
				list = markersById.arena
			elif type == sr.MARKER_ROBOT:
				list = markersById.robots
			else:
				list = markersById.buckets
			
			#Is this the first marker we've seen for this object?
			if not id in list:
				list[id] = []
				
			#Add this marker to the list of markers for this object
			list[id].append(marker)
		
		return markersById
	
	def visibleCubes(self):
		markersById = self.getMarkersById()
		
		tokens = []
		# For each token
		for markerId, markers in markersById.tokens.iteritems():
			newmarkers = []
			# Convert all the markers to a nicer format, using pyeuclid
			for marker in markers:
			
				vertices = []
				# We only care about 3D coordinates - keep those
				for v in marker.vertices:
					vertices.append(Point3(
						v.world.x,
						v.world.y,
						v.world.z
					))
				
				# Calculate the normal vector of the surface
				edge1 = vertices[0] - vertices[1]
				edge2 = vertices[2] - vertices[1]
				normal = edge1.cross(edge2).normalize()
				
				# Keep the center position
				location = marker.center.world

				newmarkers.append(Marker(
					location = Point3(location.x, location.y, location.z),
					normal = normal,
					vertices = vertices
				))
			
			token = Token(
				markers = newmarkers,
				timestamp = marker[0].timestamp,
				id = markerId,
				location = self.cameraMatrix * newmarkers[0].center
			)
			# Take into account the position of the robot
			# token.location = self.robotMatrix * token.Location
			tokens.append(token)
		
		#sort by distance, for convenience
		tokens.sort(key=lambda m: m.location.magnitude())
		return tokens
		
	def see(self, *args, **kw):
		markers = sr.Robot.see(self, *args, **kw)
		for marker in markers:
			if marker.info.code == DIE_HORRIBLY:
				self.end("Terminated by marker %d" % DIE_HORRIBLY, error=False)
			   
		return markers
		
	def driveDistance(self, distInMetres):
		SPEED = .575
		self.setSpeed(math.copysign(100, distInMetres))
		time.sleep(abs(distInMetres) / SPEED)
		self.stop()
		
	def end(self, message = 'robot stopped', error = True, shutdown = False):
		'''Kill the robot in the nicest way possible'''
		print message
		
		#stop the motors
		self.stop()
		#beep if error
		if error:
			self.power.beep([(440, 1), (220, 1), (880, 1)])
		else:
			self.power.beep([(262,2), (440, 2),(524, 2)])	
		#end the program with an exit code
		if shutdown:
			os.system('shutdown -P now')
		else:
			sys.exit(int(error))