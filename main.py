import os
import random
import pygame
import time
import itertools
from pygame.locals import *
from cube import *

class Constants():
	WINDOW_WIDTH = 450
	WINDOW_HEIGHT = 600
	STICKER_SIZE = 30
		
class Scrambler():
	@staticethod	
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
	
