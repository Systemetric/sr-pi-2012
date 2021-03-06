# This file is part of systemetric-student-robotics.

# systemetric-student-robotics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# systemetric-student-robotics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with systemetric-student-robotics.  If not, see <http://www.gnu.org/licenses/>.


import gtk, gobject, cairo, math, threading, time
from systemetric.mapping.arenamaps import CompetitionArenaMap, S007ArenaMap
from libs.pyeuclid import *
from systemetric.map import Map
from systemetric.timer import Timer
import random

class Screen(gtk.DrawingArea):
	""" This class is a Drawing Area"""
	def __init__(self):
		super(Screen,self).__init__()
		self.connect("expose_event", self.do_expose_event)
		gobject.timeout_add(50, self.tick)

	def tick(self):
		## This invalidates the screen, causing the expose event to fire.
		self.queue_draw()
		return True # Causes timeout to tick again.

	## When expose event fires, this is run
	def do_expose_event(self, widget, event):
		self.cr = self.window.cairo_create()
		## Call our draw function to do stuff.
		self.draw(*self.window.get_size())

class MapRenderer(Screen):
	def __init__(self, map):
		super(MapRenderer, self).__init__()
		self.map = map

		def update():
			print "update"
		
		self.map.onUpdate += update

	def draw(self, w, h):
		self.cr.save()
		self.initScaling(self.cr, w, h)
		self.drawArena(self.cr)
		self.drawTokens(self.cr)
		self.drawRobot(self.cr)
		self.cr.restore()


	def initScaling(self, cr, w, h):
		#Move to the middle of the screen
		cr.translate(w/2, h/2)

		margin = 10 #px
		actualWidth, actualHeight = self.map.arena.size.xy
		scaleFactor = min( (w - 2*margin) /actualWidth, (h - 2*margin)/actualHeight)

		#Scale so that a measurement of 1 corresponds to one meter. Flip Y axis to give normal coords
		cr.scale(scaleFactor, -scaleFactor)

		#Move the middle of the arena to the middle of the screen
		cr.translate(-actualWidth / 2, -actualHeight / 2)

	def drawRobot(self, cr):
		cr.save()

		#Convert matrix to the cairo format
		locInfo = self.map.robot
		if locInfo:
			p = locInfo.location
			r = locInfo.heading.radians

			cr.translate(p.x, p.y)
			cr.rotate(r)

			cr.move_to(0.25, 0)
			cr.line_to(0.25, 0.25)
			cr.line_to(-0.25, 0.25)
			cr.line_to(-0.25, 0)
			cr.arc(0, 0, 0.25, math.pi, 2*math.pi)

			cr.set_source_rgb(0.5, 0.5, 0.5) #gray
			cr.fill()

			cr.set_line_width(max(cr.device_to_user_distance(1,1)))
			cr.set_source_rgb(0.25, 0.25, 0.25) #gray
			cr.stroke()

		cr.restore()

	def drawArena(self, cr):
		cr.save()

		#Draw the background
		cr.set_source_rgb(1, 1, 1) #white
		cr.rectangle(0, 0, self.map.arena.size.x, self.map.arena.size.y)
		cr.fill()

		#Draw the markers
		cr.set_line_width(max(cr.device_to_user_distance(2, 2))) #2px
		cr.set_source_rgb(1, 0, 0) #red
		for key, marker in self.map.arena.iteritems():
			cr.move_to(marker.left.x, marker.left.y)
			cr.line_to(marker.right.x, marker.right.y)
		cr.stroke()

		cr.restore()

	def drawTokens(self, cr):
		cr.save()
		cr.set_font_size(max(cr.device_to_user_distance(10, 10)))
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		#Draw the tokens as 10cm circles, and write the id of each token next to it
		for id, entity in enumerate(self.map.tokens):
			pos = entity.position
			if pos:

				cr.save()
				cr.translate(pos.x, pos.y)

				cr.set_source_rgba(0, 0, 1, entity.reliability)
				
				cr.arc(0, 0, 0.05, 0.0, 2 * math.pi)
				cr.fill()

				text = str(id)
				cr.scale(1, -1)
				x, y, width, height = cr.text_extents(text)[:4]
				cr.move_to(0.1, height/2)
				cr.show_text(text)

				cr.restore()
				
		cr.restore()

	def startInNewWindow(self):
		self.show()

		window = gtk.Window()
		window.connect("delete-event", gtk.main_quit)
		window.set_title("Map")
		window.add(self)
		window.present()

		gtk.gdk.threads_init()
		t = threading.Thread(target=gtk.main)
		t.start()

import systemetric

def main():
	R = systemetric.Robot()
	m = Map(arena=CompetitionArenaMap())
	mr = MapRenderer(m)
	mr.startInNewWindow()

	while True:
		with Timer("Profiling") as t:
	 		with t.event("see"):       see = R.see()
			with t.event("processed"): processed = see.processed()
			with t.event("update"):    m.updateEntities(processed)

	m.fakeUpdateEntities(
		tokens={2: Point2(1, 1), 12: Point2(0.5, 1.75), 0: Point2(3, 1.25)},
		transform=Matrix3.new_translate(2, 2.5).rotate(math.pi/3)
	)

	time.sleep(2)

	m.fakeUpdateEntities(
		tokens={2: Point2(1.5, 1.75), 13: Point2(0.5, 0.75), 5: Point2(3.5, 2.25)},
		transform=Matrix3.new_translate(4, 2.5).rotate(math.pi*2/3)
	)