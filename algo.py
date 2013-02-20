from cube import *
from collections import deque
import random
from copy import copy, deepcopy
import time	

#enum types for readability
class Orientation:
	any = 0
	oriented = 1
	non_oriented = 2

class Edge:
	outer = 0
	center = 1

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
		self.stats.current_nr_search_moves = 0

		#handle setting up of allowed  moves
		while split[0] in ['set_moves', 'set_search_moves', 'comment', 'set_mode']:
			if split[0] == 'set_moves':
				new_seq = split[1].split(',')
				self.allowed_sequences = new_seq

			elif split[0] == 'set_search_moves':
				face = split[1].strip()
				self.search_moves = face
			
			elif split[0] == 'comment': 
				print "at comment"
				pass 

			elif split[0] == 'set_mode':
				self.mode = split[1].strip()

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
		
		if parts[0] == 'Inner':

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

		elif parts[0] == 'Build_Edge':
			#outer edge / center edge:
			piece = {
					'Outer' : Edge.outer,
					'Center' : Edge.center
					}
			
			orientation = { 'Any' : Orientation.any,
					'Oriented' : Orientation.oriented,
					'Non_Oriented' : Orientation.non_oriented
					}
			return (parts[0], piece[parts[1]], orientation[parts[2]], parts[3])
		elif parts[0] == 'Edge':
			return (parts[0], parts[1], parts[2])

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
		flip_algo = 'R U Rp Up Fp U F'
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
				if self.mode == 'build_edge':
					print 'teste'	
					rev = []
					rev.extend(s)
					self.rev_seq(rev)

					s.extend(flip_algo.split(' '))
					s.extend(rev)
					print "evaluating: ", s
				if cnt > 10000:
					self.stats.current_nr_search_moves += 1
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
			if self.mode == 'inner':
				search_cands = self.get_faces_with_inner_color(self.search_moves)
				move = search_cands[random.randrange(0, len(search_cands))]

				self.queued_moves.append(move)
			elif self.mode == 'edge':
				self.queued_moves.append('L L')
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
	
	def same_piece(self, fst, snd, oriented=False):
		fstleft = self.cube.state[fst.left_face()][fst.left_sticker()]
		fstright = self.cube.state[fst.right_face()][fst.right_sticker()]
		
		sndleft = self.cube.state[snd.left_face()][snd.left_sticker()]
		sndright = self.cube.state[snd.right_face()][snd.right_sticker()]

		if fstleft == sndleft and fstright == sndright:
			return True
		if not oriented and fstleft == sndright and fstright == sndleft:
			return True
		return False

	#verifies if the cube satisfies all rules in its current state
	def test_cube(self, p=False):
		for color in Turns:
			ok = self.test_color(color, p)
			if not ok:
				return False

		#edge building rules:
		for rule in self.rules:
			c = self.cube
			if rule[0].strip() == 'Build_Edge':
				if rule[1] == Edge.outer:
					#and r[2] == Orientation.oriented:
					fr_mid = edge_pieces['FR'][1]
					
					#check all pairs in mid layer, except for FR
					found = False

					for edge_pos in ['LF','BL','RB']:
						for piece_id in [0,2]: #only want to look at top and bottom edges
							if self.same_piece(fr_mid, edge_pieces[edge_pos][piece_id], oriented = (rule[2] == Orientation.oriented)):
								found = True
								break

					if not found:
						return False
			if rule[0] == 'Edge':
				if rule[1] in ['2x1x1']: #store is for 3x1x1
					fr_mid = edge_pieces['FR'][1]
					left = self.cube.state[fr_mid.left_face()][fr_mid.left_sticker()]
					right = self.cube.state[fr_mid.right_face()][fr_mid.right_sticker()]
					
					top = edge_pieces['FR'][0]
					l_top = self.cube.state[top.left_face()][top.left_sticker()]
					r_top = self.cube.state[top.right_face()][top.right_sticker()]
					
					bot = edge_pieces['FR'][2]
					l_bot = self.cube.state[bot.left_face()][bot.left_sticker()]
					r_bot = self.cube.state[bot.right_face()][bot.right_sticker()]
					cnt = 0	

					if left == l_top and right == r_top:
						cnt += 1
					if left == l_bot and right == r_bot:
						cnt += 1
					if cnt == 0:
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
			if r[0] == 'Inner':
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

