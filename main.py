import os
import random
import pygame
import time
import itertools
from pygame.locals import *

class Constants():
	WINDOW_WIDTH = 450
	WINDOW_HEIGHT = 600
	STICKER_SIZE = 30
#Provide a mapping from notation to code
Turns = ['D', 'B', 'L', 'U', 'R', 'F']
class Face: #enum
	D = 0
	B = 1
	L = 2
	U = 3
	R = 4
	F = 5
	
class Face_Data():
	def __init__(self, position, color):
		self.position = position
		self.color = color

faces = [Face_Data((150,0), (40,40,40)), Face_Data((150, 150), (0, 255, 0)), Face_Data((0, 300), (255, 150, 0)), Face_Data((150, 300), (255, 255, 0)), Face_Data((300, 300), (255,0,0)), Face_Data((150, 450), (0,0, 255))]

colors = []
#Helper methods for conversion etc
class Helper():
	@staticmethod
	def to_int(y, x):
		return y*5 + x
	@staticmethod
	def get_x(id):
		return id % 5
		
	@staticmethod
	def get_y(id):
		return id/5
	
		
class Chain_Generator():
	@staticmethod
	def rot_face(face):
		#chains for the outmost sticker circle
		ret = []
		for i in range(0, 4):
			ret.append([(face, Helper.to_int(0, i)), (face, Helper.to_int(i, 4)), (face, Helper.to_int(4, 4-i)), (face, Helper.to_int(4-i, 0))])
		
		#chains for the inner cicrle
		for i in range(1, 3):
			ret.append([(face, Helper.to_int(1, i)), (face, Helper.to_int(i, 3)), (face, Helper.to_int(3, 4-i)), (face, Helper.to_int(4-i, 1))])
		return ret

	@staticmethod
	def get_chain(command):
		ret = []
		if( command[-1:] == '\''):
			return itertools.chain(Chain_Generator.get_chain(command[:-1]),Chain_Generator.get_chain(command[:-1]),Chain_Generator.get_chain(command[:-1]))
			
		if command == 'R': 
			ret = Chain_Generator.R_chain()
		elif command == 'r': 
			ret = Chain_Generator.r_chain()
		elif command == 'F': 
			ret = Chain_Generator.F_chain()
		elif command == 'f': 
			ret = Chain_Generator.f_chain()
		elif command == 'L': 
			ret = Chain_Generator.L_chain()
		elif command == 'l': 
			ret = Chain_Generator.l_chain()
		elif command == 'b':
			ret = Chain_Generator.b_chain()
		elif command == 'B':
			ret = Chain_Generator.B_chain()
		elif command == 'u':
			ret = Chain_Generator.u_chain()
		elif command == 'U':
			ret = Chain_Generator.U_chain()
		elif command == 'd':
			ret = Chain_Generator.d_chain()
		elif command == 'D':
			ret = Chain_Generator.D_chain()
		return ret

	@staticmethod
	def d_chain():
		ret = []
		for pos in range(15,20):
			ret.append([(Face.F, pos), (Face.R, (19-pos)*5 + 3), (Face.B,24-pos), (Face.L, (pos-15)*5 + 1)])
			print "d: ", ret[:-1]
		return ret


	@staticmethod
	def D_chain():
		ret = []
		for pos in range(20,25):
			ret.append([(Face.F, pos), (Face.R, (24 - pos)*5 + 4), (Face.B,24-pos), (Face.L, (pos - 20)*5)])
			print "D: ", ret[:-1]
		for r in Chain_Generator.rot_face(Face.D):
			ret.append(r)
		return ret

	@staticmethod
	def u_chain():
		ret = []
		for pos in range(5,10):
			ret.append([(Face.F, pos), (Face.L, (pos-5)*5 + 3), (Face.B,24-pos), (Face.R, (9-pos)*5 + 1)])
		return ret


	@staticmethod
	def U_chain():
		ret = []
		for pos in range(0,5):
			ret.append([(Face.F, pos), (Face.L, pos*5 + 4), (Face.B,24-pos), (Face.R, (4-pos)*5)])
		for r in Chain_Generator.rot_face(Face.U):
			ret.append(r)
		return ret

	@staticmethod
	def B_chain():
		ret = []
		for pos in range(0, 5):
			ret.append([(Face.U, pos), (Face.L, pos), (Face.D, 24-pos), (Face.R, pos)]);
		for r in Chain_Generator.rot_face(Face.B):
			ret.append(r)
		return ret

	@staticmethod
	def b_chain():
		ret = []
		for pos in range(5, 10):
			ret.append([(Face.U, pos), (Face.L, pos), (Face.D, 24-pos), (Face.R, pos)]);
		return ret

	@staticmethod
	def f_chain():
		ret = []
		for pos in range(15, 20):
			ret.append([(Face.U, pos), (Face.R, pos), (Face.D, 24-pos), (Face.L, pos)]);
		return ret

	@staticmethod
	def F_chain():
		ret = []
		for pos in range(20, 25):
			ret.append([(Face.U, pos), (Face.R, pos), (Face.D, 24-pos), (Face.L, pos)]);
		for r in Chain_Generator.rot_face(Face.F):
			ret.append(r)
		return ret
	@staticmethod	
	def L_chain():
		ret = []
		for pos in range(0, 5*5, 5):
			ret.append([(Face.U, pos), (Face.F, pos), (Face.D, pos), (Face.B, pos)]);
		for r in Chain_Generator.rot_face(Face.L):
			ret.append(r)
		return ret
	@staticmethod
	def l_chain():
		ret = []
		for pos in range(1, 5*5, 5):
			ret.append([(Face.U, pos), (Face.F, pos), (Face.D, pos), (Face.B, pos)]);
		return ret
		
	@staticmethod
	def r_chain():
		ret = []
		for pos in range(3, 5*5, 5):
			ret.append([(Face.U, pos), (Face.B, pos), (Face.D, pos), (Face.F, pos)]);
		return ret
		
	@staticmethod	
	def R_chain():
		ret = []
		print "ret: ", ret
		for pos in range(4, 5*5, 5):
			ret.append([(Face.U, pos), (Face.B, pos), (Face.D, pos), (Face.F, pos)]);
			print "ret: ", ret
		for r in Chain_Generator.rot_face(Face.R):
			ret.append(r)
			print "ret: ", ret
		return ret

