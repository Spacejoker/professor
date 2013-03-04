from solver import Solver
from persist import Persist
from main import Scrambler
import random, string
import time
import json
from rule import Algo_Parser
REQ_SUCCESS = 0.97

class Runner():
	def __init__(self):
		self.persist = Persist()


	def menu(self):
		while True:
			print "Enter command: "
			s = raw_input()
			s = s.split(" ")
			if s[0] == 'help':
				print ""
				print "HELP:"
				print "run algo random/db scramble_type"
				print "add filename"
				print "dump algoname"
				print "list"
				print "show algoname"
				print "rm algoname"
				print "rmstats algoname"
				print "stats algoname"
				print "addsc type count"
				print "listsc type"
				print "branch algoname tries (algotype)"
				print "rmsc (type)"
				print "catrun category scramble_type" 
				print "catstats category"
				print "import filename"
				print "failshow"
				print "removeallresult"
				print "failselect id"
				print ""

			if s[0] == 'run':
				name = s[1]
				mode = s[2]
				scramble_type = s[3]
				self.run_algo_command(name,mode,scramble_type,scramble_type)

			if s[0] == 'add':
				algo = Algo_Parser.parse_algo(s[1])
				self.persist.add_algo(algo)

			if s[0] == 'list':
				algos = self.persist.list_algos()
				print ""
				print "Available algos:"
				for a in algos:
					name = a['name']
					while len(name) < 12:
						name = name + " "
					print name, 'category:', a['category']
				print ""	
			if s[0] == 'show':
				res = self.persist.get_algo(s[1])
				print ""
				print "Algo ", s[1], "described:"
				for key, value in res.items():
					print key,":",value
					if str(key) == 'steps':
						for item in value:
							print map(str, item)
				print ""

			if s[0] == 'rm':
				self.persist.remove_algo(s[1])

			if s[0] == 'rmstats':
				name = s[1]
				self.persist.remove_results(name)

			if s[0] == 'stats':
				name = s[1]
				self.stats(name)

			if s[0] == 'addsc':
				scramble_type = s[1]
				cnt = int(s[2])
				for i in range(0,cnt):
					self.persist.add_scramble({'scramble_type' : scramble_type,
								'scramble' : Scrambler.gen_scramble()})
			if s[0] == 'listsc':
				scramble_type = 'full'
				if len(s) > 1:
					scramble_type = s[1]
				#for s in self.persist.get_scrambles(scramble_type=scramble_type):
				for scram in self.persist.get_scrambles():
					print scram
			if s[0] == 'rmsc':
				sctype = None
				if len(s) > 1:
					sctype = s[1]
				self.persist.remove_scrambles(scramble_type = sctype)
			if s[0] == 'col':
				print self.persist.db.collection_names()
				#self.persist.db.problem_state.drop()

			if s[0] == 'branch':
				name = s[1]
				scramble_type = 'full'
				cnt = 1
				if len(s) > 2:
					cnt = int(s[2])
				if len(s) > 3:
					scramble_type = s[3]
				self.branch(name, cnt, scramble_type)
			if s[0] == 'catrun':
				if len(s) < 3:
					print "too few arguments"
					return
				category = s[1]
				scramble_type = s[2]
				algos = self.persist.find_algo_category(category)
				for algo in algos:
					if algo['category'] == category:
						print "Running for ", algo['name']
						self.run_algo_command(algo['name'], 'db',0, scramble_type)
			if s[0] == 'catstats':
				category = s[1]
				algos = self.persist.find_algo_category(category)
				print ""
				print "Stats for category", category
				print "============================================="
				for algo in algos:
					self.stats(algo['name'])
				print ""
			if s[0] == 't':
				for rec in self.persist.db.algo.find():
					print rec
					if rec['name'] == 'standard':
						self.persist.db.algo.remove({'name' : rec['name']})
						rec['category'] = 'full'
						self.persist.db.algo.save(rec)

			if s[0] == 'rename':
				algo = self.persist.get_algo(s[1])
				algo['name'] = s[2]
				self.persist.remove_algo(s[1])
				self.persist.add_algo(algo)

			if s[0] == 'setcat':
				algo = self.persist.get_algo(s[1])
				algo['category'] = s[2]
				self.persist.remove_algo(s[1])
				self.persist.add_algo(algo)

			if s[0] == 'dump':
				algo = self.persist.get_algo(s[1])
				algo.pop("_id", None)
				f = open(s[1] + '-dump.algo', 'w')
				json.dump(algo, f)
				f.close()
			
			if s[0] == 'import':
				f = open(s[1], 'r')
				algo = {}
				for line in f:
					split = line[:-1].split('#')
					algo[split[0]] = split[1]
					print line
				f.close()
				self.persist.add_algo(algo)

			if s[0] == 'failshow':
				fails = self.persist.result.find({'success' : False})
				for nr, fail in enumerate(fails):
					if nr >= 10:
						break
					print "============================ ITEM", nr,"==============================="
					print "algoname:",fail['name']
	
			if s[0] == 'failselect':
				chosen_nr = int(s[1])
				fails = self.persist.result.find({'success' : False})
				success = False
				for nr, fail in enumerate(fails):
					if nr == chosen_nr:
						self.persist.save_latest_solve(fail)
						success = True
				if success:
					print "Done"
				else:
					print "Unknown id"

			if s[0] == 'removeallresult':
				self.persist.result.remove()

	def stats(self, name):
		res = self.get_algo_result(name)
		success_cnt = res['success_cnt']
		tot_cnt = res['tot_cnt']
		tot_success_moves = res['tot_success_moves']
		search_cnt = res['search_cnt']

		if success_cnt > 0:
			print "Total stats for ", name,":"
			print "==========================="
			print "Succes %:",(success_cnt)/(tot_cnt+0.0)*100.0, "(",success_cnt,"/",tot_cnt,")"
			print "Avg moves:",tot_success_moves/success_cnt
			print "Search count:", search_cnt
			print "Avg time:", res['avg_time']
			print ""
		else:
			print "No successful data for ", name
	def branch(self, name, cnt, scramble_type):

		for i in range(0, cnt):
			limit = random.uniform(0.1, 0.5)
			keep_limit = random.uniform(0.0, 0.20)
			original = self.persist.get_algo(name)
			print "Original steps:"
			new_name = ''.join(random.choice(string.ascii_lowercase) for x in range(5))
			steps = []
			for line in original['steps']:
				if str(line[0]) == 'set_moves':
					cmds = ""
					#try adding some stuff:
					cmd_list = []
					for move in line[1].split(","):
						if random.random() > keep_limit:
							cmd_list.append(move)#  += "," + move

					cands = 'r,f,l,u,d,b,U,D,R,F,L,B,rp,fp,lp,up,dp,bp,Dp,r2,f2,l2,u2,d2,b2,U2,D2,R2,F2,L2,B2,r U rp,rp U r, b U bp,bp U b,fp U f,F,R,L,B,Fp,Rp,Lp,Bp'
					for move in cands.split(','):
						if random.random() > limit and move not in cmd_list:
							cmd_list.append(move)
					random.shuffle(cmd_list)	
					for c in cmd_list:
						cmds += "," + c

					if len(cmds) > 0:
						steps.append([line[0], cmds[1:]])
				else:
					steps.append(line)

			algo = { 'name' : new_name,
					'category' : original['category'],
					'steps' : steps }
			print 'new_algo:', algo
			self.persist.add_algo(algo)

			#run the algo on type full
			success_rate = self.run_algo_command(new_name,'db',0,scramble_type, break_early=True)
			
			if success_rate < 0.80:#remove everything that fails more than some %
				self.persist.remove_algo(new_name)
				print "removing algo",new_name,"since successrate is too low"
			print "success rate is", success_rate

	def run_algo(self,algo_name, scramble):
		self.persist = Persist()
		
		print "Starting run"
		solver = Solver()
		result = solver.solve(algo_name, scramble)
		print "Run complete, result:", result['success']

		self.persist.save_result(result)
		
		self.persist.save_latest_solve(result)
		return result['success']

	def run_algo_command(self, name, mode, num_times, scramble_type, break_early=False):
		scrambles = []
		print scramble_type
		if mode == 'random':
			num_times = 1
			for i in range(0,num_times):
				scrambles.append(Scrambler.gen_scramble())
		if mode == 'db':
			tmp = self.persist.get_scrambles( scramble_type)
			for scr in tmp:
				scram = scr['scramble']
				scrambles.append(scram)
		print "scram len:", len(scrambles)
		success_cnt = 0.0
		fail_cnt = 0.0
		for scram in scrambles:
			if self.run_algo(name, scram):
				success_cnt += 1
			else:
				fail_cnt += 1
			if break_early and fail_cnt / len(scrambles) > 1 - REQ_SUCCESS + 0.01: #epsilon
				return 0
		if success_cnt == 0:
			return 0.0
		success_rate = (success_cnt)/(success_cnt + fail_cnt)
		return success_rate

	def get_algo_result(self, name):
		algos = self.persist.list_results(name=name)
		success_cnt = 0
		fail_cnt = 0
		tot_success_moves = 0
		search_cnt = 0
		tot_time = 0
		for algo in algos:
			if algo['success']:
				success_cnt += 1
				tot_success_moves += algo['move_cnt']
				search_cnt += algo['search_cnt']
				tot_time += algo['time']
			else:
				fail_cnt += 1

		tot_cnt = success_cnt + fail_cnt
		avg_time = 0
		if tot_cnt > 0:
			search_cnt /= tot_cnt
			avg_time = tot_time / tot_cnt


		ret = {'success_cnt' : success_cnt,
				'fail_cnt' : fail_cnt,
				'tot_success_moves' : tot_success_moves,
				'search_cnt' : search_cnt,
				'tot_cnt' : tot_cnt,
				'avg_time' : avg_time}
		return ret

if __name__ == '__main__':
	Runner().menu()


	
