import sys
import json
import config
import signal
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from sentiment_analysis import save
from sentiment_analysis import tweet_processor


def sigint_handler(signal, frame):
    save()


class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data, encoding='utf-8')
        tweet_processor(tweet)

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    try:
        listener = StdOutListener()
        auth = OAuthHandler(config.keys['consumer_key'], config.keys['consumer_secret'])
        auth.set_access_token(config.keys['access_token'], config.keys['access_token_secret'])
        stream = Stream(auth, listener)

        signal.signal(signal.SIGINT, sigint_handler)
        # stream.filter(track=['Curitiba_PMC', 'belemfala', 'prefsp', 'Prefeitura_Rio', 'prefeiturabh'])
        stream.filter(track=['pecesiqueira', 'naosalvo', 'rafinhabastos', 'jovemnerd', 'mkarolqueiroz', 'felipenetoreal', 'belpesce', 'dilma', 'cunha'])
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except AttributeError:
        sys.exit(0)
    except:
        sys.exit(0)
