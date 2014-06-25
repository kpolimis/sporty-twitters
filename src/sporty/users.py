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
            friends = set()
            cursor = -1
            followees = set()
            followers = set()
            # Get the followees
            while cursor != 0:
                try:
                    response = json.loads(self.getFolloweesStream(user_id, cursor).text)
                    if 'errors' in response.keys():
                        sleep_min = 5
                        sys.stderr.write(json.dumps(response))
                        sys.stderr.write("Limit rate reached. Wait for " + str(sleep_min) +
                                         " minutes.\n")
                        sleep_sec = sleep_min*60
                        time.sleep(sleep_sec)
                        continue
                    cursor = response['next_cursor']
                    followees = followees.union(set(response['ids']))
                except Exception, e:
                    raise e
            cursor = -1
            # Get the followers
            while cursor != 0:
                try:
                    response = json.loads(self.getFollowersStream(user_id, cursor).text)
                    if 'errors' in response.keys():
                        sleep_min = 5
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
            user_path = os.path.join(output_dir, user_id)
            if os.path.isfile(user_path):  # friends list already exists for this user
                return
            with open(user_path, 'w') as f:
                for friend_id in friends:
                    f.write(str(friend_id) + "\n")

    def collectTweets(self, output_dir="./", count=3200):
        """
        Returns the 3200 last tweets of a user.
        """
        for user_id in user_ids:
            user_path = os.path.join(output_dir, user_id)
            if os.path.isfile(user_path):  # friends list already exists for this user
                return
            tweets = Tweets(user_path, 'a+')
            i = 0
            max_id = 0
            while True:
                try:
                    r = self.getUserStream(user_id, max_id=max_id)
                    if not r.get_iterator().results:
                        return tweets
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
                        else:
                            max_id = item['id'] - 1
                            tweets.append(item)
                            i += 1
                            if count and i >= count:
                                return tweets
                except Exception, e:
                    raise e

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
