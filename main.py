import random
import pygame


	  
#Provide a mapping from notation to code
Turns = ['D', 'B', 'L', 'U', 'R', 'F']
class Face:
	D = 0
	B = 1
	L = 2
	U = 3
	R = 4
	F = 5

#Helper methods for conversion etc
class Helper():
	@staticmethod
	def to_int(y, x):
		return y*5 + x;
	@staticmethod
	def get_x(id):
		return id % 5
	@staticmethod
	def get_y(id):
		return id/5;
		
class Chain_Generator():
	@staticmethod
	def rot_face(face):
		#chains for the outmost sticker circle
		for i in range(0, 4):
			yield([(face, Helper.to_int(0, i)), (face, Helper.to_int(i, 4)), (face, Helper.to_int(4, 4-i)), (face, Helper.to_int(4-i, 0))])
		
		for i in range(0, 2):
			yield([(face, Helper.to_int(1, i)), (face, Helper.to_int(i, 3)), (face, Helper.to_int(3, 4-i)), (face, Helper.to_int(4-i, 1))])

	@staticmethod
	def get_chain(command):
		return {
			'R' : Chain_Generator.R_chain(),
			'r' : Chain_Generator.r_chain(),
			'F' : Chain_Generator.F_chain()
			}.get(command, [])

	@staticmethod
	def F_chain():

		for pos in range(20, 25):
			yield([(Face.U, pos), (Face.R, pos), (Face.D, 24-pos), (Face.L, pos)]);
		for r in Chain_Generator.rot_face(Face.F):
			yield(r)
			
	@staticmethod
	def l_chain():
		ret = []
		for pos in range(1, 5*5, 5):
			yield([(Face.U, pos), (Face.F, pos), (Face.D, pos), (Face.B, pos)]);

	@staticmethod
	def r_chain():
		ret = []
		for pos in range(3, 5*5, 5):
			yield([(Face.U, pos), (Face.B, pos), (Face.D, pos), (Face.F, pos)]);
	@staticmethod	
	def R_chain():
		ret = []
		for pos in range(4, 5*5, 5):
			yield([(Face.U, pos), (Face.B, pos), (Face.D, pos), (Face.F, pos)]);
		for r in Chain_Generator.rot_face(Face.R):
			yield(r)
		
class Cube():
	def __init__(self):
		
		self.state = []
		for i in range(0,len(Turns)):
			sticker = []
			for x in range(0,25):
				sticker.append(i)
			self.state.append(sticker)
	
	def rot(self, rotation):
		print "todo, rotate!"
		
	def apply_chain(chain):
		pass

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

#Main application loop
def loop():
	pygame.init() 
	window = pygame.display.set_mode((640, 480)) 
	c = Cube()
	
	for side in c.state:
		for id, sticker in enumerate(side):
			pass
	pygame.draw.rect(window, (255,0,0), (20,20,30,30), 0)
	
	pygame.display.flip() 

	running = True
	while running: 
		for event in pygame.event.get(): 
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
	
