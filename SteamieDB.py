import sqlite3
import praw
import re
import datetime
from OAuth2Util import OAuth2Util
from youtube import YouTubeInfo
import hashlib
import pickle
import random
import time

class SteamieDB(object):

    def __init__(self):
        self.db = 'steamie.db'
        self.schema = 'schema.sql'
        self.conn = sqlite3.connect(self.db)
        f = open(self.schema, 'r')
        schema = f.read()
        f.close()
        self.c = self.conn.cursor()
        self.c.executescript(schema)
        self.conn.commit()

    def test(self):
        self.c.execute('SELECT * from submitted')
        output =  self.c.fetchall()
        for out in output:
            print out
        self.c.execute('SELECT * from ineligible')
        output =  self.c.fetchall()
        for out in output:
            print out

        print "CHOSEN"
        self.c.execute('SELECT * from chosen')
        output =  self.c.fetchall()
        for out in output:
            print out

    def close(self):
        self.conn.commit()
        self.conn.close()

    def checkDB(self,hash):
        self.c.execute('SELECT * from submitted where UID=?',(hash,))
        output  = self.c.fetchall()
        return len(output) is 0

    def getIDfromUID(self,hash):
        self.c.execute('SELECT submitted_id from submitted where UID=?',(hash,))
        output  = self.c.fetchall()
        return output[0][0]

    def getIDfromURL(self,url):
        self.c.execute('SELECT submitted_id from submitted where url=?',(url,))
        output = self.c.fetchone()
        print url + str(output)
        if output is not None:
            return output[0]
        else:
            return -1

    def getUsersDailyPosts(self,user): # Is user ineligible
        now = datetime.datetime.now()
        lastpost = datetime.datetime.combine(datetime.date.today(), datetime.time.min) + datetime.timedelta(hours=5)
        if lastpost > now: # Lastpost is in the future. This will happen when the script runs between midnight and 5am
            lastpost = lastpost - datetime.timedelta(days=1)
        retval = False
        self.c.execute('SELECT whensub from submitted where username=?',(user,))
        output = self.c.fetchall()
        if len(output) is not 1: # User has only ever submitted one post. Definitely not two in a day
            count = 0
            for line in output:
                date = line[0]
                received_time = datetime.datetime.fromtimestamp(int(date))
                if received_time > lastpost: # We've received a message from this user after the most recent post
                    count = count+1
                    if count > 1:
                        retval = True # User can't submit another tune today
        return retval

    def getSong(self):
        self.c.execute('SELECT submitted_id, whensub from submitted')
        # Get ids we can use
        ids = []
        time_cutoff = datetime.datetime.now() - datetime.timedelta(days=1)
        output = self.c.fetchall()
        for out in output:
            received_time = datetime.datetime.fromtimestamp(int(out[1]))
            if received_time > time_cutoff:
                ids.append(out[0])
        selected = False
        while not selected:
            number_of_songs = len(ids)
            number = random.randint(0,number_of_songs-1)
            if self.isIneligbile(ids[number]):
                ids.remove(number)
            else:
                selected = True
            print ids[number]
        selected = (ids[number],)
        self.c.execute('SELECT * from submitted where submitted_id=?',selected)
        return self.c.fetchone()

    def isIneligbile(self,id):
        self.c.execute('SELECT * from ineligible where submitted_id=?',(id,))
        output = self.c.fetchall()
        if len(output) is not 0:
            return True
        else:
            return False

