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
		return ret


	@staticmethod
	def D_chain():
		ret = []
		for pos in range(20,25):
			ret.append([(Face.F, pos), (Face.R, (24 - pos)*5 + 4), (Face.B,24-pos), (Face.L, (pos - 20)*5)])
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
		for pos in range(4, 5*5, 5):
			ret.append([(Face.U, pos), (Face.B, pos), (Face.D, pos), (Face.F, pos)]);
		for r in Chain_Generator.rot_face(Face.R):
			ret.append(r)
		return ret

class Cube():
	def __init__(self):
		self.state = []
		for i in range(0,len(Turns)):
			sticker = []
			for x in range(0,25):
				sticker.append(i)
			self.state.append(sticker)
	
	def rotate(self, commands):
		for c in commands:
			c = str(c)
			backwards = False
			if(c[-1:] == '\''):
				backwards = True
				c = c[:-1]
			chain = []
			if( c[-1:] == 'w'):
				chain.extend(Chain_Generator.get_chain(c[:1].lower()))	
			chain.extend( Chain_Generator.get_chain(c[:1]) )
			if chain == None:
				continue
			if(backwards):
				for ch in chain:
					ch.reverse()
			self.apply_chain(chain)

	def apply_chain(self, chain):
		
		for c in chain:
			c.reverse()
			tmp = self.state[c[0][0]][c[0][1]]
			
			for i in range(0, len(c)-1):
				self.state[c[i][0]][c[i][1]] = self.state[c[i+1][0]][c[i+1][1]]
				
			self.state[c[len(c)-1][0]][c[len(c)-1][1]] = tmp

	def get(self, sticker):
		return self.state[sticker[0]][sticker[1]]

	def dump_state(self):
		fout = open('state_dump.txt', 'w')
		
		for face in self.state:
			for sticker in face:
				fout.write(sticker + ",")
			fout.write("\n")

		fout.close()

