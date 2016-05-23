#!/usr/bin/python

"""
/r/glasgow daily banter thread poster
"""

import re, pyowm, praw, datetime, sys, OAuth2Util, random, traceback
from six.moves import urllib
from bs4 import BeautifulSoup, SoupStrainer
from OAuth2Util import OAuth2Util
import ConfigParser
from time import sleep
from youtube import YouTubeInfo
import urllib2, json, time

def getDayInHistory():
    historyArray = []  
    try:  
        todayInHistoryPage = urllib.request.urlopen('http://www.bbc.co.uk/scotland/history/onthisday/{dt:%B}/{dt.day}'.format(dt=datetime.datetime.now()).lower())
        historySoup = BeautifulSoup(todayInHistoryPage,'html.parser')    
        for vevent_tag in historySoup.find_all("div", {"class" : "story"}):
            contentCheck = re.search('[a-zA-Z]',vevent_tag.text)
            if contentCheck:
                if "recipe" in vevent_tag.text:
                    vevent_tag.next_sibling
                    pass           
                else:
                    historyArray.append(vevent_tag.text), vevent_tag.next_sibling
        if not historyArray:
            historyArray.append("Nothing, apparently!")
        return historyArray
    except:
        historyArray.append("Nothing, apparently!")
        return historyArray

def getMarket(r):
    marketString = ''
    current_time = datetime.datetime.now()
    newposts = r.get_subreddit('GlasgowMarket').get_new()
    posts = {}
    for post in newposts:
        received_time = datetime.datetime.fromtimestamp(int(post.created_utc))
        time_difference = current_time - received_time
        if time_difference < datetime.timedelta(days=7):
            posts[post.permalink] = post.title
    if len(posts)==0:
        marketString = 'No recent posts'
    else:
        for key,value in posts.iteritems():
            marketString = marketString + '['+value+']'+'('+key+')'+'\n\n'
    return marketString

def getSong(r): # Takes the PRAW object
    # Users must have held their account for this number of days to be able to submit suggestions
    how_old = 30
    song_strings = ["youtube.com/","youtu.be/"]
    messages = r.get_unread(unset_has_mail=True,update_user=True)

    current_time = datetime.datetime.now()

    author_list = []
    links_list = []

    for message in messages:
        #message.mark_as_read()
        if message.was_comment: # We don't want to include comment replies, just PMs
            continue
        print message
        received_time = datetime.datetime.fromtimestamp(int(message.created_utc))
        time_difference = current_time - received_time
        if time_difference < datetime.timedelta(days=1):
            if message.author in author_list:
                print "User '"+str(message.author)+"' has already submitted an eligible link for today's post"
            else:
                if not message.author:
                    continue
                sending_user = r.get_redditor(message.author)
                sending_user_join_date = datetime.datetime.fromtimestamp(int(sending_user.created_utc))
                time_difference = current_time - sending_user_join_date
                if time_difference < datetime.timedelta(days=how_old):
                    print "User '"+str(message.author)+"' must be " + str(how_old) + " days old to submit songs"
                    continue
                available_links = re.findall(r'(https?://[^\s]+)', message.body)
                for link in available_links:
                    if any(song_string in link for song_string in song_strings):
                        links_list.append(link)
                        author_list.append(message.author)
                        # Only allow one Youtube link per message - we'll just take the first
                        break

    number_of_songs = len(links_list)
    if number_of_songs==0:
         suffix_string =  "No eligible links submitted today. [Suggest tomorrow's tune](https://www.reddit.com/message/compose/?to=SteamieBot&amp;subject=SongRequest)."
    elif number_of_songs==1:
        suffix_string = "Only one eligible link submitted today. [Suggest tomorrow's tune](https://www.reddit.com/message/compose/?to=SteamieBot&amp;subject=SongRequest)."
    else:
        suffix_string = "Picked from " + str(number_of_songs) + " eligible links submitted today. [Suggest tomorrow's tune](https://www.reddit.com/message/compose/?to=SteamieBot&amp;subject=SongRequest)."

    if number_of_songs==0:
        scottishmusictop = r.get_subreddit('scottishmusic').get_hot(limit=5)
        for submission in scottishmusictop:
            if any(song_string in submission.url for song_string in song_strings):
                links_list.append(submission.url)              
        number = random.randint(0,len(links_list)-1)
        return links_list[number] + " (via /r/ScottishMusic) \n\n" + suffix_string
    else:
        number = random.randint(0,number_of_songs-1)
        print get_title(links_list[number])
        return links_list[number] + " (suggested by /u/" + author_list[number].name + ") \n\n" + suffix_string 

# function to remove duplicate litems from lists.
# stolen from stackoverflow. SHAMELESS.

