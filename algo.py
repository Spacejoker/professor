from cube import *
from collections import deque
import random

class Imported_Algo():
	def __init__(self, cube, filename):
		self.cube = cube
		file = open(filename, 'r')
		self.algo_steps = deque()
		for line in file.readlines():
			self.algo_steps.append(line[:-1]) #skip the newline
		self.allowed_sequences = []
		self.rules = []
		self.queued_moves = deque()

	def get_remaining_steps(self):
		return self.algo_steps

	def next_move(self):
		#if we have a prepared move in stock just feed that one
		if len(self.queued_moves) > 0:
			return self.queued_moves.popleft()
	
		#continue parsing the algorithm lines
		next_line = self.algo_steps.popleft()
		split = next_line.split('#')

		#handle setting up of allowed  moves
		while split[0] in ['set_moves', 'set_search_moves']:
			new_seq = split[1].split(',')
			if split[0] == 'set_moves':
				self.allowed_sequences = new_seq
			elif split[0] == 'set_search_moves':
				self.search_moves = new_seq
			print new_seq
			split = self.algo_steps.popleft().split('#')


		if split[0] == 'done':
			print 'algorithm done, you should be happy now'
			return ' '
	
		#handle a change of requirements
		
		commands = split[1].split('|')
		for cmd in commands:
			print cmd
			c = cmd[:-1].split('(')
			rule = self.parse_rule(c[1])
			if c[0] == "+":
				self.rules.append(rule)
				print "Add ", rule
			else:
				self.rules.remove(rule)
				print "Remove ", rule
		print "current rules: ", self.rules
		#search for a way of making these requirements come true
		
		return 'r'

	def parse_rule(self, rule):
		parts = rule.split(',')
		print parts
		size = parts[1].split('x')
		print size
		return (parts[0], (size[0],size[1]), parts[2], parts[3] == 'Correct')

class Sample_Algo():
	def __init__(self, cube):
		self.cube = cube
		self.steps = [[((Face.D,7),Face.D)], 
			[((Face.D, 6), Face.D)],
			[((Face.D, 11), Face.D)],
			[((Face.D, 8), Face.D), ((Face.D, 13), Face.D)],]
		self.done = []
		self.queue = deque()

	def test_cube(self, done):
		c = self.cube
		for item in done:
			#print item
			if self.cube.get(item[0]) != item[1]:
				return False
		return True

	def make_queue(self):
		print "making queue, total target is ", self.done
		que = deque()
		mods = ['r','f','l','u','d','b','D']
		c = self.cube
		done = False
		for m in mods:
			que.append(m)
		while len(que) > 0:
			seq = que.popleft()
			s = seq.split(" ")
			if len(s) > 5:
				continue
			c.rotate(s)
				
			if self.test_cube(self.done) and self.test_cube(self.steps[0]):
				print "already done: ", self.done
				done = True

			s.reverse()
			for i, m in enumerate(s):
				if(s[i][-1:] == '\''):
					s[i] = m[:-1]
				else:
					s[i] = m + '\''
			c.rotate(s)

			if done == True :
				for c in s:
					self.queue.append(c)
				return
			for m in mods:
				que.append( seq + ' ' + m)
		print "found sequence ", que
		
	def next_move(self):
		print "queue: ", self.queue
		if len(self.queue) > 0:
			return self.queue.popleft()
		else:
			print self.steps[0]
			self.done.extend(self.steps[0])
			if self.steps > 0:
				while len(self.queue) == 0:
					self.make_queue()
					if len(self.queue) == 0:
						self.cube.rotate([Turns[random.randint(0,5)]])
				self.steps = self.steps[1:]
			else:
				print "done"
				self.queue.append(" ")
				
		return self.queue.popleft()
	
