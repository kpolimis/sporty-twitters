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
        self.most_similar_list = []
        self.filter_stats = defaultdict(int)  # list)
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

    def __msg_wait(self, wait_time):
        sys.stderr.write("Limit rate reached. Wait for "
                         + str(wait_time) + " seconds.\n")
        time.sleep(wait_time)

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
                    if 'error' in response.keys() and response['error'] == 'Not authorized.':
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
                    if 'error' in response.keys() and response['error'] == 'Not authorized.':
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
                        if 'error' in response.keys() and response['error'] == 'Not authorized.':
                            cursor = 0
                            break
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

    def __getUser(self, uid, user_dir):
        """
        Load the details of a user given its user identifier.
        """
        user_file = os.path.join(user_dir, str(uid))
        if os.path.isfile(user_file):
            with open(user_file) as uf:
                line = uf.readline()
                if line:
                    tw = json.loads(line)
                    user = tw['user']
                    return user
        else:
            return False

    def __getFriends(self, uid, friends_dir):
        friends_file = os.path.join(friends_dir, str(uid) + '.extended')
        if os.path.isfile(friends_file):
            with open(friends_file) as ff:
                for line in ff:
                    yield json.loads(line)

    def __processUser(self, u, males, females, user_dir, friends_dir,
                      use_tweets=True, is_friend=False):
        cityregex = re.compile("([^,]+),\s*([A-Za-z\s]{2,})")
        accr_set = set(map(lambda x: x.lower(), self.states.keys()))
        states_set = set(map(lambda x: x.lower(), self.states.values()))
        inspected = []

        def find_location_in_tweets(u):
            if not use_tweets or u['id'] in inspected:
                return u, False
            else:
                inspected.append(u['id'])
            utweets = Tweets(os.path.join(user_dir, str(u['id'])))
            found_location = False

            for t in utweets:
                if t['place'] and t['place']['full_name']:
                    u['location'] = t['place']['full_name']
                    found_location = True
                    break
            return u, found_location

        if is_friend:
            self.filter_stats['friends'] += 1
        else:
            self.filter_stats['users'] += 1

        if not u['location']:
            if is_friend:
                self.filter_stats['friend_empty_location'] += 1
                return False
            else:
                self.filter_stats['user_empty_location'] += 1
                u, found_location = find_location_in_tweets(u)
                if found_location:
                    self.filter_stats['user_location_via_tweets'] += 1
                else:
                    return False

        if not cityregex.match(u['location']):
            if is_friend:
                self.filter_stats['friend_not_matching_regex'] += 1
                return False
            else:
                self.filter_stats['user_not_matching_regex'] += 1
                u, found_location = find_location_in_tweets(u)
                if found_location:
                    if cityregex.match(u['location']):
                        self.filter_stats['user_location_via_tweets'] += 1
                    else:
                        return False
                else:
                    return False

        u['location'] = cityregex.match(u['location']).group(1, 2)
        if u['location'][0].lower() in states_set and u['location'][0] == 'USA':
            u['location'] = ('', u['location'][1])
        elif u['location'][1].lower() in accr_set:
            u['location'] = (u['location'][0],
                             self.states[u['location'][1].upper()])
        elif u['location'][1].lower() not in states_set:
            if is_friend:
                self.filter_stats['friend_no_matching_state'] += 1
            else:
                self.filter_stats['user_no_matching_state'] += 1
            return False

        self.labelGender(u, males, females)
        if u['gender'] == 'n':
            if is_friend:
                self.filter_stats['friend_ambiguous_gender'] += 1
            else:
                self.filter_stats['user_ambiguous_gender'] += 1
            return False

        if is_friend:
            return u

        return self.__getFriends(u['id'], friends_dir)

    def getMostSimilar(self, u, males, females,
                       user_dir, friends_dir,
                       use_tweets=True, is_friend=False):
        log = lambda x: 0 if not x else math.log(x)
        # clean a user and get his/her friends
        friends = self.__processUser(u, males, females, user_dir, friends_dir,
                                     use_tweets=use_tweets)
        if not friends:
            return False

        most_similar = (0, 0)  # tuple (uid, cosine_similarity)
        i = 0
        for f in friends:
            i += 1
            f = self.__processUser(f, males, females, user_dir,
                                   friends_dir, use_tweets=use_tweets,
                                   is_friend=True)
            if not f:
                continue
            # filter on gender
            if f['gender'] != u['gender']:
                self.filter_stats['different_gender'] += 1
                continue
            # filter on location
            if f['location'][1] != u['location'][1]:
                self.filter_stats['different_location'] += 1
                continue

            # is this user the most similar until now?
            self.filter_stats['friend_OK'] += 1
            similarity = self.cosineSimilarity(f, u, log)
            if similarity > most_similar[1]:
                most_similar = (f['id'], similarity)

        if i == 0:
            self.filter_stats['user_no_friends_loaded'] += 1
        else:
            self.filter_stats['user_with_friends'] += 1
        u['most_similar'] = most_similar if most_similar != (0, 0) else None
        return u

    def getSimilarFriends(self, user_dir, friends_dir, use_tweets=True):
        males, females = self.getCensusNames()
        for uid in self.user_ids:
            u = self.__getUser(uid, user_dir)
            if not u:  # cannot load the user
                self.filter_stats['cannot_load_user'] += 1
                continue
            u = self.getMostSimilar(u, males, females, user_dir, friends_dir,
                                    use_tweets=use_tweets)

            if u and u['most_similar']:
                fid = u['most_similar'][0]
                similarity = u['most_similar'][1]
                entry = (uid, fid, similarity)
                print ";".join(map(str, entry))
                self.most_similar_list.append(entry)

        for k in self.filter_stats:
            sys.stderr.write(k + " " + str(self.filter_stats[k]) + "\n")

        return self.most_similar_list

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
        local_f = '/home/virgile/sporty-twitters/inputs/census/dist.female.first'
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
