import json
from tweets import Tweets
from utils import TwitterAPIUser
import time
import sys

class User(TwitterAPIUser):
    """docstring for User"""
    def __init__(self, user_id, settings_file=None):
        super(User, self).__init__(settings_file)
        self.user_id = user_id
        self.tweets = Tweets()

    def collect_tweets(self, count=3200, output_file=None, mode='a+'):
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
                            sys.stderr.write("Limit rate reached. Wait for 1 minute.\n")
                            sleep_sec = 60
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

