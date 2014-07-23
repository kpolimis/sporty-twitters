import mood
import tweets
import users
import utils
import sys


class api():
    """
    Main API that centralizes/wraps all the other APIs so that the user does
    not have to worry about which API instanciate.
    """
    def __init__(self, settings_file=None):
        self.tweets = tweets.api(settings_file)
        self.mood = mood.api()
        self.users = users.api(settings_file=settings_file)
