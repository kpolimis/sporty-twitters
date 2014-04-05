import re
import sys

def pprint(toprint):
	if type(toprint) == file:
		lines = [l[:-1] for l in toprint]
	elif type(toprint) == str:
		lines = toprint.splitlines()

	i = 1
	for l in lines:
		print str(i) + ". " + l
		i += 1

def print_header(header, underlined_char="-", under=True, over=False):
	if over:
		print underlined_char*len(header)
	print header
	if under:
		print underlined_char*len(header)