def get_title(vid):
    if 'youtu.be' in vid:
        id = vid.split('/')
        id = id[-1]
    else:
        id = vid.split('=')
        id = id[-1]
    youtube = YouTubeInfo()
    return youtube.getTitle(id)


def uniq(input):
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output

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


    return uniq(trainStatus)

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

def newWeather(apiKey):
    response = urllib2.urlopen('https://api.forecast.io/forecast/'+apiKey+'/55.8580,-4.2590?units=si')
    html = response.read()
    data = json.loads(html)

    tempMin =  int(data['daily']['data'][0]['temperatureMin'])
    tempMax =  int(data['daily']['data'][0]['temperatureMax'])


    weatherString = '**Weather**\n\n'
    weatherString = weatherString + data['hourly']['summary'] + '\n\n'

    if tempMax==tempMin:
        weatherString = weatherString + "Around " + str(tempMin) + " degrees."
    else:
        weatherString = weatherString + "Around " + str(tempMin) + ' to ' + str(tempMax) + " degrees.\n\n"

    if 'alerts' in data: #len(data['alerts']) != 0:
        weatherString = weatherString + '[**Weather Warning**]('+data['alerts'][-1]['uri']+')\n\n'+ data['alerts'][-1]['description']
    return weatherString

def getWeather(apiKey):

    # Function to return the weather, temperature
    # and wind speed as a list. API allows for more
    # detail if we want to put it in.

    weatherList = []

    owm=pyowm.OWM(API_key=apiKey) # API key for Open Weather Map

    weatherObject = owm.weather_at_place('Glasgow,UK').get_weather() # Putting Scotland instead of UK throws an error. Fucksake.

    # get the details
    temperature = int(weatherObject.get_temperature(unit='celsius')['temp'])
    weatherDetails = weatherObject.get_detailed_status()
    windSpeed = int(weatherObject.get_wind()['speed'])

    # concat them into a string so it'll return a list rather than a tuple
    if temperature > 18:
        tempString = str(temperature) + " degrees: Taps aff!"
    elif temperature > 3:
        tempString = str(temperature) + " degrees"
    elif temperature > 0:
        tempString = "Baltic."
    elif temperature <= 0:
        tempString = "Bloody freezing."

    weatherDetailString = "Weather Details: " + weatherDetails

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

def createPost(r, config):
    title = "The Steamie - {0:%A} {0:%-d} {0:%B} {0:%Y}".format(datetime.date.today())

    #weatherApiKey = config.get('config', 'openweather_api_key')
    forecastApi = config.get('config', 'forecast_api_key')

    #weather = getWeather(weatherApiKey)
    trains = getTrains()
    gigs = getGigInfo()
    tuneString = getSong(r)
    marketString = getMarket(r)
    dayInHistory = getDayInHistory()

    #weatherString = ""
    #for line in weather:
    #    weatherString += line + "\n\n"

    weatherStr = newWeather(forecastApi)

    trainString = ""
    for line in trains:
        trainString += line + "\n\n"

    gigString = ""
    for line in gigs:
        gigString += line + "\n\n"

    historyString = ""
    for line in dayInHistory:
        historyString += line

    body = (#"**Weather**\n\n"
            #+ weatherString + "\n\n"
            weatherStr + "\n\n" +
            "**Travel**\n\n"
            + trainString + "\n\n"
            "**What's On Today**\n\n"
            + gigString + "\n\n"+
            "**Today in Scottish History**\n\n"
            + historyString + "\n\n"+
            "**/r/GlasgowMarket Digest**\n\n"
            +marketString + '\n\n' + 
            "**Tune of the day**\n\n"
            + tuneString)

    return title,body


def postSteamie(configFile):
    config = ConfigParser.ConfigParser()
    config.read(configFile)
    subreddit = config.get('config', 'subreddit')
    linkFlair = config.get('config', 'link_flair')

    r = praw.Reddit("Steamie Poster for /r/glasgow v0.1.0")
    o = OAuth2Util(r)
    o.refresh()

    post = createPost(r, config)

    print post[0] + "\n\n"
    print post[1]

    submission = r.submit(subreddit,post[0],text=post[1])
    submission.sticky()
    r.select_flair(submission, flair_template_id=linkFlair)

def tryPost(configFile):
    attempt_start = datetime.datetime.now()
    success = False
    while (datetime.datetime.now()-attempt_start) < datetime.timedelta(hours=2):
        try:
            print("Attempting to post 'The Steamie'")
            postSteamie(configFile)
            success = True
            break
        except Exception, err:
            print("Failed to make daily post. Waiting 15 minutes to retry. Error: ")
            traceback.print_exc()
            sleep(15*60) #Sleep in seconds
