from DataCollector import DataCollector
import sys
from tweepy import OAuthHandler
from tweepy import Stream
import json

def display_usage(name):
    print "Usage: python " + name + " nb_tweets [output_file]"

if __name__ == '__main__':
    nbargs = len(sys.argv)
    if nbargs <= 1 or nbargs > 3 : # Wrong usage
        display_usage(sys.argv[0])
        exit()
    elif nbargs == 2: # Output collect to stdout
        nbtweets = int(sys.argv[1])
        c = DataCollector(maxcount = nbtweets)
    else: # Output collect in a file
        nbtweets = int(sys.argv[1])
        c = DataCollector(maxcount=nbtweets, output_file=sys.argv[2])

    # Parsing settings file to get the developer key, secret and token.
    json_file = open('settings.json')
    settings = json.load(json_file)
    json_file.close()

    consumer_key = settings['consumer_key']
    consumer_secret = settings['consumer_secret']
    access_token = settings['access_token']
    access_token_secret = settings['access_token_secret']

    # Authenticate to the twitter API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, c)

    # Start to collect tweets
    stream.filter(track=['runkeeper,nikeplus,runtastic,endomondo'], languages=['en', 'en_EN', 'en_GB', 'en_US', 'en_CA', None])