class Cube():
	def __init__(self):
		
		self.state = []
		for i in range(0,len(Turns)):
			sticker = []
			for x in range(0,25):
				sticker.append(i)
			self.state.append(sticker)
		
	def apply_chain(self, chain):
		
		for c in chain:
			c.reverse()
			tmp = self.state[c[0][0]][c[0][1]]
			
			for i in range(0, len(c)-1):
				self.state[c[i][0]][c[i][1]] = self.state[c[i+1][0]][c[i+1][1]]
				
			self.state[c[len(c)-1][0]][c[len(c)-1][1]] = tmp

class Scrambler():
	@staticmethod	
	def genScramble():
		scramble = ""
		for x in range (0,60):
			turn = Turns[random.randint(0,5)]
			mod = random.randint(0,5)
			if(mod % 3 == 0):
				turn = turn.lower()
			if(mod % 3 == 1):
				turn = turn + 'w'
			if(mod >3):
				turn += '\''
			scramble += turn  + " "
		print scramble
		f = open('scramble.txt', 'w')
		f.write(scramble)
		f.close()

class Graphics():
	
	def __init__(self):
		self.window = pygame.display.set_mode((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)) 
	
	def draw_cube(self, cube):
		for side in range(0, len(cube.state)):
			for id, sticker in enumerate(cube.state[side]):
				f = faces[side]
				color = faces[sticker]
				size = Constants.STICKER_SIZE
				pygame.draw.rect(self.window, color.color, (f.position[0] + Helper.get_x(id)*size,f.position[1] + Helper.get_y(id)*size,size-1,size-1), 0)	
				
		pygame.display.flip() 
#Main application loop
def loop():
	pygame.init() 
	
	c = Cube()
	g = Graphics()
	
	running = True
	while running: 
		g.draw_cube(c)
		keymap = {}
		event = pygame.event.wait()
		if event.type == pygame.KEYDOWN:
			keymap[event.scancode] = event.unicode
			
			c.apply_chain(Chain_Generator.get_chain(event.unicode)) #handles dvorak
			
			if event.unicode == 'e':
				c.apply_chain(Chain_Generator.get_chain('R\'')) 
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				running = False
		
	pygame.quit()

if __name__ == '__main__':

	

	Scrambler.genScramble()
	
	print "GET: "
	for c in Chain_Generator.get_chain('R'):
		print c
	
	print "GET F: "
	for c in Chain_Generator.get_chain('F'):
		print c
	
	loop()
	
