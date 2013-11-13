from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from ProgressBar import ProgressBar
import json

class DataCollector(StreamListener):
    count = 0
    maxcount = 0
    output_file = None
    f = None
    bar = None

    def __init__(self, api=None, maxcount=10, output_file=None):
        super(DataCollector, self).__init__(api)
        self.maxcount = maxcount
        self.output_file = output_file
        self.bar = ProgressBar(size=30)

    def on_data(self, data):
        # Opening the file for the first and only time
        if self.count == 0 and self.output_file != None:
            self.f = open(self.output_file, 'w')
            
        self.count += 1
        tweet = json.loads(data)

        # Keep the useful informations only
        payload = {}
        payload['id'] = tweet['id']
        payload['created_at'] = tweet['created_at']
        payload['uid'] = tweet['user']['id']
        payload['text'] = tweet['text']
        payload['lang'] = tweet['lang']
        payload['geo'] = tweet['geo']

        # Handling the error when the characters are not all in unicode
        try:
            if self.output_file == None: print json.dumps(payload)
            else: 
                self.f.write(json.dumps(payload))
                self.f.write("\n")
                # Printing progress bar
                self.bar.update(float(self.count)/float(self.maxcount))
        except UnicodeEncodeError:
            self.count -= 1
            return
        
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
