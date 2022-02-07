import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary
    """
    SIA = SentimentIntensityAnalyzer()
    user_dict = {}
    user_obj = api.get_user(screen_name=name)
    count = 100
    tweets_obj = tweepy.Cursor(api.user_timeline, id=name).items(count)
    tweets = []
    for tweet in tweets_obj:
        tweet_dict = {}
        tweet_dict['id'] = tweet.id
        tweet_dict['created'] = tweet.created_at
        tweet_dict['retweeted'] = tweet.retweet_count
        tweet_dict['text'] = tweet.text
        tweet_dict['hashtags'] = tweet.entities['hashtags']
        tweet_dict['urls'] = [url_dict['url'] for url_dict in tweet.entities['urls']]
        tweet_dict['mentions'] = [mention_dict['screen_name'] for mention_dict in tweet.entities['user_mentions']]
        tweet_dict['score'] = SIA.polarity_scores(text=tweet_dict['text'])['compound']
        tweets.append(tweet_dict)
    user_dict['user'] = name
    user_dict['count'] = user_obj.statuses_count
    user_dict['tweets'] = tweets
    return user_dict


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image
    """
    follusr = []
    count = 100
    friends_list = tweepy.Cursor(api.get_friends, id=name).items(count)
    for friend in friends_list:
        f_dict = {}
        f_dict['name'] = friend.name
        f_dict['screen_name'] = friend.screen_name
        f_dict['followers'] = friend.followers_count
        f_dict['created'] = friend.created_at.date()
        f_dict['image'] = friend.profile_image_url_https
        follusr.append(f_dict)
    return follusr