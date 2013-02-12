from cube import *
from collections import deque

class Sample_Algo():
	def __init__(self, cube):
		self.cube = cube
		self.steps = [[((Face.D,7),Face.D)], [((Face.D, 6), Face.D), ((Face.D, 11), Face.D)]]
		self.done = []
		self.queue = deque()

	def test_cube(self, done):
		c = self.cube
		for item in done:
			if self.cube.get(item[0]) != item[1]:
				return False
		return True

	def make_queue(self):
		que = deque()
		mods = ['r','f','l','u','d','b','D']
		c = self.cube
		done = False
		for m in mods:
			que.append(m)
		while True:
			seq = que.popleft()
			s = seq.split(" ")
			
			c.rotate(s)
				
			if self.test_cube(self.done) and self.test_cube(self.steps[0]):
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

	def next_move(self):
		
		if len(self.queue) > 0:
			return self.queue.popleft()
		
		if len(self.steps) > 0 and self.test_cube(self.queue) and self.test_cube(self.steps[0]):
			self.queue.extend(self.steps[0])
			self.steps.remove(0)
		else:
			self.make_queue()
		
		return self.queue.popleft()
	
