def line_count(path):
	count = 0
	with open(path) as f:
		for line in f:
			count += 1
	return count