class RedditDB(object):

    def __init__(self):
        self.r = praw.Reddit("Steamie Poster for /r/glasgow v0.1.0")
        self.youtube = YouTubeInfo()
        o = OAuth2Util(self.r)
        o.refresh()

        self.how_old = 30
        self.post_time = 5 # AM. We need this to seperate days for users

    def addVideo(self,vid):
        self.youtube.add_video_to_playlist(vid,'PLwNSRYv3TVjlSlEGV6rq7E643I2m4Xnfx')

    def get_title(self,id):
        #return "Test"
        return self.youtube.getTitle(id)

    def populateDB(self,db):
        # Insert the default song
        default_id = 'dQw4w9WgXcQ'
        title = self.get_title('dQw4w9WgXcQ')
        values = (title,default_id,0,'steamiebot')
        text = pickle.dumps(values)
        hash = hashlib.md5(text).hexdigest()
        if db.checkDB(hash):
            db_input = values + (hash,)
            db.c.execute('INSERT into submitted VALUES (null,?,?,?,?,?)',db_input)
            db.conn.commit()

        message_gen = self.r.get_messages(limit=None)
        pattern = re.compile("(?:http[s]?://www\.youtube\.com/watch\?v=|http://youtu.be/)([0-9A-Za-z\-_]*)")
        for message in message_gen:
            ids = list(pattern.findall(message.body))
            if len(ids) is 0: # No Youtube links in this message
                continue
            for vid_id in ids:
                title = self.get_title(vid_id)
                received_time = int(message.created_utc)
                values = (title,vid_id,received_time,str(message.author))
                text = pickle.dumps(values)
                hash = hashlib.md5(text).hexdigest()
                if db.checkDB(hash):
                    db_input = values + (hash,)
                    db.c.execute('INSERT into submitted VALUES (null,?,?,?,?,?)',db_input)
                    db.conn.commit()

    def populateSubmitted(self,db):
        pattern = re.compile("(?:youtube\.com/watch\?v=|youtu.be/)([0-9A-Za-z\-_]*)")
        posts_gen = self.r.get_me().get_submitted(limit=None)
        for posts in posts_gen:
            subreddit = str(posts.subreddit)
            if str(posts.subreddit) != 'glasgow':
                continue
            body = posts.selftext
            ids = list(pattern.findall(body))
            if len(ids) is 0: # No Youtube links in this message
                continue
            for vid_id in ids:
                #ID = db.getIDfromURL(vid_id)
                ID = -1
                date = int(posts.created_utc)
                db.c.execute('INSERT into chosen VALUES (null,?,?,?)',(date,vid_id,ID))
                db.conn.commit()
                try:
                    reddit.addVideo(vid_id)
                    time.sleep(1)
                except:
                    time.sleep(5)
                    continue

    def getMessages(self,db):
        message_gen =  self.r.get_messages(limit=None)
        for message in message_gen:
            print message
        return
        pattern = re.compile("(?:http[s]?://www\.youtube\.com/watch\?v=|http://youtu.be/)([0-9A-Za-z\-_]*)")
        current_time = datetime.datetime.now()
        messages = self.r.get_unread(unset_has_mail=True,update_user=True)
        for message in messages:
            if message.was_comment: # We don't want to include comment replies, just PMs
                continue
            ids = list(pattern.findall(message.body))
            if len(ids) is 0: # No Youtube links in this message
                continue
            for vid_id in ids:
                title = self.get_title(vid_id)
                #received_time = datetime.datetime.fromtimestamp(int(message.created_utc))
                received_time = int(message.created_utc)
                values = (title,vid_id,received_time,str(message.author))
                text = pickle.dumps(values)
                hash = hashlib.md5(text).hexdigest()
                if db.checkDB(hash):
                    db_input = values + (hash,)
                    db.c.execute('INSERT into submitted VALUES (null,?,?,?,?,?)',db_input)

                    # Check to see if the user is eligible for a submission today
                    sending_user = self.r.get_redditor(message.author)
                    sending_user_join_date = datetime.datetime.fromtimestamp(int(sending_user.created_utc))
                    time_difference = current_time - sending_user_join_date
                    if time_difference < datetime.timedelta(days=self.how_old): # If the user is less than 30 days old, they're not eligible for a submission
                        # We need to get the ID of the submission above to link it to the database
                        submission_id = db.getIDfromUID(hash)
                        db_input = ('User is not 30 days old',submission_id)
                        db.c.execute('INSERT into ineligible VALUES (null,?,?)',db_input)
                    print str(message.author) + str(db.getUsersDailyPosts(str(message.author)))
                    if db.getUsersDailyPosts(str(message.author)):
                        submission_id = db.getIDfromUID(hash)
                        db_input = ('User has submitted a post today',submission_id)
                        db.c.execute('INSERT into ineligible VALUES (null,?,?)',db_input)

                    db.conn.commit()
                else:
                    print "Log: Data already in database"




if __name__ == "__main__":
    db = SteamieDB()
    reddit = RedditDB()

    #sqreddit.populateDB(db)
    reddit.populateSubmitted(db)
    #reddit.getMessages(db)
    #db.getSong()
    #db.test()
    db.close()

