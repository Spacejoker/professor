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
					scrambles.append(Scrambler.gen_scramble())
				if s[2] == 'db':
					scrambles = persist.get_scrambles()
			for scram in scrambles:
				run_algo(s[1] + ".algo", scram)

if __name__ == '__main__':
	menu()


	
