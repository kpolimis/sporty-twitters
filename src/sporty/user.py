import json
from tweets import Tweets
from utils import TwitterAPIUser
import time
import sys


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
                    sys.stderr.write("Limit rate reached. Wait for 2 minutes.\n")
                    sleep_sec = 120
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
                            sys.stderr.write("Limit rate reached. Wait for 2 minutes.\n")
                            sleep_sec = 120
                            time.sleep(sleep_sec)
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
