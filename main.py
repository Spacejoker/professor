import os
import random
import pygame
import time
import itertools
from pygame.locals import *
from cube import *
from algo import Imported_Algo, Rule_Lookup
import pymongo
from graphics import *

class Mode():
	MENU = 1
	SIMULATION = 2

class Constants():
	WINDOW_WIDTH = 1200
	WINDOW_HEIGHT = 630
	STICKER_SIZE = 30

class Persist():
	def __init__(self):
		conn = pymongo.Connection('localhost', 27017)
		self.db = conn['cube']	
		self.result = self.db.result
	def save(self, data):
		print "items in db: "
		for i in self.result.find():
			print i
		self.result.save(data)

class Stats():
	def __init__(self):
		self.nr_moves = 0
		self.nr_search_steps = 0
		self.current_nr_search_moves = 0
		self.persist = Persist()

	def reset(self):
		self.nr_moves = 0
		self.nr_search_steps = 0
		self.current_nr_search_moves = 0
	
	def save(self, data):
		chunk = { 'state' : data,
			'nr_moves' : self.nr_moves,
			'nr_search_steps' : self.nr_search_steps }
		self.persist.save(chunk)
class Scrambler():
	@staticmethod	
	def gen_scramble(export = False):
		scramble = ""
		for x in range (0,60):
			turn = Turns[random.randint(0,5)]
			mod = random.randint(0,5)
			if(mod % 3 == 0):
				turn = turn.lower()
			if(mod % 3 == 1):
				turn = turn + 'w'
			if(mod >3):
				turn += 'p'
			scramble += turn  + " "
		if export:
			f = open('scramble.txt', 'w')
			f.write(scramble)
			f.close()
		print scramble
		return scramble

	@staticmethod
	def gen_edge_destroy():
		tot = ""
		for x in range(0, 60):
			setup = 'u'
			move = 'R U Rp'
			undo = 'up'
			tot += setup + " " + move + " " + undo + " "
			for y in range(0,20):
				tot += Turns[random.randint(0,5)] + " "
		print tot
		return tot
	
class Simulation():
	def __init__(self):
		self.mode = Mode.MENU
		self.running = True
		pygame.init() 
		self.g = Graphics()
		self.algo_file = 'standard.algo'
	pass

	
	def menu(self):
		while self.mode == Mode.MENU:
			self.g.draw_menu()
			event = pygame.event.wait()

			if event.type == pygame.KEYDOWN:
				self.mode = Mode.SIMULATION
		pass
	#Main application loop
	def loop(self):
		self.c = Cube()
		self.s = Stats()

		prim = False
		w = False

		self.algo = Imported_Algo(self.c, 'standard.algo', self.s)
		font = pygame.font.SysFont("monospace", 15)
		run_to_comment = False

		#handle input and draw graphics
		while self.running: 
			if self.s.current_nr_search_moves > 2:
				print "fail"
				self.reset_cubes()
			s = self.s
			c = self.c
			g = self.g
			algo = self.algo

			g.draw_cube(c, self.algo, s)
			keymap = {}
			event = pygame.event.wait()

			if event.type == pygame.KEYDOWN:
				#handles dvorak
				keymap[event.scancode] = event.unicode
				cmd = event.unicode

				if w:
					cmd = cmd.upper()
					cmd += 'w'

				if(prim):
					cmd += 'p'

				if event.unicode == 'y':
					prim = not prim

				if event.unicode == 'w':
					w = not w

				if event.unicode.upper() in Turns:	
					c.rotate([cmd])

				if event.unicode == '1':
					self.algo.parse_algo()
					next_move = ' '
					done = False

					while True:
						c.rotate([next_move])
						next_move = algo.next_move()
						if next_move != ' ':
							s.nr_moves += 1
						g.draw_cube(c, algo, s)
						if next_move == None or next_move == ' ' or next_move == '' and (algo.queued_moves) == 0:
							if done:
								print "Done with this auto-step, back to manual!"
								break;
							split = algo.algo_steps[0].split("#")
							if split[0] == 'comment':
								s.save(split[1])
								done = True
							else:
								algo.parse_algo()
								g.draw_cube(c, algo, s)
						time.sleep(0.1)

				if event.unicode == ' ':
					print "Next move: ", algo.next_move()

				if event.unicode == 'q':
					c.rotate([algo.next_move()])
				
				if event.unicode == '[':
					c.rotate(Scrambler.gen_edge_destroy().split(' '))

				if event.unicode == '0':
					c.rotate(Scrambler.gen_scramble().split(' '))

				if event.unicode == '`':
					while(len(algo.queued_moves) > 0):
						c.rotate(algo.next_move())


				if event.unicode == '7':
					self.algo_file = 'edge.algo'
					self.reset_cube()

				if event.unicode == '9':
					self.reset_cube()
				#Debug controls
				if event.unicode == 'o':
					print "Recalculating moves needed"
					print "Rules to obey:"
					for r in algo.rules:
						print r
					algo.queued_moves.clear()
					algo.make_queue()

				if event.unicode == 'e':
					print algo.queued_moves

				if event.unicode == 'a':
					algo.parse_algo()
					
				if event.unicode == '.':
					t = time.time()
					algo.test_cube(True)
					diff = time.time() - t
				
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					self.running = False

		pygame.quit()

	def reset_cube(self):
		self.c = Cube()
	  	self.s.reset()
		print 'loading: ' + self.algo_file
		self.algo = Imported_Algo(self.c, self.algo_file, self.s)

if __name__ == '__main__':
	sim = Simulation()
	while True:
		if sim.mode == Mode.MENU:
			sim.menu()
		else:
			sim.loop()
			sim.mode = Mode.MENU

