import systemetric
import time
from systemetric import Bearing

R = systemetric.Robot()
A = systemetric.Arm()

#Whether searching for cubes or a bucket
followState = "cube"
#Any cubes already found
foundCubes = set()

#Distance between each step to move towards a bucket in meters
#(e.g. if 2 meter step, every 2 meters it will check location of bucket again)
STEPDIST = 1

while True:
	#Find all markers it can see
	markers = R.see(res=(1280,1024)).processed()

	#If finding cubes
	if followState == "cube":
		print "Reading markers"
		#Get only the unique (not found already) tokens
		tokens = [m for m in markers.tokens if m.id not in foundCubes]
		
		# Are there any tokens?
		if tokens:
			if abs(tokens[0].center) < 0.45:
				#If close enough to cube to grab then 'grab'
				foundCubes.add(tokens[0].id)
				print "Found cube #%d!" % tokens[0].id
				A.grabCube(wait=True)
			else:
				#Else attempt to drive to cube
				R.driveTo(tokens[0].center, gap=0.2)
		else:
			#Couldn't find any markers
			print "No Marker..."
			
			# Spin 30 degrees clockwise
			R.rotateBy(30, fromTarget=True)
			
			# Disable heading correction
			R.stop()

		if len(foundCubes) > 1:
			#If found 2 or more cubes, start finding bucket
			followState = "bucket"
			#Reset found cubes
			foundCubes = set()

	elif followState == "bucket":
		#If finding bucket, get all seen buckets
		buckets = markers.buckets

		if buckets:
			#If any buckets found, target first bucket in list
			b = buckets[0]

			#Choose the best point on the bucket to align to
			target = min(b.desirableRobotTargets, key=abs)

			#Print bucket information
			print "Bucket seen at %s" % b.center
			print "Driving to %s" % target

			if abs(target) < 0.1:
				#Nearly at the target, don't move any more
				print "Nearly there"
				angle = Bearing.ofVector(b.center)


				if abs(angle) > 5:
					#Need to turn a bit more to face the bucket
					print "Off by %s" % angle
					R.rotateBy(angle)

				#Angle is ok now - go for it!
				print "Success!"
				R.drive(15)
				time.sleep(1)
				R.stop()
				R.power.beep(440, 1)
				
				#Start following cubes again, skip the rest of the loop
				followState = "cube"
				continue

			else:
				if abs(target) > STEPDIST:
					#Too far from target - limit movement
					target = STEPDIST * target.normalize()

				#One more movement
				R.driveTo(target)
				time.sleep(0.1)

				#Turn to face where we think the bucket should be, so we can see it next loop
				targetFacing = b.center - target
				angleDifference = Bearing.ofVector(targetFacing) - Bearing.ofVector(target)
				print "Turning to face bucket again"
				R.rotateBy(angleDifference)
				R.stop()
		
		time.sleep(1)
		R.rotateBy(20)

		R.stop()