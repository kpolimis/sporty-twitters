import json
import argparse

# Initialize the args parser
parser = argparse.ArgumentParser(description='Organize the data in a CSV file from results.')

parser.add_argument('-i', type=str, help='file containing the results', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the data to plot', metavar="output-file")

def compute_scores(input_file, output_file):
	results = json.load(open(input_file))
	scores = []
	for u in results:
		user = results[u]
		score = user['avgprob']['4']*4
		scores.append(score)
	with open(output_file, "w") as f:
		for score in scores:
			f.write(str(score) + "\n")

if __name__ == "__main__":
	args = parser.parse_args()
	compute_scores(args.i, args.o)