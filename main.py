import os, sys
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
from helper import Formatter

BATCH_SIZE = 10

class Mode():
	MENU = 1
	SIMULATION = 2

class Constants():
	WINDOW_WIDTH = 1200
	WINDOW_HEIGHT = 800
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

	def list_problems(self):
		probs = self.db.problem_state.find()
		for nr, p in enumerate(probs):
			if nr > 5:	
				print "=============================="
				print "Got a total of ", self.db.problem_state.count(), "problems"
				break
			print "Problem nr ", nr, "=================================="
			rules = p['rules']
			for rule in map(Formatter.rule_to_string, rules):
				if(rule != None):
					print rule
			print "Allowed sequences:", map(str, p['allowed_sequences'])
			print "Scramble:", map(str,p['scramble'])

	def get_first_problem(self):
		probs = self.db.problem_state.find()
		return probs[0]

	def clear_problems(self):
		self.db.problem_state.remove()

	def remove_first_problem(self):
		prob = self.db.problem_state.find()[0]
		self.db.problem_state.remove({'scramble' : prob['scramble']})

	def dump_state(self, algo):
		chunk = { 
				'all_commands' : algo.cube.all_commands,
				'scramble' : algo.cube.scramble,
				'rules' : algo.rules,
				"date": datetime.datetime.utcnow(),
				'mode' : algo.mode,
				'flip_algo' : algo.flip_algo,
				'allowed_sequences' : algo.allowed_sequences,
				'stored' : algo.stored
				}
		self.db.problem_state.remove({'scramble' : algo.cube.scramble})
		self.db.problem_state.save(chunk)
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
	def gen_3x3x3_scramble():
		tot = ""
		for x in range(0, 60):
			for y in range(0,20):
				tot += Turns[random.randint(0,5)] + " "
		print tot
		return tot

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
		self.batch = 0
		self.inputHandler = {
				'0' : self.scramble,
				'1' : self.to_next_comment,
				'2' : self.increment_batch,
				'j': self.s.persist.list_problems,
				'q': self.next_move, #c.rotate([algo.next_move()])
				'[': self.destroy_edges, #c.rotate(Scrambler.gen_edge_destroy().split(' '))
				']' : self.custom_scramble,
				'k': self.load_state,
				'6': self.show_rules,
				'7': self.load_edge_algo,
				'8': self.load_3x3_algo,
				'9' : self.load_std_algo,
				'o' : self.recalc,
				'e' : self.show_queued_moves,
				'a' : self.algo.parse_algo,
				'c' : self.s.persist.clear_problems,
				'g' : self.s.persist.remove_first_problem,
				'x' : self.scramble_from_fst_problem
				}

	def scramble_from_fst_problem(self):
		prob = self.s.persist.get_first_problem()
		self.scramble(map(str, prob['scramble']))

	def increment_batch(self):
		self.scramble()
		self.batch += BATCH_SIZE

	def show_rules(self):
		print self.algo.rules

	def menu(self):
		while self.mode == Mode.MENU:
			self.g.draw_menu()
			event = pygame.event.wait()

			if event.type == pygame.KEYDOWN:
				self.mode = Mode.SIMULATION
	def recalc(self):
		self.algo.load_state(self.s.persist)

	def custom_scramble(self):
		parity_scramble = "F r r B B U U l U U rp U U r U U F F r F F lp B B r r Fp"
		scramble_3x3 = Scrambler.gen_3x3x3_scramble()
		wr_scramble = "L2 Dp U L R B L R D D U B B Fp U Lp Rp Bp Fp D F Lp B B U U Rp Bp F F"
		scramble = wr_scramble
		self.scramble(scramble)

	def show_queued_moves(self):
		print self.algo.queued_moves

	def next_move(self):
		print 'move:', self.algo.next_move()
		self.c.rotate([self.algo.next_move()])

	def destroy_edges(self):
		self.c.rotate(Scrambler.gen_edge_destroy().split(' '))

	def list_problems(self):
		self.s.persist.list_problems()

	def load_3x3_algo(self):
		self.algo_file = '3x3.algo'
		self.reset_cube()

	def load_edge_algo(self):
		self.algo_file = 'edge.algo'
		self.reset_cube()

	def load_std_algo(self):
		self.algo_file = 'standard.algo'
		self.reset_cube()

	def load_state(self):
		self.algo.load_state(self.s.persist)

	def scramble(self, scramble_seq=None):
		if(scramble_seq == None):
			scramble_seq = Scrambler.gen_scramble().split(' ')
		self.c.rotate(scramble_seq)
		self.c.scramble = scramble_seq 

	def init_menu(self):
		pass

	#Main application loop
	def loop(self):

		prim = False
		w = False

		font = pygame.font.SysFont("monospace", 15)
		run_to_comment = False
		self.reset = False
	
		self.init_menu()
	
		#handle input and draw graphics
		while self.running: 
			s = self.s
			c = self.c
			g = self.g
			algo = self.algo
			if self.reset:
				print self.reset, " is the reset state"
				self.reset_cube()
				self.reset = False
				self.scramble()
		
			if self.batch > 0 and not pygame.event.peek(pygame.KEYDOWN):
				print algo.rules
				self.to_next_comment()
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
			pygame.event.clear()

		pygame.quit()

	def reset_cube(self):
		self.c = Cube()
		self.s.reset()
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
				self.batch -= 1
				self.s.persist.dump_state(self.algo)
				break

			g.draw_cube(c, algo, s)
			
			if next_move == None or next_move == ' ' or next_move == '' and (algo.queued_moves) == 0:
				if done:
					print "Done with this auto-step, back to manual!"
					break;

				split = algo.algo_steps[0].split("#")
				if split[0] == 'comment':
					print "comment!", split[1]
					s.save(split[1])
					done = True
					if split[1] == 'done':
						self.batch -= 1
						print 'reseting cube since the algo is complete'
						self.reset = True
						return
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

