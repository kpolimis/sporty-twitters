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

class DataCollector(StreamListener):
    count = 0
    maxcount = 0
    output_file = None
    f = None

    def __init__(self, api=None, maxcount=10, output_file=None):
        super(DataCollector, self).__init__(api)
        self.maxcount = maxcount
        self.output_file = output_file

    def on_data(self, data):
        # Opening the file for the first and only time
        if self.count == 0 and self.output_file != None:
            self.f = open(self.output_file, 'w')
            
        self.count += 1
        tweet = json.loads(data)

        encoder = json.JSONEncoder()

        # Keeping useful data
        payload = "{"
        payload += "'id': '" + str(tweet['id']) + "',"
        # to get the real posted time, we can use the user time zone
        payload += "'created_at': '" + tweet['created_at'] + "',"
        payload += "'userid': '" + str(tweet['user']['id']) + "',"
        payload += "'text':" + encoder.encode(tweet['text']) + ","
        payload += "'lang': '" + tweet['user']['lang'] + "',"
        payload += "'geo': " + str(tweet['geo']) + "}\n"

        try:
            if self.output_file == None: print payload
            else: 
                self.f.write(payload)
                self.f.flush()
        except UnicodeEncodeError: # Handling the error when the characters are not all in unicode
            self.count -= 1
            return
        
        # Building progress bar
        percent = float(self.count)/float(self.maxcount)
        progress = "["
        barsize = 20
        for i in range(0,barsize-1):
            step = 1./float(barsize)
            if percent-step >= step:
                progress += "="
            elif percent-step < 0:
                progress += " "
            percent -= step
        progress += "]"

        # Printing progress bar
        sys.stdout.write('\r' + str(self.count) + "/" + str(self.maxcount) + " (" + str(self.count*100/self.maxcount) + "%) " +  progress)
        sys.stdout.flush()

        if self.count < self.maxcount:
            # Waiting for another tweet
            return True
        else: 
            # Closing the file and ending the collect of tweets
            if self.output_file != None:
                self.f.close()
                print ""
            return False

    def on_error(self, status):
        print "Error " + status

def display_usage(name):
    print "Usage: python " + name + " nb_tweets [output_file]"

if __name__ == '__main__':
    if len(sys.argv) == 1:
        display_usage(sys.argv[0])
        exit
    elif len(sys.argv) == 2:
        nbtweets = int(sys.argv[1])
        c = DataCollector(maxcount = nbtweets)
    elif len(sys.argv) == 3:
        nbtweets = int(sys.argv[1])
        c = DataCollector(maxcount=nbtweets, output_file=sys.argv[2])

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, c)
    stream.filter(track=['runkeeper,nikeplus,runtastic,endomondo'], languages=['en', 'en_EN', 'en_GB', 'en_US', 'en_CA', 'None'])
