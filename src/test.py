import sporty.users as u
from os import listdir
from os.path import isfile, join
import sys

user_dir = '/data/1/sporty/users/'
friends_dir = '/data/1/sporty/friends/'
uids = [f for f in listdir(user_dir) if isfile(join(user_dir,f))]

print len(uids)
# uids = [111397971,1115884644,111636637,1118674309,1120500210,112091139,112203950,1122204780]

users = u.api(uids[-100:])
users.getMostSimilarFriend(user_dir, friends_dir)
