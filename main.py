import os
import random
import pygame
import time
import itertools
from pygame.locals import *
from cube import *
from algo import Imported_Algo, Rule_Lookup

class Mode():
	MENU = 1
	SIMULATION = 2

class Constants():
	WINDOW_WIDTH = 1200
	WINDOW_HEIGHT = 630
	STICKER_SIZE = 30

class Stats():
	def __init__(self):
		self.nr_moves = 0
		self.nr_search_steps = 0
	def reset(self):
		self.nr_moves = 0
		self.nr_search_steps = 0
class Scrambler():
	@staticmethod	
	def gen_scramble():
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
		f = open('scramble.txt', 'w')
		f.write(scramble)
		f.close()

		return scramble

class Graphics():

	def __init__(self):
		self.window = pygame.display.set_mode((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)) 
		self.font = pygame.font.SysFont("monospace", 15)

	def draw_cube(self, cube, algo, stats):

		pygame.draw.rect(self.window, (0,0,0), (0,0,Constants.WINDOW_WIDTH,Constants.WINDOW_HEIGHT), 0)
		#label = self.font.render("Prim: " + str(prim) , 1, (255,255,0))
		#self.window.blit(label, (20,20))
		#label = self.font.render("w: " + str(w) , 1, (255,255,0))
		#self.window.blit(label, (20,40))

		for side in range(0, len(cube.state)):
			for id, sticker in enumerate(cube.state[side]):
				f = faces[side]
				color = faces[sticker]
				size = Constants.STICKER_SIZE
				pygame.draw.rect(self.window, color.color, (f.position[0] + Helper.get_x(id)*size, f.position[1] + Helper.get_y(id)*size, size-1,size-1), 0)	
		num = 1	
		for step in algo.algo_steps:
			if num > 7:
				break
			if step.split("#")[0] == "comment":
				label = self.font.render(str(num) + ": " + str(step.split("#")[1]), 1, (255, 0,0))
				self.window.blit(label, (500,100 + num*20))
				num += 1
		for id, rule in enumerate(algo.rules):
			display = Rule_Lookup[rule[1]] + ", sticker " + str(rule[2]) + " on "
			if rule[3] != None:
				display += "face  " + str(Turns[rule[3]])
			else:
				display += " any face"

			label = self.font.render(display, 1, (255, 0,0))
			self.window.blit(label, (800,120 + id*20))
		label = self.font.render("Allowed: " + str(algo.allowed_sequences), 1, (255, 255,255))
		self.window.blit(label, (400, 20))
		label = self.font.render("Nr moves: " + str(stats.nr_moves), 1, (255,255,255))
		self.window.blit(label ,(600, 600))

		label = self.font.render("Nr search steps: " + str(stats.nr_search_steps), 1, (255,255,255))
		self.window.blit(label ,(600, 550))

		pygame.display.flip() 
class Simulation():
	def __init__(self):
		self.mode = Mode.MENU
		pass
#Main application loop
	def loop(self):
		pygame.init() 
		c = Cube()
		g = Graphics()
		s = Stats()

		running = True
		prim = False
		w = False

		algo = Imported_Algo(c, 'standard.algo', s)
		font = pygame.font.SysFont("monospace", 15)
		run_to_comment = False

		while running: 
			g.draw_cube(c, algo, s)
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
				c.rotate([cmd])

				if event.unicode >= '1' and event.unicode <= '7':
					algo.parse_algo()
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
							if algo.algo_steps[0].split("#")[0] == 'comment':
								done = True
							else:
								algo.parse_algo()
								g.draw_cube(c, algo, s)
						time.sleep(0.1)

				if event.unicode == ' ':
					print "Next move: ", algo.next_move()
				if event.unicode == 'q':
					c.rotate([algo.next_move()])
				if event.unicode == '0':
					c.rotate(Scrambler.gen_scramble().split(' '))
				if event.unicode == '`':
					while(len(algo.queued_moves) > 0):
						c.rotate(algo.next_move())
				if event.unicode == '8':
					c = Cube()
					algo = Imported_Algo(c, 'top.algo', s)
				if event.unicode == '9':
					c = Cube()
					s.reset()
					algo = Imported_Algo(c, 'standard.algo', s)
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
					print "parsing next step in algo"
					algo.parse_algo()
				if event.unicode == '.':
					t = time.time()
					algo.test_cube(True)
					diff = time.time() - t
					print "time passed: ", diff
				if event.unicode == 'y':
					prim = not prim
				if event.unicode == 'w':
					w = not w
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					running = False

		pygame.quit()

if __name__ == '__main__':
	sim = Simulation()
	while True:
	if sim.mode == Mode.MENU:
		print 'ok'
		sim.mode = Mode.SIMULATION
	else:
		sim.loop()

