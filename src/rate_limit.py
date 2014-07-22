"""
Usage: rate_limit -h | --help
       rate_limit show <settings_file>
"""
from TwitterAPI import TwitterAPI
from docopt import docopt
import json


def main():
    args = docopt(__doc__)
    if args['show']:
        with open(args['<settings_file>']) as settings_f:
            settings = json.load(settings_f)
            consumer_key = settings['consumer_key']
            consumer_secret = settings['consumer_secret']
            access_token = settings['access_token']
            access_token_secret = settings['access_token_secret']
            twitterapi = TwitterAPI(consumer_key, consumer_secret,
                                    access_token, access_token_secret)
            r = twitterapi.request('application/rate_limit_status')
            print r.text

if __name__ == '__main__':
    main()
