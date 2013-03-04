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

	def get_result(self, name):
		return self.db.result.find({'name':name})

	def get_latest_solve(self):
		latest = self.db.latest.find()[0]
		print "Latest", latest
		return latest

	def save_latest_solve(self, res):
		self.db.latest.remove()
		self.db.latest.save({'scramble' : res['scramble'], 'moves' : res['moves']})

	def save_result(self, res):
		remove = self.db.result.remove({'scramble' : res['scramble'], 'name':res['name']}) # remove identical solve
		print remove
		self.db.result.save(res)

	def remove_results(self, name=None):
		if name == None:
			self.db.result.remove()
		else:
			self.db.result.remove({'name':name})

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
			self.db.algo.remove({'name':algo['name']})
			print "Overwriting algo"
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

	def remove_algo(self, name=None):
		if name == None:
			print "Must supply name, nothing removed"
		else:
			self.db.algo.remove({'name' : name})
			self.remove_results(name)

	def add_scramble(self, scramble):
		self.db.scramble.save(scramble)

	def get_scrambles(self, scramble_type=None):
		if scramble_type == None:
			return self.db.scramble.find()
		scrambles = self.db.scramble.find({'scramble_type':scramble_type})
		return scrambles

	def remove_scrambles(self, scramble_type=None):
		if scramble_type != None:
			self.db.scramble.remove({'scramble_type':scramble_type})
		else:
			self.db.scramble.remove()
	
	def find_algo_category(self, category):
		return self.db.algo.find({'category' : category})
