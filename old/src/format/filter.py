import sys 
import argparse
import json
from ..utils.ProgressBar import ProgressBar
import os
from ..utils.line_count import line_count

# Initialize the args parser
parser = argparse.ArgumentParser(description='Filter the tweets stored in a file given a list of keywords.')

parser.add_argument('-k', type=str, help='json file containing the keywords to filter', metavar="keyword-file", required=True)
parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")
parser.add_argument('-act', choices=['keep', 'remove'], default='keep', help='Action to do : keep the found tweets or remove them')

def filter_contains(input_file, keywords_file, output=None, rm=False):
    """Filter the data in the input_file. Keep (or delete if the rm flag is True) the tweets that contains the elements in a given list of keywords stored in a json file. If an output file is given, then the tweets are saved in it. Otherwise, it is printed in the standard output."""

    in_std_output = output == None # True if we need to print in stdout, False otherwise
    devnull = output == os.devnull

    result=[]
    keywords = json.load(open(keywords_file))

    # Setting up progress bar
    nb_lines = line_count(input_file)
    lineno = 0
    if devnull:
        bar = ProgressBar(30, output=os.devnull)
    else:
        bar = ProgressBar(30)

    # Filtering input_file
    with open(input_file) as f:
        for line in f:
            lineno += 1     # update progress bar variable
            find = False    # flag indicating that a keyword has been found
            write = False   # flag indicating that the line is going to be written

            for word in keywords:
                if line.lower().find(word.lower()) > -1:    # a keyword has been found in the line
                    find = True
                    break

            # if the required action is to keep lines with keywords : we write every lines in which a keyword has been found.
            if not rm and find:
                write = True
                result.append(line)

            # if the required action is to remove lines with keywords : we write every lines in which no keyword has been found.
            if rm and not find:
                write = True
                result.append(line)

            # updating progress bar view
            bar.update(float(lineno)/float(nb_lines))

    if not in_std_output:
        with open(output, "w") as f:
            f.write(json.dumps(result))
    else:
        sys.stdout.write(json.dumps(result))

    return result

if  __name__ == "__main__":
    # parse arguments
    args = parser.parse_args()
    filter_contains(args.i, args.k, args.o, args.act=='remove')
