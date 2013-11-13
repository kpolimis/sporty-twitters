import sys 
import argparse
import json

# Initialize the args parser
parser = argparse.ArgumentParser(description='Filter the tweets stored in a file given a list of keywords.')

parser.add_argument('-k', type=str, help='json file containing the keywords to filter', metavar="keyword-file", required=True)
parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")
parser.add_argument('-act', choices=['keep', 'remove'], default='keep')

def filter_contains(input_file, keywords_file, output=None, rm=False):
    """Filter the data in the input_file. Keep (or delete if the rm flag is True) the tweets that contains the elements in a given list of keywords stored in a json file. If an output file is given, then the tweets are saved in it. Otherwise, it is printed in the standard output."""

    in_std_output = output == None # True if we need to print in stdout, False otherwise

    if not in_std_output:
        out = open(output, 'w')

    result=""

    keywords = json.load(open(keywords_file))

    with open(input_file) as f:
        for line in f:
            find = False
            write = False
            for word in keywords:
                if line.lower().find(word.lower()) > -1:
                    find = True
                    break

            if not rm and find: 
                write = True
                result += line
            if rm and not find:
                write = True
                result += line

            if write and in_std_output:
                sys.stdout.write(line)
                sys.stdout.flush()
            elif write and not in_std_output:
                out.write(line)

    if not in_std_output:
        out.close()

    return result

if  __name__ == "__main__":
    args = parser.parse_args()
    filter_contains(args.i, args.k, args.o, args.act=='remove')
