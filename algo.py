from cube import *
from collections import deque
import random
from copy import copy, deepcopy
import time	

class Block:
	inner_1x1 = 0 
	inner_2x1 = 1
	inner_2x2 = 2
	inner_3x1 = 3
	inner_3x3 = 4
	inner_3x2 = 5
	inner_1x1_corner = 6

Rule_Lookup = {
		0 : 'inner_1x1',
		1 : 'inner_2x1',
		2 : 'inner_2x2',
		3 : 'inner_3x1',
		4 : 'inner_3x3',
		5: 'inner_3x2',
		6 : 'inner_1x1_corner'
	}
class Imported_Algo():
	def __init__(self, cube, filename, stats):
		self.cube = cube
		self.stats = stats
		file = open(filename, 'r')
		self.algo_steps = deque()
		for line in file.readlines():
			self.algo_steps.append(line[:-1]) #skip the newline
		self.allowed_sequences = []
		self.rules = []
		self.queued_moves = deque()
	
		#build patterns to recognize
		self.inner_1x1 = [[7],[11],[13],[17]]
		self.inner_2x1 = [[6,7], [7,8], [8,13], [13,18], [6,11], [11,16],[16,17],[17,18]]
		self.inner_2x2 = [[6,7,11], [7,8,13], [11,16,17], [13,17,18]]
		self.inner_3x1 = [[6,7,8],[6,11,16],[16,17,18],[8,13,18]]
		self.inner_3x3 = [[6,7,8,11,13,16,17,18]]
		self.inner_3x2 = []
		self.inner_1x1_corner = [[6],[8],[16],[18]]

		#building the 3x2 blocks are easier like this
		for sub in self.inner_3x1:
			tmp = []
			tmp.extend(self.inner_3x3[0])

			for c in sub:
				tmp.remove(c)
			self.inner_3x2.append(tmp)

	def get_remaining_steps(self):
		return self.algo_steps

	#continue parsing the algorithm lines
	def parse_algo(self):
		next_line = self.algo_steps.popleft()
		split = next_line.split('#')

		#handle setting up of allowed  moves
		while split[0] in ['set_moves', 'set_search_moves', 'comment']:
			if split[0] == 'set_moves':
				new_seq = split[1].split(',')
				self.allowed_sequences = new_seq
			elif split[0] == 'set_search_moves':
				face = split[1].strip()
				self.search_moves = face
			
			elif split[0] == 'comment': 
				print "at comment"
				pass 
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
				try:
					self.rules.remove(rule)
				except:
					raise NameError("Rule is incorrect, cannot remove:" + str(rule))


	def next_move(self):
		#if we have a prepared move in stock just feed that one
		if self.test_cube():
			return ' '

		if len(self.queued_moves) == 0:
			self.make_queue()

		if len(self.queued_moves) > 0:
			pop = self.queued_moves.popleft()
			return pop
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
				'3x2' : Block.inner_3x2,
				'1x1_corner' : Block.inner_1x1_corner
				}

		size = m[parts[1]]
		return (parts[0], size, parts[2], Face_Lookup[parts[3]])

	def rev_seq(self, s):
		s.reverse()
		for i, m in enumerate(s):
			if(s[i][-1:] == 'p'):
				s[i] = m[:-1]
			else:
				s[i] = m + 'p'


	def make_queue(self):
		mods = self.allowed_sequences
		c = self.cube
		if self.test_cube():
			return
		
		while True:
			que = deque()
			done = False
			for m in mods:
				que.append(m)
			cnt = 0

			while len(que) > 0:
				cnt = cnt + 1
				seq = que.popleft()
				s = seq.split(" ")

				if cnt > 10000:
					break

				c.rotate(s)

				if self.test_cube(): 
					done = True
				#undo what we did to the mutable cube, then revert tho sequence to the correct one
				self.rev_seq(s)

				c.rotate(s)

				self.rev_seq(s)

				if done == True :
					for c in s:
						self.queued_moves.append(c)
					self.stats.nr_search_steps += cnt
					return

				#continue the bfs
				for m in mods:
					que.append( seq + ' ' + m)
			#the search found nothing, now fall back on the search-moves:
			search_cands = self.get_faces_with_inner_color(self.search_moves)
			move = search_cands[random.randrange(0, len(search_cands))]

			self.queued_moves.append(move)
			self.stats.nr_search_steps += cnt
			return
	
	#handles inner faces, not for edges or corners
	def get_faces_with_inner_color(self, color):
		ret = []
		for face_id, face in enumerate(self.cube.state):
			for sticker in [6,7,8,11,13,16,17,18]: 
				if face[sticker] == Face_Lookup[color]:
					ret.append(Turns[face_id])
		return ret
			
	#verifies if the cube satisfies all rules in its current state
	def test_cube(self, p=False):

		for color in Turns:
			ok = self.test_color(color, p)
			if not ok:
				return False
		return True
		#for each face, examine what patterns they have in each color
		#TODO: handle pattern recognizion for each color

	def test_color(self, color, p):
		num_blocks = []
		for i in range(0,7):
			num_blocks.append([0,0,0,0,0,0,0])
		for face in range (0,6):
			f = self.cube.state[face]
			used = []

			stickers = self.get_stickers(f, color )
			stickers = filter(lambda x: x in self.inner_3x3[0], stickers)

			#examine what we have on each side, one hit is enough since we never need 2 free 2x1 or 3x1 blocks in an incorrect position
			#3x3 and 3x2, only on d-face
			self.check_case(self.inner_3x3, Block.inner_3x3, num_blocks, face, used, stickers)
			self.check_case(self.inner_3x2, Block.inner_3x2, num_blocks, face, used, stickers)
			#3x1
			self.check_case(self.inner_3x1, Block.inner_3x1, num_blocks, face, used, stickers)

			#2x2 only D
			self.check_case(self.inner_2x2, Block.inner_2x2, num_blocks, face, used, stickers)

			#2x1
			self.check_case(self.inner_2x1, Block.inner_2x1, num_blocks, face, used, stickers)
			if p:
				print "Face is ", face, ", Used stuff: ", used
			#1x1 - only interesting on correct side
			self.check_case(self.inner_1x1, Block.inner_1x1, num_blocks, face, used, stickers)
			self.check_case(self.inner_1x1_corner, Block.inner_1x1_corner, num_blocks, face, used, stickers)

		if p:
			print "Color: ", color, ", num_blocks: ", num_blocks

		for r in self.rules:
			req_face = Face_Lookup[r[2]]
			
			if r[2] != color:
				continue
			
			block_type = r[1]
			needs_face = r[3]
			if needs_face != None:
				if( num_blocks[block_type][needs_face] > 0):
					num_blocks[block_type][needs_face] -= 1
				else:
					return False
			else:
				success = False
				for face in range(0,6):
					if face == req_face: #any means not on the solved side
						continue
					if num_blocks[block_type][face] > 0:
						num_blocks[block_type][face] -= 1
						success = True
						break
				if not success:
					return False

		return True

	def check_case(self, cands, case, num_blocks, face, used, stickers):
		for cand in cands:
			success = True
			for a in cand:
				found = False
				for b in stickers:
					if a == b:
						found = True
						break;
				if not found:
					success = False
					break

				for b in used:
					if a == b:
						success = False
						break
			if success:
				num_blocks[case][face] += 1
				if case == self.inner_3x1:
					num_blocks[self.inner_2x1][face] += 1
					num_blocks[self.inner_1x1][face] += 1
				used.extend(cand)
				return

		#for cand in cands:
		#	if len(set(cand) & set(stickers)) == len(cand) and len(set(cand) & set(used)) == 0:
		#		num_blocks[case][face] += 1
		#		used.extend(cand)
	def get_stickers(self, face, color):
		ret = []

		for id, sticker in enumerate(face):
			if sticker == Face_Lookup[color]:
				ret.append(id)

		return ret

