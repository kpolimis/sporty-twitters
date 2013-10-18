import json
import sys 
import os

def display_usage(name):
    print "Usage: python " + name + " input_file [output_file]"

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

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
        for u in sorted(set(users.keys())):
            line = str(u) + "," + str(users[u]) + "\n"
            out.write(line)
        out.close()
    else:
        for u in sorted(set(users.keys())):
            print str(u) + "," + str(users[u])
    return users

if __name__ == "__main__":
    nbargs = len(sys.argv)
    if nbargs <= 1 or nbargs > 3: # Wrong usage
        display_usage(sys.argv[0])
        exit()
    elif nbargs == 2:
        users = collect_users(sys.argv[1])
    else:
        users = collect_users(sys.argv[1], sys.argv[2])
        
