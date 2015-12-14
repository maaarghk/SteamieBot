#!/usr/bin/python

"""
/r/glasgow daily banter thread poster
"""

import re, pyowm, praw, datetime, sys, OAuth2Util, random
from six.moves import urllib
from bs4 import BeautifulSoup, SoupStrainer
from OAuth2Util import OAuth2Util;
import ConfigParser;

if len(sys.argv) > 1:
    configFile = sys.argv[1]
else:
    configFile = "steamiebot.ini"

config = ConfigParser.ConfigParser()
config.read(configFile)
subreddit = config.get('config', 'subreddit')
linkFlair = config.get('config', 'link_flair')

r = praw.Reddit("Steamie Poster for /r/glasgow v0.1.0")
o = OAuth2Util(r)
o.refresh()

def getSong(r): # Takes the PRAW object
    # Users must have held their account for this number of days to be able to submit suggestions
    how_old = 30

    messages = r.get_unread(unset_has_mail=True,update_user=True)

    current_time = datetime.datetime.now()

    author_list = []
    links_list = []

    for message in messages:
        print message
        received_time = datetime.datetime.fromtimestamp(int(message.created_utc))
        time_difference = current_time - received_time
        if time_difference < datetime.timedelta(days=1):
            if message.author in author_list:
                print "User '"+str(message.author)+"' has already submitted an eligible link for today's post"
            else:
                sending_user = r.get_redditor(message.author)
                sending_user_join_date = datetime.datetime.fromtimestamp(int(sending_user.created_utc))
                time_difference = current_time - sending_user_join_date
                if time_difference < datetime.timedelta(days=how_old):
                    print "User '"+str(message.author)+"' must be",how_old, "days old to submit songs"
                    continue
                available_links = re.findall(r'(https?://[^\s]+)', message.body)
                author_list.append(message.author)
                for link in available_links:
                    if "youtube.com/" in link:
                        links_list.append(link)
                        author_list.append(message.author)
                        # Only allow one Youtube link per message - we'll just take the first
                        break

    number_of_songs = len(links_list)
    if number_of_songs==0:
        return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    else:
        number = random.randint(0,number_of_songs-1)
        return links_list[number]

def getTrains():

    # Function to find line updates from Scotrail
    # Via JourneyCheck and return as a list.

    trainStatus = []
    onlyupdates = SoupStrainer(attrs = {"id" : "lu_update_body"})

    glcPage = urllib.request.urlopen('http://www.journeycheck.com/scotrail/route?from=&to=GLC&action=search&savedRoute=')
    glqPage = urllib.request.urlopen('http://www.journeycheck.com/scotrail/route?from=&to=GLQ&action=search&savedRoute=')

    glcSoup = BeautifulSoup(glcPage,'html.parser')
    glqSoup = BeautifulSoup(glqPage,'html.parser')

    # the following finds if the Line Updates section contains a number greater than 0.
    # if it does, it goes on to return the info line by line in a list.

    lineUpdatesGlc = glcSoup.find_all(id="headingTextLU")
    lineUpdatesGlq = glqSoup.find_all(id="headingTextLU")


    if (int(filter(str.isdigit,str(lineUpdatesGlc[0])))) + (int(filter(str.isdigit,str(lineUpdatesGlq[0])))) == 0:
        print '0'
        trainStatus.append("No line problems reported.")
    else:
        glcPage = urllib.request.urlopen('http://www.journeycheck.com/scotrail/route?from=&to=GLC&action=search&savedRoute=')
        glqPage = urllib.request.urlopen('http://www.journeycheck.com/scotrail/route?from=&to=GLQ&action=search&savedRoute=')

        glcText = BeautifulSoup(glcPage,'html.parser',parse_only=onlyupdates).get_text()
        glqText = BeautifulSoup(glqPage,'html.parser',parse_only=onlyupdates).get_text()
        combinedTrains = glcText + glqText

        # Take out the stuff we don't want to see (whitespace, code & non-relevant stuff)

        for line in combinedTrains.splitlines():
            contentCheck = re.search('[a-zA-Z]',line)

            if contentCheck:
                if "');" in line:
                    pass
                elif "delay-repay" in line:
                    pass
                elif "Additional Information" in line:
                    pass
                elif "currently no Line" in line:
                    pass
                elif "Impact" in line:
                    pass

                else:
                    stripline = line.strip()
                    trainStatus.append(stripline)
            else:
                pass


    return trainStatus

def getGigInfo():

    # Function to return all the day's gig titles and
    # locations from the List website as a list.

    gigList = []

    # Get the webpage and parse it with BeautifulSoup
    gigPage = urllib.request.urlopen('https://www.list.co.uk/events/music/when:tonight/location:Glasgow(55.8621,-4.2465)/distance:5/')
    gigSoup = BeautifulSoup(gigPage,'html.parser')
    titleSet = gigSoup.find_all('h3') # finds the relevant titles
    for title in titleSet:
        titleString = re.search('(?<=title=")(.*)(?=">)',str(title)) # regex to isolate the sentence
        if titleString:
            gigInfo = titleString.group(1)
            gigList.append(unicode(gigInfo,'utf-8'))
    return gigList

def getWeather():

    # Function to return the weather, temperature
    # and wind speed as a list. API allows for more
    # detail if we want to put it in.

    weatherList = []

    owm=pyowm.OWM(API_key='2e55f450fa37e779a4172bffbaac75a5') # API key for Open Weather Map

    weatherObject = owm.weather_at_place('Glasgow,UK').get_weather() # Putting Scotland instead of UK throws an error. Fucksake.

    # get the details
    temperature = weatherObject.get_temperature(unit='celsius')['temp']
    weatherDetails = weatherObject.get_detailed_status()
    windSpeed = weatherObject.get_wind()['speed']

    # concat them into a string so it'll return a list rather than a tuple
    if temperature > 18:
        tempString = temperature + " degrees: Taps aff!"
    elif temperature > 3:
        tempString = "Temperature: "+str(temperature)+" degrees"
    elif temperature > 0:
        tempString = "Baltic."
    elif temperature < 0:
        tempString = "Bloody freezing."

    weatherDetailString = "Weather Details: "+weatherDetails

    weatherList.append(weatherDetailString)
    weatherList.append("Temperature: " + tempString)

    # Fairly obvious what this does :) could add stuff
    # like this for other temp/weather events
    if windSpeed > 20:
        weatherList.append("Blowy as fuck")
    if windSpeed < 20:
        weatherListString = "Wind: " + str(windSpeed) + " mph"
        weatherList.append(weatherListString)

    return weatherList

def createPost(r):
    title = "The Steamie - {0:%A} {0:%-d} {0:%B} {0:%Y}".format(datetime.date.today())

    weather = getWeather()
    trains = getTrains()
    gigs = getGigInfo()
    tuneString = getSong(r)

    weatherString = ""
    for line in weather:
        weatherString += line + "\n\n"

    trainString = ""
    for line in trains:
        trainString += line + "\n\n"

    gigString = ""
    for line in gigs:
        gigString += line + "\n\n"

    body = ("**Weather**\n\n"
            + weatherString + "\n\n"
            "**Travel**\n\n"
            + trainString + "\n\n"
            "**What's On Today**\n\n"
            + gigString + "\n\n"
            "**Tune of the day**\n\n"
            + tuneString
            + "[Suggest tomorrow's tune](https://www.reddit.com/message/compose/?to=SteamieBot&amp;subject=SongRequest)")

    return title,body

post = createPost(r)

print post[0] + "\n\n"
print post[1]

submission = r.submit(subreddit,post[0],text=post[1])
r.select_flair(submission, flair_template_id=linkFlair)
