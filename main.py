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
import datetime

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
		#for i in self.result.find():
			#jprint i
		self.result.save(data)

	def dump_state(self, data):
		problem_state = self.db.problem_state
		problem_state.remove()
		problem_state.save(data)
		print "dumped state!"

	def list_problems(self):
		probs = self.db.problem_state.find()

		for p in probs:
			print p

	def get_first_problem(self):
		probs = self.db.problem_state.find()
		print "Rules:"
		for rule in probs[0]['rules']:
			print rule
		print probs[0]['stored'], " pieces stored"
		print probs[0]['mode'], " is the mode"
		return probs[0]

	def clear_problems(self):
		self.db.problem_state.remove()

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
		self.c = Cube()
		self.s = Stats()
		self.algo = Imported_Algo(self.c, 'standard.algo', self.s)
		self.inputHandler = {
				'0' : self.scramble,
				'1' : self.to_next_comment,
				'j': self.s.persist.list_problems,
				'q': self.next_move, #c.rotate([algo.next_move()])
				'[': self.destroy_edges, #c.rotate(Scrambler.gen_edge_destroy().split(' '))
				'k': self.load_state,
				'7': self.load_edge_algo,
				'9' : self.reset_cube,
				'o' : self.recalc,
				'e' : self.show_queued_moves,
				'a' : self.algo.parse_algo}

	def menu(self):
		while self.mode == Mode.MENU:
			self.g.draw_menu()
			event = pygame.event.wait()

			if event.type == pygame.KEYDOWN:
				self.mode = Mode.SIMULATION
	def recalc(self):
		self.algo.load_state(self.s.persist)

	def show_queued_moves(self):
		print self.algo.queued_moves

	def next_move(self):
		self.c.rotate([algo.next_move()])

	def destroy_edges(self):
		self.c.rotate(Scrambler.gen_edge_destroy().split(' '))

	def list_problems(self):
		self.s.persist.list_problems()

	def load_edge_algo(self):
		self.algo_file = 'edge.algo'
		self.reset_cube()
	
	def load_state():
		self.algo.load_state(self.s.persist)

	def scramble(self):
		self.c.rotate(Scrambler.gen_scramble().split(' '))

	#Main application loop
	def loop(self):

		prim = False
		w = False
		batch = False

		font = pygame.font.SysFont("monospace", 15)
		run_to_comment = False
		self.reset = False

		#handle input and draw graphics
		while self.running: 
			s = self.s
			c = self.c
			g = self.g
			algo = self.algo

			if self.reset:
				print self.reset, " is the reset state"
				self.reset_cube()
				c.rotate(Scrambler.gen_scramble().split(' '))
				self.reset = False
		
			if batch:
				print algo.rules
				self.to_next_comment(c, algo, s)
				continue

			g.draw_cube(c, self.algo, s)
			keymap = {}
			event = pygame.event.wait()

			if event.type == pygame.KEYDOWN:
				#handles dvorak
				keymap[event.scancode] = event.unicode
				cmd = event.unicode
				if event.unicode in self.inputHandler:
					self.inputHandler[event.unicode]()
				elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					self.running = False
				elif event.unicode == '?':
					print "Commands: \n", self.inputHandler
				elif event.unicode.upper() in Turns:	
					c.rotate([cmd])
				else:
					print "No mapping for key: ", event.unicode


				#if w:
					#cmd = cmd.upper()
					#cmd += 'w'

				#if(prim):
					#cmd += 'p'

				#if event.unicode == 'y':
					#prim = not prim

				#if event.unicode == 'w':
					#w = not w


		pygame.quit()

	def reset_cube(self):
		self.c = Cube()
		self.s.reset()
		print 'loading: ' + self.algo_file
		self.algo_file = 'standard.algo'
		self.algo = Imported_Algo(self.c, self.algo_file, self.s)

	def to_next_comment(self):
		c = self.c
		algo = self.algo
		s = self.s
		self.algo.parse_algo()
		next_move = ' '
		done = False
		g = self.g
		prim = False

		while True:
			c.rotate([next_move])
			next_move = algo.next_move()
			if next_move == 'fail':
				print 'reseting cube due to error'
				self.reset = True
				break

			g.draw_cube(c, algo, s)
			
			if next_move == None or next_move == ' ' or next_move == '' and (algo.queued_moves) == 0:
				if done:
					print "Done with this auto-step, back to manual!"
					break;
				split = algo.algo_steps[0].split("#")
				if split[0] == 'comment':
					s.save(split[1])
					done = True
				if split[1] == 'done':
					print 'reseting cube since the algo is complete'
					self.reset = True
					break
				else:
					algo.parse_algo()
					g.draw_cube(c, algo, s)
			else :
				s.nr_moves += 1
				if prim:
					time.sleep(0.1)

if __name__ == '__main__':
	sim = Simulation()
	while True:
		if sim.mode == Mode.MENU:
			sim.menu()
		else:
			sim.loop()
			sim.mode = Mode.MENU

