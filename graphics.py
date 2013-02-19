import pygame
import time
import itertools
from pygame.locals import *
from cube import *
from main import *

faces = [Face_Data((153,0), (40,40,40)), Face_Data((153, 153), (255, 150, 0)), Face_Data((0, 306), (0, 0, 255)), Face_Data((153, 306), (255, 255, 0)), Face_Data((306, 306), (0,255,0)), Face_Data((153, 459), (255,0, 0))]

class Edge_Pair():
	def __init__(self, left, right):
		self.left = left
		self.right = right

	def left_face(self):
		return self.left[0]

	def left_sticker(self):
		return self.left[1]
	
	def right_face(self):
		return self.right[0]

	def right_sticker(self):
		return self.right[1]

#helper to be able to show all edge-sets for edge building
added_edges = [
		('FR', [Edge_Pair((Face.F, 9),(Face.R,21)), Edge_Pair((Face.F, 14),(Face.R, 22)), Edge_Pair((Face.F, 19),(Face.R, 23))]),
		('LF', [Edge_Pair((Face.L, 23),(Face.F,5)), Edge_Pair((Face.L, 22),(Face.F, 10)), Edge_Pair((Face.L, 21),(Face.F, 15))]),
		('BL', [Edge_Pair((Face.B, 15),(Face.L, 3)), Edge_Pair((Face.B, 10),(Face.L, 2)), Edge_Pair((Face.B, 5),(Face.L, 1))]),
		('RB', [Edge_Pair((Face.R, 1),(Face.B, 19)), Edge_Pair((Face.R, 2),(Face.B, 14)), Edge_Pair((Face.R, 3),(Face.B, 9))]),
		]
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
			display = Rule_Lookup[rule[1]] + ", sticker " + str(rule[2]) + " on "
			if rule[3] != None:
				display += "face  " + str(Turns[rule[3]])
			else:
				display += " any face"

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
		for edge in added_edges:
			name = edge[0]
			self.window.blit(self.font.render(name, 1, text_color), (edge_x, edge_y))
			for num, pair in enumerate(edge[1]):
				fst = cube.state[pair.left_face()][pair.left_sticker()]
				snd = cube.state[pair.right_face()][pair.right_sticker()]
				self.draw_face(faces[fst].color, edge_x, edge_y + num*size + 20)
				self.draw_face(faces[snd].color, edge_x + size, edge_y + num*size + 20)
			edge_x += 100

		pygame.display.flip() 
	def draw_face(self, color, x, y):
		print color
		size = Constants.STICKER_SIZE
		pygame.draw.rect(self.window, color, (x, y, size-1, size-1), 0)

	def draw_menu(self):
		label = self.font.render("The professor's cube!", 1, (255,255,255))
		self.window.blit(label ,(300, 550))

		pygame.display.flip() 

