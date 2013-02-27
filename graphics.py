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
		#load images
		self.images = []
		size = Constants.STICKER_SIZE
		self.seen_sticker_pos = []
		for i in range(0,6):
			tmp = []
			for j in range(0,25):
				tmp.append((-1, 0))
			self.seen_sticker_pos.append(tmp)

		for color in ['black','orange','blue','yellow','green','red']:
			cur_img = []
			for num in range(0,3):
				asurf = pygame.image.load(os.path.join('img', color + str(num) + '.png'))
				asurf = pygame.transform.scale(asurf, (size-1, size-1))
				cur_img.append(asurf)
			self.images.append(cur_img)
		
		self.bg = pygame.image.load(os.path.join('img', 'bg.png'))

	def draw_cube(self, cube, algo, stats):

		self.window.blit(self.bg, (0,0))
		xoffset = 58
		yoffset = 74
		for side in range(0, len(cube.state)):
			for id, sticker in enumerate(cube.state[side]):
				f = faces[side]
				color = faces[sticker]
				size = Constants.STICKER_SIZE
				self.draw_face(sticker, f.position[0] + Helper.get_x(id)*size + xoffset, f.position[1] + Helper.get_y(id)*size + yoffset, side, id)

		num = 1	

		#display comments
		for step in algo.algo_steps:
			if num > 7:
				break
			#if step.split("#")[0] == "comment":
				#label = self.font.render(str(num) + ": " + str(step.split("#")[1]), 1, (255, 0,0))
		#		self.window.blit(label, (500,100 + num*20))
				#num += 1
		
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
		#	self.window.blit(label, (800,120 + id*20))

		label = self.font.render("Allowed: " + str(algo.allowed_sequences), 1, (255, 255,255))
		self.window.blit(label, (400, 20))
		label = self.font.render("Nr moves: " + str(stats.nr_moves), 1, (255,255,255))
		self.window.blit(label ,(900, 600))

		label = self.font.render("Nr search steps: " + str(stats.nr_search_steps), 1, (255,255,255))
		self.window.blit(label ,(600, 600))

		self.draw_edges(['FR', 'LF', 'BL', 'RB'], 604, 75, cube, size)
		self.draw_edges(['UF', 'UL', 'UB', 'UR'], 604, 75+120, cube, size)
		self.draw_edges(['DF', 'DL', 'DB', 'DR'], 604, 75+240, cube, size)

		self.draw_corners(cube, size)

		pygame.display.flip() 

	def draw_corners(self, cube, size):

		c = cube.create_corner_map()
		x0 = 1030
		x = x0
		y = 75
		cnt = 0
		for name, stickers in c.items():
			if cnt >= 2:
				cnt = 0
				y += 2*size + 20
				x = x0
			cnt += 1

			label = self.font.render(name, 1, (255,255,255))
			self.window.blit(label ,(x, y))
			self.draw_face(stickers[1], x + size/2, y + 20)
			self.draw_face(stickers[2], x , y + 20 + size)
			self.draw_face(stickers[0], x - size/2, y + 20)

			x += size * 4

	def draw_edges(self, names, x0, y0, cube, size):

		edge_x = x0
		edge_y = y0

		for name in names:
			edges = edge_pieces[name]
			self.window.blit(self.font.render(name, 1, text_color), (edge_x, edge_y))
			for num, pair in enumerate(edges):
				fst = cube.state[pair.left_face()][pair.left_sticker()]
				snd = cube.state[pair.right_face()][pair.right_sticker()]
				self.draw_face(fst, edge_x, edge_y + num*size + 20,pair.left_face(), pair.left_sticker())
				self.draw_face(snd, edge_x + size, edge_y + num*size + 20, pair.right_face(), pair.right_sticker())
			edge_x += 100

	def draw_face(self, color, x, y, face = 0, sticker_nr = 0):
		size = Constants.STICKER_SIZE
		img = None
		#handle so that we show the same picture if it has already been shown in this spot
		img_cache = self.seen_sticker_pos[face][sticker_nr]
		if img_cache[0] == color:
			img = self.images[color][img_cache[1]]
		else: 
			num = random.randint(0,2)
			self.seen_sticker_pos[face][sticker_nr] = (color, num)
			img = self.images[color][num]
		self.window.blit(img, (x, y, size, size))
		#pygame.draw.rect(self.window, color, (x, y, size-1, size-1), 0)

	def draw_menu(self):
		label = self.font.render("The professor's cube!", 1, (255,255,255))
		self.window.blit(label ,(300, 550))

		pygame.display.flip() 

