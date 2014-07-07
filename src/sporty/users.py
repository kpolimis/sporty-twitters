import json
from tweets import Tweets
from utils import TwitterAPIUser
from datastructures import LSF
import time
import sys
import requests
import os.path


class api(TwitterAPIUser):
    def __init__(self, user_ids=[], settings_file=None):
        super(api, self).__init__(settings_file)
        self.loadUsers(user_ids)

    def loadUsers(self, user_ids=[]):
        if type(user_ids) == list:
            self.user_ids = user_ids
        elif type(user_ids) == int:
            self.user_ids = [user_ids]
        else:
            self.user_ids = LSF(user_ids).tolist()

    def getFriends(self, output_dir="./"):
        """
        Returns the list of friends (intersection between followees and followers) for a user.
        """
        for user_id in self.user_ids:
            user_path = os.path.join(output_dir, user_id)
            if os.path.isfile(user_path):  # friends list already exists for this user
                continue
            friends = set()
            cursor = -1
            followees = set()
            followers = set()
            # Get the followees

            while cursor != 0:
                try:
                    response = json.loads(self.getFolloweesStream(user_id, cursor).text)
                    if 'error' in response.keys() and response['error'] == 'Not authorized.':
                        break
                    if 'errors' in response.keys():
                        if response['errors'][0]['code'] == 88:
                            sleep_min = 5
                            sys.stderr.write(json.dumps(response) + "\n")
                            sys.stderr.write("Limit rate reached. Wait for " + str(sleep_min) +
                                             " minutes.\n")
                            sleep_sec = sleep_min*60
                            time.sleep(sleep_sec)
                        continue
                    cursor = response['next_cursor']
                    followees = followees.union(set(response['ids']))
                except Exception, e:
                    print response
                    raise e
            cursor = -1
            # Get the followers
            while cursor != 0:
                try:
                    response = json.loads(self.getFollowersStream(user_id, cursor).text)
                    if 'error' in response.keys() and response['error'] == 'Not authorized.':
                        break
                    if 'errors' in response.keys():
                        if response['errors'][0]['code'] == 88:
                            sleep_min = 5
                            sys.stderr.write(json.dumps(response) + "\n")
                            sys.stderr.write("Limit rate reached. Wait for " + str(sleep_min) +
                                             " minutes.\n")
                            sleep_sec = sleep_min*60
                            time.sleep(sleep_sec)
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
            if os.path.isfile(user_path):  # friends list already exists for this user
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
                                sys.stderr.write("Limit rate reached. Wait for " + str(sleep_min) +
                                                 " minutes.\n")
                                sleep_sec = sleep_min*60
                                time.sleep(sleep_sec)
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

    def show(self):
        """
        Returns the user objects using the Twitter API on a list of user ids.
        """
        extended = []
        for uid in self.user_ids:
            try:
                r = self.getUserShow(uid)
                if not r.get_iterator().results:
                    keep_try = False
                for item in r.get_iterator():
                    if 'message' in item.keys():
                        remaining = r.get_rest_quota()['remaining']
                        if not remaining:
                            sleep_min = 5
                            sys.stderr.write("Limit rate reached. Wait for " + str(sleep_min) +
                                             " minutes.\n")
                            sleep_sec = sleep_min*60
                            time.sleep(sleep_sec)
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

    def labelGender(self):
        males, females = getCensusNames()
        for tw in tweets:
            names = tw['user']['name'].lower().split()
            if len(names) == 0:
                names = ['']
            name = names[0]
            if name in males:
                tw['user']['gender'] = 'm'
            elif name in females:
                tw['user']['gender'] = 'f'
            else:
                tw['user']['gender'] = 'n'
        return tweets

    def getCensusNames():
        males_url = 'http://www.census.gov/genealogy/www/data/1990surnames/dist.male.first'
        females_url = 'http://www.census.gov/genealogy/www/data/1990surnames/dist.female.first'
        males = requests.get(males_url).text.split('\n')
        males = [m.split()[0].lower() for m in males if m]
        females = requests.get(females_url).text.split('\n')
        females = [f.split()[0].lower() for f in females if f]
        # Remove ambiguous names (those that appear on both lists)
        ambiguous = [f for f in females + males if f in males and f in females]
        males = [m for m in males if m not in ambiguous]
        females = [f for f in females if f not in ambiguous]
        return set(males), set(females)
