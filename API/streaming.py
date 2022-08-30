import tweepy
from ssh.keys import *
import pandas as pd
import json

# authentication
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# Processing Count, data global variable
columns = ['User', 'Tweet']
data = []
count = 1
maxcount = 0
filename = ''
process_status = False


def process_data(response):
    # my own function to process twitter
    global data, count, maxcount, filename, process_status
    try:
        tweet = json.loads(response.decode('utf-8'))
        # if tweet.get('user', {}).get('verified', ''):
        if True:
            # if user is verified only count tweets
            if not tweet.get('truncated', ''):
                data.append(
                    [tweet.get('user', {}).get('screen_name', ''), tweet.get('text', '')])
            else:
                data.append([tweet.get('user', {}).get('screen_name', ''),
                            tweet.get('extended_tweet', {}).get('full_text', '')])

            # checking no of count
            if count < maxcount:
                count += 1
            else:
                df = pd.DataFrame(data, columns=columns)
                # print(df)
                try:
                    df.to_csv(r'static/downloads/'+filename, sep='\t',
                              encoding='utf-8', header='true')
                    process_status = True  # flag value for success
                except Exception as e:
                    print(f"Error on Data while writing file : {e}")
                return True

    except Exception as e:
        print(f"Error on Data: {e}")
    return False

# Streaming Data


class MyStreamListener(tweepy.Stream):
    tweets = []
    limit = 1

    def on_status(self, status):
        self.tweets.append(status)
        # print(status.user.screen_name + ": " + status.text)

        if len(self.tweets) == self.limit:
            self.disconnect()

    def on_data(self, raw_data):
        try:
            tweet_status = process_data(raw_data)
            # if total no of count is completed
            if tweet_status:
                self.disconnect()
        except Exception as e:
            print(f"Error on Data: {e}")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print('data failed')
            return False


class TwitterStream():
    def __init__(self, usermax=10, file="mytweets"):
        global maxcount, filename, process_status
        maxcount = usermax
        filename = f'{file}.csv'
        self.stream = MyStreamListener(
            API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    def search_by_keywords(self, keywords):
        # stream by keywords
        self.stream.filter(track=keywords, languages=["en"])
        return process_status

    def search_by_user(self, users):
        user_ids = []

        for user in users:
            user_ids.append(api.get_user(screen_name=user).id)

        self.stream.filter(follow=user_ids)
        return process_status
