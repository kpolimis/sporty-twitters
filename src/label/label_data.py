import argparse
import re
import fileinput
import json
import sys

def ask_label(first_input, incorrect_input, labels):
	ask = "\n" + first_input
	while True:
		try:
			l = raw_input(ask)
			if str(l) == 'q':
				l = str(l)
				break
			elif int(l) in labels:
				l = int(l)
				break
			else:
				ask = incorrect_input	
		except ValueError:
			ask = incorrect_input
			continue
	return l

def label(labels, input_file, output_file, begin_line=0, raw_json=False):
	# Set instructions for user
	first_input = "\nChoose label amongst " + str(labels) + " or (q)uit: "
	incorrect_input = "Incorrect input. " + first_input

	# Force labels to be a set
	labels = set(labels)

	with open(output_file, "a+") as o:
		with open(input_file, "r") as i:
			count = 0
			for line in i:
				if raw_json:
					tw = json.loads(line)
					line = tw['text']

				# read lines that are before the given beginning line
				if count < begin_line:
					count += 1
					continue
				# show the line and ask the user to choose a label
				sys.stdout.write(line)
				l = ask_label(first_input, incorrect_input, labels)
				if l == 'q':
					break

				if raw_json:
					tw['label'] = l
					outstr = json.dumps(tw) + "\n"
				else:
					outstr = line[:-1] + "\t" + str(l) + "\n"
				# output the line and the label separated by a tab
				o.write(outstr)
				o.flush()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", type=str)
	parser.add_argument("output_file", type=str)
	parser.add_argument("labels", type=int, nargs='+')
	parser.add_argument("-l", "--line", type=int, nargs='?', default=0)
	parser.add_argument("--raw-json", "--json", dest='raw_json', action='store_true')
	parser.set_defaults(raw_json=False)
	args = parser.parse_args()
	label(args.labels, args.input_file, args.output_file, args.line, args.raw_json)
    
