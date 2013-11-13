import json
import sys 
import argparse

# Initialize the args parser
parser = argparse.ArgumentParser(description='Create a list of unique users from a dataset of tweets')

parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")

def collect_users(input_file, output=None):
    """Collect the unique users and store them into a file with the number of their tweets"""
    if output != None:
        out = open(output, 'w')
    users = {} # dictionary of all the users
    with open(input_file) as f:
        for line in f:
            tweet = json.loads(line)
            uid = tweet['uid']
            if uid in users.keys():
                users[uid] += 1
            else:
                users[uid] = 1
    if output != None:
        out.write(json.dumps(users))
    else:
        print json.dumps(users)
    return users

if __name__ == "__main__":
    args = parser.parse_args()
    collect_users(args.i, args.o)
        