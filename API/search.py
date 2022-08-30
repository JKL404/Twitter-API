import tweepy
from ssh.keys import *
import pandas as pd


class TwitterStream():
    def __init__(self, limit=10, filename="mytweets"):
        self.filename = f'{filename}.csv'
        self.limit = limit

        # authentication
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)

    def search_by_keywords(self, keywords):
        # search by keywords
        self.tweets = tweepy.Cursor(
            self.api.search_tweets, q=keywords, tweet_mode='extended').items(self.limit)
        return self.process_data()

    def search_by_user(self, user):
        self.tweets = tweepy.Cursor(
            self.api.user_timeline, screen_name=user, tweet_mode='extended').items(self.limit)
        return self.process_data()

    def process_data(self):
        # my own function to process twitter tweets
        try:
            columns = ['User', 'Tweet']
            data = []
            for tweet in self.tweets:
                data.append([tweet.user.screen_name, tweet.full_text])

            df = pd.DataFrame(data, columns=columns)
            try:
                df.to_csv(r'static/downloads/'+self.filename, sep='\t',
                          encoding='utf-8', header='true')
                return True
            except Exception as e:
                print(f"Error on Data while writing file : {e}")
        except Exception as e:
            print(f"Error on Data: {e}")
        return False
