import pygame
import time
import itertools
from pygame.locals import *
from cube import *
from main import *

faces = [Face_Data((153,0), (40,40,40)), Face_Data((153, 153), (255, 150, 0)), Face_Data((0, 306), (0, 0, 255)), Face_Data((153, 306), (255, 255, 0)), Face_Data((306, 306), (0,255,0)), Face_Data((153, 459), (255,0, 0))]

#helper to be able to show all edge-sets for edge building
text_color = (255, 220, 220)

class Graphics():

	def __init__(self):
		self.window = pygame.display.set_mode((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT)) 
		self.font = pygame.font.SysFont("monospace", 15)
		

	def draw_cube(self, cube, algo, stats):

		pygame.draw.rect(self.window, (0,0,0), (0,0,Constants.WINDOW_WIDTH,Constants.WINDOW_HEIGHT), 0)

		for side in range(0, len(cube.state)):
			for id, sticker in enumerate(cube.state[side]):
				f = faces[side]
				color = faces[sticker]
				size = Constants.STICKER_SIZE
				pygame.draw.rect(self.window, color.color, (f.position[0] + Helper.get_x(id)*size, f.position[1] + Helper.get_y(id)*size, size-1,size-1), 0)	
		num = 1	

		#display comments
		for step in algo.algo_steps:
			if num > 7:
				break
			if step.split("#")[0] == "comment":
				label = self.font.render(str(num) + ": " + str(step.split("#")[1]), 1, (255, 0,0))
				self.window.blit(label, (500,100 + num*20))
				num += 1
		
		#display rules in a list
		for id, rule in enumerate(algo.rules):
			display = ""
			if rule[0] == 'Inner':
				display = Rule_Lookup[rule[1]] + ", sticker " + str(rule[2]) + " on "
				if rule[3] != None:
					display += "face  " + str(Turns[rule[3]])
				else:
					display += " any face"
			if rule[0] == 'Edge':
				display += str(rule)

			label = self.font.render(display, 1, (255, 0,0))
			self.window.blit(label, (800,120 + id*20))

		label = self.font.render("Allowed: " + str(algo.allowed_sequences), 1, (255, 255,255))
		self.window.blit(label, (400, 20))
		label = self.font.render("Nr moves: " + str(stats.nr_moves), 1, (255,255,255))
		self.window.blit(label ,(600, 600))

		label = self.font.render("Nr search steps: " + str(stats.nr_search_steps), 1, (255,255,255))
		self.window.blit(label ,(600, 550))
		
		edge_x = 600
		edge_y = 350

		for name, edges in edge_pieces.iteritems():
			self.window.blit(self.font.render(name, 1, text_color), (edge_x, edge_y))
			for num, pair in enumerate(edges):
				fst = cube.state[pair.left_face()][pair.left_sticker()]
				snd = cube.state[pair.right_face()][pair.right_sticker()]
				self.draw_face(faces[fst].color, edge_x, edge_y + num*size + 20)
				self.draw_face(faces[snd].color, edge_x + size, edge_y + num*size + 20)
			edge_x += 100

		pygame.display.flip() 
	def draw_face(self, color, x, y):
		size = Constants.STICKER_SIZE
		pygame.draw.rect(self.window, color, (x, y, size-1, size-1), 0)

	def draw_menu(self):
		label = self.font.render("The professor's cube!", 1, (255,255,255))
		self.window.blit(label ,(300, 550))

		pygame.display.flip() 

