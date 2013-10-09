from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
import simplejson as json

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key=""
consumer_secret=""

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=""
access_token_secret=""

class DataCollecter(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        payload = "{"
        payload += "'id': '" + str(tweet['id']) + "',"
        payload += "'created_at': '" + tweet['created_at'] + "',"
        payload += "'userid': '" + str(tweet['user']['id']) + "',"
        payload += "'text': '" + tweet['text'] + "',"
        payload += "'geo': '" + str(tweet['geo']) + "}"
        print payload
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    c = DataCollecter()

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, c)
    stream.filter(track=['runkeeper,nikeplus,runtastic,endomondo'],
                  languages=['en', 'en_EN', 'en_US', 'en_CA'])

    api = API(auth)

    # users = api.lookup_users(screen_names=['virgilelandeiro'])
    # users = api.lookup_users(user_ids=[257548783])

    # for user in users:
    #     timeline = user.timeline()
    #     for status in timeline:
    #         print status.text
    
        
                             
