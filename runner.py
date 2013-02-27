from solver import Solver
from persist import Persist
from main import Scrambler


def run_algo(algo_name, scramble):
	persist = Persist()
	
	print "Starting run"
	solver = Solver()
	result = solver.solve(algo_name, scramble)
	print "Run complete, result:"
	print result, "\n"

	persist.save_result(result)

def menu():
	persist = Persist()
	while True:
		print "Enter command: "
		s = raw_input()
		s = s.split(" ")

		if s[0] == 'run':
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
			for scram in scrambles:
				run_algo(s[1], scram)

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
		
		if s[0] == 'stats':
			name = s[1]
			algos = persist.list_results(name=name)
			success_cnt = 0
			fail_cnt = 0
			tot_success_moves = 0
			for algo in algos:
				if algo['success']:
					success_cnt += 1
					tot_success_moves += algo['move_cnt']
				else:
					fail_cnt += 1
			tot_cnt = success_cnt + fail_cnt
			print "Total stats for ", name,":"
			print "Succes %:",(success_cnt)/(tot_cnt+0.0)*100.0, "(",success_cnt,"/",tot_cnt,")"
			print "Avg moves",tot_success_moves/success_cnt

		if s[0] == 'addsc':
			scramble_type = s[1]
			cnt = int(s[2])
			for i in range(0,cnt):
				persist.add_scramble({'scramble_type' : scramble_type,
							'scramble' : Scrambler.gen_scramble()})
		if s[0] == 'listsc':
			scramble_type = s[1]
			#for s in persist.get_scrambles(scramble_type=scramble_type):
			for s in persist.get_scrambles():
				print s

		if s[0] == 'col':
			print persist.db.collection_names()
			#persist.db.problem_state.drop()
if __name__ == '__main__':
	menu()


	
