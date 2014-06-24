import json
from tweets import Tweets
from utils import TwitterAPIUser
import time
import sys
import requests


class api(TwitterAPIUser):
    def __init__(self, user_id=0, settings_file=None):
        super(api, self).__init__(settings_file)
        self.user_id = user_id
        self.tweets = Tweets()
        self.friends = set()

    def getFriends(self):
        """
        Returns the list of friends (intersection between followees and followers) for a user.
        """
        cursor = -1
        followees = set()
        followers = set()
        # Get the followees
        while cursor != 0:
            try:
                response = json.loads(self.getFolloweesStream(self.user_id, cursor).text)
                if 'errors' in response.keys():
                    sleep_min = 5
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
                response = json.loads(self.getFollowersStream(self.user_id, cursor).text)
                if 'errors' in response.keys():
                    sys.stderr.write("Limit rate reached. Wait for 2 minutes.\n")
                    sleep_sec = 120
                    time.sleep(sleep_sec)
                    continue
                cursor = response['next_cursor']
                followers = followers.union(set(response['ids']))
            except Exception, e:
                raise e
        # Return the intersection between followers and followees
        self.friends = followees.intersection(followers)
        return self.friends

    def collectTweets(self, count=3200, output_file=None, mode='a+'):
        """
        Returns the 3200 last tweets of a user.
        """
        self.tweets = Tweets(output_file, mode)
        i = 0
        max_id = 0
        while True:
            try:
                r = self.getUserStream(self.user_id, max_id=max_id)
                if not r.get_iterator().results:
                    return self.tweets
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
                        self.tweets.append(item)
                        i += 1
                        if count and i >= count:
                            return self.tweets
            except Exception, e:
                raise e

    def genderFromCensus(self):
        males, females = get_census_names()
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

    def get_census_names():
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
