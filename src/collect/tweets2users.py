import json
import sys 
import argparse
from ..utils.ProgressBar import ProgressBar

# Initialize the args parser
parser = argparse.ArgumentParser(description='Create a list of unique users from a dataset of tweets')

parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")

def tweets2users(input_file, output=None):
    """Collect the unique users and store them into a file with the number of their tweets"""
    if output != None:
        out = open(output, 'w')
    users = {} # dictionary of all the users
    nb_lines = 0
    with open(input_file) as f:
        for line in f:
            nb_lines += 1
            pass
    lineno = 0
    bar = ProgressBar(30)

    with open(input_file) as f:
        for line in f:
            lineno += 1
            tweet = json.loads(line)
            uid = tweet['uid']
            if uid in users.keys():
                users[uid] += 1
            else:
                users[uid] = 1
            bar.update(float(lineno)/float(nb_lines))
    if output != None:
        out.write(json.dumps(users))
    else:
        print json.dumps(users)
    return users

if __name__ == "__main__":
    args = parser.parse_args()
    tweets2users(args.i, args.o)
        