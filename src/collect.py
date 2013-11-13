from DataCollector import DataCollector
from tweepy import OAuthHandler
from tweepy import Stream
import json
import argparse

# Initialize the args parser
parser = argparse.ArgumentParser(description='Collect the tweets related to sport-tracker apps.')

parser.add_argument('-N', type=int, help='number of tweets to collect', metavar="quantity", required=True)
parser.add_argument('-o', type=str, help='file to output the collected tweets', metavar="output-file")
parser.add_argument('-s', type=str, help='json file containing the Twitter API key and token', metavar="settings-file", default="settings.json")

if __name__ == '__main__':
    args = parser.parse_args()

    c = DataCollector(maxcount=args.N, output_file=args.o)

    # Parsing settings file to get the developer key, secret and token.
    settings = json.load(open(args.s))

    consumer_key = settings['consumer_key']
    consumer_secret = settings['consumer_secret']
    access_token = settings['access_token']
    access_token_secret = settings['access_token_secret']

    # Authenticate to the twitter API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, c)

    # Start to collect tweets
    stream.filter(track=['runkeeper,nikeplus,runtastic,endomondo,facebook'], languages=['en', 'en_EN', 'en_GB', 'en_US', 'en_CA', None])
