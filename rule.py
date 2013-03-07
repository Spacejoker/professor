import json
from algo import *

class Rule():
	inner = 'inner'

	def __init__(self):
		pass

	def make_test(self):
		self.type = Rule.inner
		self.command = Block.inner_1x1

class Algo_Parser():
	@staticmethod
	def parse_algo(filename):
		content = None	
		with open(filename, 'r') as content_file:
		    content = content_file.read()
		c = json.loads(content)
		for cmd in c['commands']:
			print cmd['type']
		return c

if __name__ == '__main__':
	Algo_Parser.parse_algo('f3x3.algo')
