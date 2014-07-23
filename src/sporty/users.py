import json
import math
import os.path
import re
import requests
import sys
import time
from collections import defaultdict
from datastructures import LSF
from scipy.spatial.distance import cosine
from tweets import Tweets
from utils import TwitterAPIUser


class api(TwitterAPIUser):
    def __init__(self, user_ids=[], settings_file=None):
        super(api, self).__init__(settings_file)
        self.loadIds(user_ids)
        self.users = []
        self.friends = defaultdict(list)
        self.similarityMatrix = defaultdict(dict)
        self.sortedFriends = defaultdict(list)
        self.states = {
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
            }

    def loadIds(self, user_ids=[]):
        """
        Store a list of user IDs in the instance. This list will be used to
        load users and users' friends.
        """
        if type(user_ids) == list:
            self.user_ids = user_ids
        elif type(user_ids) == int:
            self.user_ids = [user_ids]
        else:
            self.user_ids = LSF(user_ids).tolist()

    def load(self, user_dir, debug=False):
        """
        For every user id, this function loads the user from a file which name
        matches with the user id in the given user_dir directory.
        """
        self.users = []
        debug_str = "Loading users: "
        user_list = self.user_ids[:1000]
        nb_uids = str(len(user_list))
        for i, uid in enumerate(user_list):
            if debug:
                sys.stderr.write(debug_str + str(i) + "/" + nb_uids + "\r")
            user_file = os.path.join(user_dir, str(uid))
            if os.path.isfile(user_file):
                with open(user_file) as uf:
                    line = uf.readline()
                    if line:
                        tw = json.loads(line)
                        user = tw['user']
                        self.users.append(user)
        if debug:
            sys.stderr.write(debug_str + "Done.\n")
        return self.users

    def loadFriends(self, friends_dir, debug=False):
        """
        For every user id, this function loads its friends from a file which
        name match with the user id in the given friends_dir directory.
        """
        self.friends = defaultdict(list)
        debug_str = "Loading friends: "
        user_list = self.user_ids[:1000]
        nb_uids = str(len(user_list))
        for i, uid in enumerate(user_list):
            friends_file = os.path.join(friends_dir, str(uid) + '.extended')
            if debug:
                sys.stderr.write(debug_str + str(i) + "/" + nb_uids + "\r")
            if os.path.isfile(friends_file):
                friends = self.friends[int(uid)]
                with open(friends_file) as ff:
                    for line in ff:
                        friends.append(json.loads(line))
        if debug:
            sys.stderr.write(debug_str + "Done.\n")
        return self.friends

    def outputFriendsIds(self, output_dir="./"):
        """
        Outputs the list of friends (intersection between followees and
        followers) for a user.
        """
        for user_id in self.user_ids:
            user_path = os.path.join(output_dir, user_id)
            if os.path.isfile(user_path):
            # friends list already exists for this user
                continue
            friends = set()
            cursor = -1
            followees = set()
            followers = set()
            # Get the followees

            while cursor != 0:
                try:
                    stream = self.getFolloweesStream(user_id, cursor)
                    response = json.loads(stream.text)
                    if 'error' in response.keys() \
                    and response['error'] == 'Not authorized.':
                        cursor = 0
                        break
                    if 'errors' in response.keys():
                        if response['errors'][0]['code'] == 88:
                            wait_for = self.getWaitTime('friends',
                                                        '/friends/ids')
                            self.__msg_wait(wait_for)
                        continue
                    cursor = response['next_cursor']
                    followees = followees.union(set(response['ids']))
                except Exception, e:
                    raise e
            cursor = -1
            # Get the followers
            while cursor != 0:
                try:
                    stream = self.getFollowersStream(user_id, cursor)
                    response = json.loads(stream.text)
                    if 'error' in response.keys() \
                    and response['error'] == 'Not authorized.':
                        cursor = 0
                        break
                    if 'errors' in response.keys():
                        if response['errors'][0]['code'] == 88:
                            wait_for = self.getWaitTime('friends',
                                                        '/followers/ids')
                            self.__msg_wait(wait_for)
                        continue
                    cursor = response['next_cursor']
                    followers = followers.union(set(response['ids']))
                except Exception, e:
                    raise e

            # Get the intersection between followers and followees
            friends = followees.intersection(followers)
            # Output the result
            with open(user_path, 'w') as f:
                for friend_id in friends:
                    f.write(str(friend_id) + "\n")

    def collectTweets(self, output_dir="./", count=3200):
        """
        Returns the 3200 last tweets of every user in user_ids.
        """
        for user_id in self.user_ids:
            user_path = os.path.join(output_dir, user_id)
            if os.path.isfile(user_path):
                # if friends list already exists for this user
                continue
            tweets = Tweets(user_path, 'a+')
            i = 0
            max_id = 0
            keep_try = True
            while keep_try:
                try:
                    r = self.getUserStream(user_id, max_id=max_id)
                    if not r.get_iterator().results:
                        keep_try = False
                    for item in r.get_iterator():
                        if 'message' in item.keys():
                            remaining = r.get_rest_quota()['remaining']
                            if not remaining:
                                sleep_min = 5
                                sleep_sec = sleep_min*60
                                self.__msg_wait(sleep_sec)
                                break
                            else:
                                sys.stderr.write(str(item) + "\n")
                        elif 'errors' in item.keys():
                            continue
                        else:
                            max_id = item['id'] - 1
                            tweets.append(item)
                            i += 1
                            if count and i >= count:
                                keep_try = False
                                break
                except Exception, e:
                    if item:
                        sys.stderr.write(str(item) + "\n")
                    raise e

    def extendFromIds(self):
        """
        Returns the user objects using the Twitter API for every user id.
        """
        extended = []
        user_ids = self.user_ids
        chunks = [user_ids[x:x+100] for x in xrange(0, len(user_ids), 100)]
        for uids in chunks:
            item = None
            try:
                r = self.getUserShow(uids)
                if not r.get_iterator().results:
                    keep_try = False
                for item in r.get_iterator():
                    if 'message' in item.keys():
                        remaining = r.get_rest_quota()['remaining']
                        if not remaining:
                            sleep_min = 5
                            sleep_sec = sleep_min*60
                            self.__msg_wait(sleep_sec)
                            break
                        else:
                            sys.stderr.write(str(item) + "\n")
                    elif 'errors' in item.keys():
                        continue
                    else:
                        extended.append(item)
            except Exception, e:
                if item:
                    sys.stderr.write(str(item) + "\n")
                raise e
        return extended

    def cosineSimilarity(self, u1, u2, f=lambda x: x):
        """
        Compute the cosine similarity between two users considering their
        statuses count, followees count, and friends count.
        """
        U1, U2 = [[f(u['statuses_count']),
                   f(u['friends_count']),
                   f(u['followers_count'])]
                  for u in (u1, u2)]
        return 1 - cosine(U1, U2)

    def getSimilarFriends(self, user_dir, friends_dir):
        def find(f, seq):
            for item in seq:
                if f(item):
                    return item
            return None

        log = lambda x: 0 if not x else math.log(x)

        self.load(user_dir, debug=True)
        self.loadFriends(friends_dir, debug=True)

        # Clean the list of users
        self.users = self.__filterUsers(self.users)

        # Filter the friends to keep the matching ones
        for u in self.users:
            self.friends[u['id']] = self.__filterUsers(self.friends[u['id']],
                                                       friends=True)

            ## GENDER
            gender_f = lambda f: f['gender'] == u['gender']
            self.friends[u['id']] = filter(gender_f,
                                           self.friends[u['id']])

            ## LOCATION
            location_filtered = []
            # match on exact location
            loc_exact_f = lambda f: f['location'] == u['location']
            location_filtered = filter(loc_exact_f,
                                       self.friends[u['id']])
            # match on same state
            if not location_filtered:
                loc_state_f = lambda f: f['location'][1] == u['location'][1]
                location_filtered = filter(loc_state_f,
                                           self.friends[u['id']])

            self.friends[u['id']] = location_filtered

        # Compute the similarity value between every user and each of their
        # friends
        for u in self.users:
            d = self.similarityMatrix[u['id']]
            ufriends = self.friends[u['id']]
            for f in ufriends:
                d[f['id']] = self.cosineSimilarity(f, u)  # , log)
            # Sort the friends by descending similarity
            sortedFriends = sorted(d, key=d.get, reverse=True)
            self.sortedFriends[u['id']] = [find(lambda x: x['id'] == uid,
                                                ufriends)
                                           for uid in sortedFriends]

        # Display
        # for u in self.users:
        #     print self.__displayUser(u)
        #     for f in self.sortedFriends[u['id']]:
        #         print self.__displayFriend(f, u, 1)
        return self.sortedFriends

    def labelGender(self, user, males, females):
        name = user['name'].lower().split()
        if len(name) == 0:
            name = ['']
        name = name[0]
        if name in males:
            user['gender'] = 'm'
        elif name in females:
            user['gender'] = 'f'
        else:
            user['gender'] = 'n'
        return user

    def getCensusNames(self):
        # males_url = 'http://www.census.gov/genealogy/www/data/'
        # + '1990surnames/dist.male.first'
        # females_url = 'http://www.census.gov/genealogy/www/data/'
        # + '1990surnames/dist.female.first'
        # males = requests.get(males_url).text.split('\n')
        # females = requests.get(females_url).text.split('\n')

        males = []
        females = []
        local_m = '/home/virgile/sporty-twitters/inputs/census/dist.male.first'
        local_f = '/home/virgile/sporty-twitters/inputs/census/' \
        + 'dist.female.first'
        with open(local_m) as males_f:
            for line in males_f:
                males.append(line)
        with open(local_f) as females_f:
            for line in females_f:
                females.append(line)

        males_dict = {}
        females_dict = {}
        for m in males:
            if m:
                entry = m.split()
                males_dict[entry[0].lower()] = float(entry[1])
        for f in females:
            if f:
                entry = f.split()
                females_dict[entry[0].lower()] = float(entry[1])
        # Remove ambiguous names (those that appear on both lists)
        males = males_dict
        females = females_dict
        ambiguous = {n: (males[n], females[n])
                     for n in females.keys() + males.keys()
                     if n in males and n in females}
        males = [m for m in males if m not in ambiguous]
        females = [f for f in females if f not in ambiguous]
        eps = 0.1
        todel = []
        for n in ambiguous:
            scores = ambiguous[n]
            if scores[0] > scores[1]+eps:
                males.append(n)
                todel.append(n)
            elif scores[0]+eps < scores[1]:
                females.append(n)
                todel.append(n)
        for n in todel:
            del ambiguous[n]
        return set(males), set(females)

    def __displayUser(self, u, indent=0):
        udisplay = ""
        udisplay += indent*"\t"
        udisplay += "- name: " + u['name'].encode('ascii', 'ignore')
        udisplay += ", gender: " + u['gender']
        udisplay += ", location: " + str(u['location'])
        udisplay += "\n"
        udisplay += indent*"\t"
        udisplay += "  statuses: " + str(u['statuses_count'])
        udisplay += ", followees: " + str(u['friends_count'])
        udisplay += ", followers: " + str(u['followers_count'])
        return udisplay

    def __displayFriend(self, user, parent, indent=0):
        udisplay = self.__displayUser(user, indent)
        udisplay += "\n"
        udisplay += indent*"\t"
        log = lambda x: 0 if not x else math.log(x)
        udisplay += "  similarity: "
        udisplay += str(self.similarityMatrix[parent['id']][user['id']])
        return udisplay

    def __filterUsers(self, users, friends=False):
        cityregex = re.compile("([^,]+),\s*([A-Za-z\s]{2,})")
        males, females = self.getCensusNames()

        ## LOCATION

        # only keep users that have a US formated location (e.g. 'Chicago, IL')
        users = filter(lambda u: cityregex.match(u['location']), users)

        accr_set = set(map(lambda x: x.lower(), self.states.keys()))
        states_set = set(map(lambda x: x.lower(), self.states.values()))
        allowed_set = accr_set.union(states_set)

        def group_location(user):
            user['location'] = cityregex.match(user['location']).group(1, 2)
            if user['location'][1].lower() in accr_set:
                user['location'] = (user['location'][0],
                                    self.states[user['location'][1].upper()])
            elif user['location'][1].lower() not in allowed_set:
                user['location'] = None

        map(group_location, users)

        # only keep users that have a defined location
        users = filter(lambda u: u['location'], users)

        ## GENDER

        # label users on gender
        map(lambda u: self.labelGender(u, males, females), users)
        # only keep users that have a non ambiguous gender
        users = filter(lambda u: u['gender'] != 'n', users)

        ## FRIENDS

        if not friends:
            # only keep users that have at least one friend
            users = filter(lambda u: self.friends[u['id']], users)

        return users

    def __msg_wait(self, wait_time):
        sys.stderr.write("Limit rate reached. Wait for "
                         + str(wait_time) + " seconds.\n")
        time.sleep(wait_time)
