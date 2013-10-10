from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
import simplejson as json
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
            if self.output_file == None: print payload
            else: 
                self.f.write(payload)
                self.f.flush()

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
