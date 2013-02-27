from solver import Solver
from persist import Persist
from main import Scrambler
import random, string
import time
REQ_SUCCESS = 0.9

persist = Persist()
def run_algo(algo_name, scramble):
	persist = Persist()
	
	print "Starting run"
	solver = Solver()
	result = solver.solve(algo_name, scramble)
	print "Run complete, result:",result['success']

	persist.save_result(result)
	return result['success']
def run_algo_command(s, break_early=False):
	scrambles = []
	if len(s) > 2:
		if s[2] == 'random':
			num_times = 1
			if len(s) > 3:
				num_times = int(s[3])
			for i in range(0,num_times):
				scrambles.append(Scrambler.gen_scramble())
		if s[2] == 'db':
			tmp = persist.get_scrambles(scramble_type=s[3])
			for scr in tmp:
				scram = scr['scramble']
				scrambles.append(scram)
	print "scram len:", len(scrambles)
	success_cnt = 0.0
	fail_cnt = 0.0
	for scram in scrambles:
		if run_algo(s[1], scram):
			success_cnt += 1
		else:
			fail_cnt += 1
		if break_early and fail_cnt / len(scrambles) > 1 - REQ_SUCCESS + 0.01: #epsilon
			return 0

	success_rate = (success_cnt)/(success_cnt + fail_cnt)
	return success_rate

def get_algo_result(name):
	algos = persist.list_results(name=name)
	success_cnt = 0
	fail_cnt = 0
	tot_success_moves = 0
	search_cnt = 0
	for algo in algos:
		if algo['success']:
			success_cnt += 1
			tot_success_moves += algo['move_cnt']
			search_cnt += algo['search_cnt']
		else:
			fail_cnt += 1
	tot_cnt = success_cnt + fail_cnt
	ret = {'success_cnt' : success_cnt,
			'fail_cnt' : fail_cnt,
			'tot_success_moves' : tot_success_moves,
			'search_cnt' : search_cnt,
			'tot_cnt' : tot_cnt}
	return ret
def menu():
	while True:
		print "Enter command: "
		s = raw_input()
		s = s.split(" ")
		if s[0] == 'help':
			print ""
			print "HELP"
			print "run algo random/db scramble_type"
			print "add algoname filename"
			print "list"
			print "show algoname"
			print "rm algoname"
			print "rmstats algoname"
			print "stats algoname"
			print "addsc type count"
			print "listsc type"
			print "branch algoname tries (algotype)"
			print "rmsc (type)"
			print ""


		if s[0] == 'run':
			run_algo_command(s)
		if s[0] == 'add':
			name = s[1]
			filename = s[2]
			steps = []
			for line in open(filename,'r').readlines():
				next_line = line[:-1]#self.algo_steps.popleft()
				split = next_line.split('#')
				steps.append(split)

			algo = { 'name' : name,
					'steps' : steps }
			persist.add_algo(algo)

		if s[0] == 'list':
			algos = persist.list_algos()
			print ""
			print "Available algos:"
			for a in algos:
				print a['name']
			print ""	
		if s[0] == 'show':
			res = persist.get_algo(s[1])
			print ""
			print "Algo ", s[1], "described:"
			for key, value in res.items():
				print key,":",value
			print ""

		if s[0] == 'rm':
			persist.remove_algo(s[1])

		if s[0] == 'rmstats':
			name = s[1]
			persist.remove_results(name)

		if s[0] == 'stats':
			name = s[1]
			res = get_algo_result(name)
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
				print ""
			else:
				print "No successful data for ", name

		if s[0] == 'addsc':
			scramble_type = s[1]
			cnt = int(s[2])
			for i in range(0,cnt):
				persist.add_scramble({'scramble_type' : scramble_type,
							'scramble' : Scrambler.gen_scramble()})
		if s[0] == 'listsc':
			scramble_type = 'full'
			if len(s) > 1:
				scramble_type = s[1]
			#for s in persist.get_scrambles(scramble_type=scramble_type):
			for scram in persist.get_scrambles():
				print scram
		if s[0] == 'rmsc':
			sctype = None
			if len(s) > 1:
				sctype = s[1]
			persist.remove_scrambles(scramble_type = sctype)
		if s[0] == 'col':
			print persist.db.collection_names()
			#persist.db.problem_state.drop()

		if s[0] == 'branch':
			name = s[1]
			cnt = 1
			scramble_type = 'full'
			if len(s) > 2:
				cnt = int(s[2])
			if len(s) > 3:
				scramble_type = s[3]

			for i in range(0, cnt):
				limit = random.uniform(0.1, 0.5)
				keep_limit = random.uniform(0.0, 0.20)
				original = persist.get_algo(name)
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
						cands = 'r,f,l,u,d,b,U,D,R,F,L,B,rp,fp,lp,up,dp,bp,Dp,r U rp,rp U r, b U bp,bp U b,fp U f,F,R,L,B,Fp,Rp,Lp,Bp'
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
						'steps' : steps }
				print 'new_algo:', algo
				persist.add_algo(algo)

				#run the algo on type full
				success_rate = run_algo_command(['run',new_name,'db',scramble_type], break_early=True)
				
				if success_rate < 0.80:#remove everything that fails more than some %
					persist.remove_algo(new_name)
					print "removing algo",new_name,"since successrate is too low"
				print "success rate is", success_rate
	
		if s[0] == 't':
			for rec in persist.db.result.find():
				if 'name' in rec.keys():
					print rec['name']
if __name__ == '__main__':
	menu()


	
