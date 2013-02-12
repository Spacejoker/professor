from cube import *
from collections import deque
import random
from copy import copy, deepcopy

class Block:
	inner_1x1 = 0 
	inner_2x1 = 1
	inner_2x2 = 2
	inner_3x1 = 3
	inner_3x3 = 4
	inner_3x2 = 5

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

	def parse_algo(self):
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
			c = cmd[:-1].split('(')
			rule = self.parse_rule(c[1])
			if c[0] == "+":
				self.rules.append(rule)
			else:
				self.rules.remove(rule)

		print 'Next step in algo parsed, current rules are: ', self.rules

	def next_move(self):
		#if we have a prepared move in stock just feed that one
		if self.test_cube():
			print "no need to do anything"
			return ' '

		if len(self.queued_moves) == 0:
			self.make_queue()

		if len(self.queued_moves) > 0:
			print "queue before move: ", self.queued_moves
			return self.queued_moves.popleft()
		else:
			return ' '

	def parse_rule(self, rule):
		parts = rule.split(',')
		parts = map(lambda x: x.strip(), parts)
		
		m = {
			'1x1' : Block.inner_1x1,
			'2x1' : Block.inner_2x1,
			'2x2' : Block.inner_2x2,
			'3x1' : Block.inner_3x1,
			'3x3' : Block.inner_3x3,
			'3x2' : Block.inner_3x2
		}

		size = m[parts[1]]
		return (parts[0], size, parts[2], parts[3] == 'Correct')

	def rev_seq(self, s):
		s.reverse()
		for i, m in enumerate(s):
			if(s[i][-1:] == '\''):
				s[i] = m[:-1]
			else:
				s[i] = m + '\''
		

	def make_queue(self):
		que = deque()
		mods = self.allowed_sequences
		c = self.cube
		done = False
		if self.test_cube():
			print "no need to make queue, got skip"
			return
		for m in mods:
			que.append(m)

		while len(que) > 0:
			seq = que.popleft()
			s = seq.split(" ")
			if len(s) > 5:
				continue
			#compare = deepcopy(c.state)
			c.rotate(s)
				
			if self.test_cube(): 
				done = True
				
			#undo what we did to the mutable cube, then revert tho sequence to the correct one
			self.rev_seq(s)
			c.rotate(s)
			
			self.rev_seq(s)

			#for id, row in enumerate(c.state):
			#	if(row != compare[id]):
			#		print "Problem detected, ", s

			if done == True :
				for c in s:
					self.queued_moves.append(c)
				print "new queue: ", self.queued_moves
				return

			#continue the bfs
			for m in mods:
				que.append( seq + ' ' + m)
	

	def test_cube(self, p=False):
		
		#color by color, just D for now:
		inner_1x1 = [[7],[11],[13],[17]]
		inner_2x1 = [[6,7], [7,8], [8,13], [13,18], [6,11], [11,16],[16,17],[17,18]]
		inner_2x2 = [[6,7,11], [7,8,13], [11,16,17], [13,17,18]]
		inner_3x1 = [[6,7,8],[6,11,16],[16,17,18],[8,13,18]]
		inner_3x3 = [[6,7,8,11,13,16,17,18]]
		inner_3x2 = []

		for sub in inner_3x1:
			tmp = []
			tmp.extend(inner_3x3[0])
			
			for c in sub:
				tmp.remove(c)
			inner_3x2.append(tmp)

		#for each face, examine the stickers with the wanted color

		num_blocks = []
		for i in range(0,6):
			num_blocks.append([0,0])

		for face in range (0,6):
			f = self.cube.state[face]
			used = []
			db = []	
			stickers = self.get_stickers(f, 'D')
			stickers = filter(lambda x: x in inner_3x3[0], stickers)
		
			#examine what we have on each side, one hit is enough since we never need 2 free 2x1 or 3x1 blocks in an incorrect position
			#3x3 only D
			#3x2
			#3x1
			#2x2 only D
			if face == Face.D:
				for cand in inner_2x2:
					if len(set(cand) & set(stickers)) == len(cand) and len(set(cand) & set(used)) == 0:
						num_blocks[Block.inner_2x2][0] += 1
						num_blocks[Block.inner_2x2][1] += 1
						used.extend(cand)
						print cand

			#2x1
			for cand in inner_2x1:
				if len(set(cand) & set(stickers)) == len(cand) and len(set(cand) & set(used)) == 0:
					num_blocks[Block.inner_2x1][1] += 1
					if face == Face.D:
						num_blocks[Block.inner_2x1][0] += 1
					used.extend(cand)

			#1x1 - only interesting on D
			if face == Face.D:
				for cand in inner_1x1:
					if len(set(cand) & set(stickers)) == len(cand):# and len(set(cand) & set(used)) == 0:
						num_blocks[Block.inner_1x1][0] += 1
						num_blocks[Block.inner_1x1][1] += 1
						used.extend(cand)
					
		if p:
			print num_blocks
		
		for r in self.rules:
			corr_id = 1
			if r[3]:
				corr_id = 0
			if( num_blocks[r[1]][corr_id] > 0):
				num_blocks[r[1]][corr_id] -= 1
				if(corr_id == 0):
					num_blocks[r[1]][1] -= 1

			else:
				return False

		return True
		#self.cube.state[face][sticker]

	def get_stickers(self, face, color):
		ret = []

		for id, sticker in enumerate(face):
			if sticker == Face_Lookup[color]:
				ret.append(id)

		return ret

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
	
