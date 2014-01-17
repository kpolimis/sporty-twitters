import json
import random
import argparse
import os

# Initialize the args parser
parser = argparse.ArgumentParser(description='From a list of users L for which the friends have been collected using get_user_data.py, this script outputs a list of Twitter users randomly selected amongst the friends of L users and that is the same size of L.')

parser.add_argument('-i', type=str, help='list of users which have been processed', metavar="input-file", required=True)
parser.add_argument('-d', type=str, help='directory where the processed users data have been stored', required=True)
parser.add_argument('-o', type=str, help='file to output the new list of users', metavar="output-file", required=True)

def create_friends_list(input_file, output_file, directory):
	proc_users = json.load(open(input_file))
	new_users = []

	allfriends = []
	for u in proc_users:
		friends_file = directory + "/" + u + "/friends"
		if os.path.exists(friends_file):
			with open(friends_file) as f:
				friends = [int(line) for line in f]
			allfriends = list(set(allfriends + friends))

	i = len(proc_users)
	while i != 0:
		new_user = random.randrange(len(allfriends))
		if new_user not in new_users:
			new_users.append(allfriends[new_user])
			i -= 1

	with open(output_file, "w") as f:
		f.write(json.dumps(new_users))

if __name__ == "__main__":
	args = parser.parse_args()
	sportusers2friends(args.i, args.o, args.d)