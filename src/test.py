import sporty.users as u
from os import listdir
from os.path import isfile, join
import sys
import re

user_dir = '/data/1/sporty/users/'
friends_dir = '/data/1/sporty/friends/'
uids = [f for f in listdir(user_dir) if isfile(join(user_dir, f))]

# print len(uids)
# uids = [111397971,1115884644,111636637,1118674309,1120500210,112091139,112203950,1122204780]

api = u.api(uids[:1000])

# api.load(user_dir)
# api.loadFriends(friends_dir)

# for user in api.users:
#     m = re.match("([^,]+),\s+([A-Za-z]{2,})", user['location'])
#     if m:
#         print m.group(1, 2)

api.buildSimilarityMatrix(user_dir, friends_dir)
