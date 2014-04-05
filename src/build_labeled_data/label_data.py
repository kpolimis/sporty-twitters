import argparse
import re
import fileinput
import sys

def ask_label(first_input, incorrect_input, labels):
	ask = first_input
	while True:
		l = raw_input(ask)
		if str(l) == 'q':
			l = str(l)
			break
		elif int(l) in labels:
			l = int(l)
			break
		else:
			ask = incorrect_input	
	return l

def label(labels, input_file, output_file, begin_line=0):
	# Set instructions for user
	first_input = "Choose label amongst " + str(labels) + " or (q)uit: "
	incorrect_input = "Incorrect input. " + first_input

	# Force labels to be a set
	labels = set(labels)

	with open(output_file, "a+") as o:
		with open(input_file, "r") as i:
			count = 0
			for line in i:
				# read lines that are before the given beginning line
				if count < begin_line:
					count += 1
					continue
				# show the line and ask the user to choose a label
				sys.stdout.write(line)
				l = ask_label(first_input, incorrect_input, labels)
				if l == 'q':
					break
				# output the line and the label separated by a tab
				o.write(line[:-1] + "\t" + str(l) + "\n")
				o.flush()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", type=str)
	parser.add_argument("output_file", type=str)
	parser.add_argument("labels", type=int, nargs='+')
	parser.add_argument("-l", "--line", type=int, nargs='?', default=0)
	args = parser.parse_args()

	label(args.labels, args.input_file, args.output_file, args.line)
