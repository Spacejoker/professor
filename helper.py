from algo import Rule_Lookup, Orientation_Lookup, Piece_Lookup
from cube import Face_Lookup, Turns
class Formatter():
	@staticmethod
	def rule_to_string(rule):
		if rule[0] == 'Inner':
			target = "Any"
			if rule[3] != None:
				target = Turns[rule[3]]
			return str(rule[0] + ", " + Rule_Lookup[rule[1]] + ", "  + str(rule[2]) + ", " + target)
		if rule[0] == 'Build_Edge':
			return str(rule[0] + ', Piece: ' + Piece_Lookup[rule[1]] + ", Orientation: " + Orientation_Lookup[rule[2]] + ", type: " + rule[3] +  ", position: " + str(map(str,rule[4])))
		return map(str, rule)
