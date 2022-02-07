"""
A web server that responds with two pages, one showing the most recent
100 tweets for given user and the other showing the people that follow
that given user, which sorted by the number of followers those users have.

For authentication purposes, the server takes a commandline argument
that indicates the file containing Twitter data in a CSV file format:
[consumer_key, consumer_secret, access_token, access_token_secret]
"""
import sys
from flask import Flask, render_template
from tweetie import *
from colour import Color
from numpy import median


app = Flask(__name__)


def add_color(tweets):
    """
    Given a list of tweets, one dictionary per tweet, add
    a "color" key to each tweets dictionary with a value
    containing a color graded from red to green [-1, 1].
    """
    colors = list(Color("red").range_to(Color("green"), 100))
    n = len(colors) - 1
    senti_score = []
    for t in tweets:
        score = t['score']
        senti_score.append(score)
        c_idx = int((score + 1) * n / 2)
        t['color'] = colors[c_idx]
    return senti_score


@app.route("/favicon.ico")
def favicon():
    """
    Open and return a 16x16 or 32x32 .png or other image file in binary mode.
    This is the icon shown in the browser tab next to the title.
    """
    with open('image.ico', 'rb') as f:
        ico = f.read()
    return ico


@app.route("/<name>")
def tweets(name):
    """
    Display the tweets for a screen name color-coded by sentiment score
    """
    user_info = fetch_tweets(api, name)
    senti_score = add_color(user_info['tweets'])
    user_info['medi_score'] = median(senti_score)
    return render_template('tweets.html', results=user_info)


@app.route("/following/<name>")
def following(name):
    """
    Display the list of users followed by a screen name, sorted in
    reverse order by the number of followers of those users.
    """
    follow_guy = fetch_following(api, name)
    follow_guy.sort(key=lambda x: x['followers'], reverse=True)
    return render_template('following.html', results=follow_guy, name=name)


if __name__ == '__main__':
    i = sys.argv.index('server:app')
    twitter_auth_filename = sys.argv[i+1]
    api = authenticate(twitter_auth_filename)

# gunicorn -D --threads 1 -b 0.0.0.0:5000 --access-logfile server.log --timeout 60 server:app tweepy_key.csv
# gunicorn --threads 1 -b 0.0.0.0:5000 --access-logfile server.log --timeout 60 server:app tweepy_key.csv
# ps aux | grep gunicorn
# kill -9 9042