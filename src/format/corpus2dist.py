from collections import Counter
import argparse
import json

# Initialize the args parser
parser = argparse.ArgumentParser(description='Create the users distribution in a CSV file from a corpus.')

parser.add_argument('-i', type=str, help='file containing the corpus', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the users distribution', metavar="output-file")

def corpus2dist(input_file, output_file):
	corpus = json.load(open(input_file))

	nbs = []
	for u in corpus:
		user = corpus[u]
		nbs.append(user['nbtweets'])

	count = Counter(nbs)
	count = count.most_common(len(count))

	with open(output_file, "w") as f:
		for pair in count:
			f.write(str(pair[0]) + "," + str(pair[1]) + "\n")

if __name__ == "__main__":
	args = parser.parse_args()
	corpus2dist(args.i, args.o)
