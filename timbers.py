# !/usr/bin/python
import praw
import os
import re
import redis
from textblob import TextBlob
import sys
import psycopg2
import config
from config import *
import datetime

# Login to reddit object
reddit = praw.Reddit(client_id=config.client_id, client_secret=config.client_secret, password=config.password, user_agent=config.user_agent, username=config.username)
redis = redis.StrictRedis(host='localhost', port=6379, db=0)
submission = reddit.submission(url=sys.argv[1])

# Iterate through the comments, perform sentiment analysis.

comments = []


submission.comments.replace_more(limit=0)
for top_level_comment in submission.comments:
    try:
        comments.append(str(top_level_comment.body.lower()))
    except:
        pass
    for second_level_comment in top_level_comment.replies:
        try:
            comments.append(str(second_level_comment.body.lower()))
        except:
            pass

comments = ' '.join(comments)
commentSentiment = (TextBlob(comments)).sentiment.polarity

# Input loop to supply goal info.

scorers = []
scoreFlag = False

while True:
    if scoreFlag == False:
        print "Enter the goal scorers in chronological order. Enter 'end' when finished. "
        scoreFlag = True
    data = raw_input()
    if not data == "end":
        scorers.append(data)
        continue
    else:
        break

minutes = []
minuteFlag = False

while True:
    if minuteFlag == False:
        print "Enter the minutes in which the goals were scored in chronological order. Enter 'end' when finished. "
        minuteFlag = True
    data = raw_input()
    if not data == "end":
        minutes.append(data)
        continue
    else:
        break

opponent = raw_input("Enter the opponent. ")
result = raw_input("Enter the result. ")

# Collect date of post.

def get_date(submission):
    time = submission.created
    return datetime.datetime.fromtimestamp(time).date()

date = get_date(submission)

try:
    conn = psycopg2.connect(config.conn_string)
    print('Successfully connected to database...')
except:
    print('Connection to database failed. Check configuration settings.')

cur = conn.cursor()
cur.execute("""INSERT INTO timbers (date, opponent, result, sentiment, scorers, minutes ) VALUES (%s, %s , %s, %s, %s, %s)""", (date, opponent, result, commentSentiment, scorers, minutes))

conn.commit()
cur.close()
conn.close()
print("Data import complete.")

