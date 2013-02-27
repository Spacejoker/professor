import os, sys
from collections import deque
from pygame.locals import *
from cube import *
from algo import Imported_Algo, Rule_Lookup
import datetime
from helper import Formatter
from persist import Persist
import time

class Solver():
	def __init__(self):
		self.persist = Persist()
		pass

	def solve(self, algo_name, scramble):
		c = Cube()	
		
		steps = deque()
		dbalgo = self.persist.get_algo(algo_name)
		print dbalgo.keys()

		for line in dbalgo['steps']:
			steps.append(line) #skip the newline
		algo = Imported_Algo(c, algo_steps=steps)

		move_cnt = 0	
		solution = []
		for move in scramble:
			c.rotate(move)

		done = False
		success = False
		t0 = time.time()

		while True:

			fst = True
			while len(algo.queued_moves) > 0 or fst:
				fst = False
				move = algo.next_move()
				if move == 'fail':
					done = True

				if move != None and move != ' ' and move != '':
					move_cnt += 1
					c.rotate([move])
					solution.append(move)

			split = algo.algo_steps[0]

			if split[0] == 'comment':
				if split[1] == 'done':
					done = True
					success = True
				print "Comment:", split[1]
			
			if done:
				break
			#next step in algo		
			algo.parse_algo()

		result = {'scramble' : scramble,
			'move_cnt' : move_cnt,
			'success' : success,
			'rules' : algo.rules,
			'moves' : solution,
			'name' : algo_name,
			'time' : time.time() - t0}

		return result

