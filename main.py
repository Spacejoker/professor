import os
import random
import pygame
import time
import itertools
from pygame.locals import *
from cube import *
from algo import Sample_Algo
class Constants():
	WINDOW_WIDTH = 450
	WINDOW_HEIGHT = 600
	STICKER_SIZE = 30
		
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
				turn += '\''
			scramble += turn  + " "
		f = open('scramble.txt', 'w')
		f.write(scramble)
		f.close()

		return scramble

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
	prim = False
	w = False

	algo = Sample_Algo(c)
	font = pygame.font.SysFont("monospace", 15)

	while running: 
		g.draw_cube(c)

		pygame.draw.rect(g.window, (0,0,0), (0,0,200,200), 0)
		label = font.render("Prim: " + str(prim) , 1, (255,255,0))
		g.window.blit(label, (20,20))
		label = font.render("w: " + str(w) , 1, (255,255,0))
		g.window.blit(label, (20,40))
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
				cmd += '\''
			c.rotate([cmd])
			
			if event.unicode == ' ':
				print "Next move: ", algo.next_move()
			if event.unicode == 'q':
				c.rotate(algo.next_move())
			if event.unicode == '0':
				c.rotate(Scrambler.gen_scramble().split(' '))
			if event.unicode == '9':
				c = Cube()
				algo = Sample_Algo(c)
			if event.unicode == 'p':
				prim = not prim
			if event.unicode == 'w':
				w = not w
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				running = False
		
	pygame.quit()

if __name__ == '__main__':
	loop()
	
