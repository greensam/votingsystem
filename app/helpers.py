def round2(yes, no, abstain):
	if yes > no and yes > 2*abstain:
		return "In"
	elif yes == no and float(abstain)/(yes + no) < 0.5:
		return "In"
	else:
		return "Out"

def round3(yes, no, abstain):
	if yes > no and yes > abstain:
		return "In"
	else:
		return "Out"

def final_dinner(yes, no, abstain):
	if yes > (no + abstain):
		return "In" 
	else:
		return "Out"


def get_formula(round):
	if round == "round2":
		return round2
	elif round == "round3":
		return round3
	elif round == "final_dinner":
		return final_dinner
	else:
		raise ValueError("No Function for Specified Round")