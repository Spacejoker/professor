import pymongo
import datetime

class Persist():
	def __init__(self):
		conn = pymongo.Connection('localhost', 27017)
		self.db = conn['cube']	
		self.result = self.db.result
	
	def list_problems(self):
		probs = self.db.problem_state.find()
		for nr, p in enumerate(probs):
			if nr > 5:	
				print "=============================="
				print "Got a total of ", self.db.problem_state.count(), "problems"
				break
			print "Problem nr ", nr, "=================================="
			rules = p['rules']
			for rule in map(Formatter.rule_to_string, rules):
				if(rule != None):
					print rule
			print "Allowed sequences:", map(str, p['allowed_sequences'])
			print "Scramble:", map(str,p['scramble'])
	
	def list_results(self, name=None):
		if name != None:
			return self.db.result.find({'name':name})
		return self.db.result.find()

	def save_result(self, res):
		self.db.result.save(res)

	def remove_results(self, all=False):
		if all:
			self.db.result.remove()
		else:
			print "TODO, remove first"

	def get_first_problem(self):
		probs = self.db.problem_state.find()
		return probs[0]

	def clear_problems(self):
		self.db.problem_state.remove()

	def remove_first_problem(self):
		prob = self.db.problem_state.find()[0]
		self.db.problem_state.remove({'scramble' : prob['scramble']})

	def dump_state(self, algo):
		chunk = { 
				'all_commands' : algo.cube.all_commands,
				'scramble' : algo.cube.scramble,
				'rules' : algo.rules,
				"date": datetime.datetime.utcnow(),
				'mode' : algo.mode,
				'flip_algo' : algo.flip_algo,
				'allowed_sequences' : algo.allowed_sequences,
				'stored' : algo.stored
				}
		self.db.problem_state.remove({'scramble' : algo.cube.scramble})
		self.db.problem_state.save(chunk)

	def add_algo(self, algo):
		if self.get_algo(algo['name']):
			print "cannot save, algo exists"
		else:
			self.db.algo.save(algo)
	
	def get_algo(self, name):

		params = {'name' : name}
	        algos = self.db.algo.find(params)

		if algos.count() > 0:
			return algos[0]
		else:
			return None

	def list_algos(self):
		return self.db.algo.find()

	def remove_algo(self, name):
		self.db.algo.remove({'name' : name})
