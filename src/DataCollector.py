from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
import json
import sys 

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

        # Keep the useful informations only
        payload = {}
        payload['id'] = tweet['id']
        payload['created_at'] = tweet['created_at']
        payload['uid'] = tweet['user']['id']
        payload['text'] = tweet['text']
        payload['lang'] = tweet['lang']
        payload['geo'] = tweet['geo']

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

        # Handling the error when the characters are not all in unicode
        try:
            if self.output_file == None: json.dumps(payload)
            else: 
                self.f.write(json.dumps(payload))
                self.f.write("\n")
                # Printing progress bar
                sys.stdout.write('\r' + str(self.count) + "/" + str(self.maxcount) + " (" + str(self.count*100/self.maxcount) + "%) " +  progress)
                sys.stdout.flush()
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
