import unittest
import praw
import httplib
import re
import json
from itertools import groupby
import os

if os.path.exists('settings.py'):
  import settings
  def GetPraw():
    return praw.Reddit(client_id = settings.client_id,
                       client_secret = settings.client_secret,
                       username = settings.reddituser,
                       password = settings.redditpass,
                       user_agent = 'r/starcraft event tracker script')

def getLiquipediaEventsJson(game):
  conn = httplib.HTTPConnection('liquipedia.net')
  conn.connect()
  request = conn.putrequest('GET','/' + game + '/api.php?format=json&action=query&titles=Liquipedia:Tournaments&prop=revisions&rvprop=content')
  conn.endheaders()
  conn.send('')
  return conn.getresponse().read()

def liquipediaEventsJsonIntoSource(data):
  jsonData = json.loads(data)
  return jsonData['query']['pages'].values()[0]['revisions'][0]['*']

def isJsonSectionLine(str):
  return re.match("^\*[^*].*", str) != None

def splitByJsonSection(lines):
  sections = []
  section = []
  for line in lines:
    if isJsonSectionLine(line):
      sections.append(section)
      section = []
    section.append(line)
  sections.append(section)
  return sections

def jsonEventToDict(event):
  matches = re.match("\*\*([^\|]+)\|([^\|]+)\| *startdate=([^\|]+)\| *enddate=([^\|]+)", event)
  if matches != None:
    eventLink = matches.group(1).strip().replace(" ", "_")
    eventName = eventNameReplacements(matches.group(2).strip())
    eventStart = matches.group(3).strip()
    eventEnd = matches.group(4).strip()
    return dict(name= eventName, link = "http://liquipedia.net/starcraft2/" + eventLink, start = eventStart, end = eventEnd)
  matches = re.match("\*\*([^\|]+)\|([^\|]+)\| *startdate=([^\|]+)", event)
  if matches != None:
    eventLink = matches.group(1).strip().replace(" ", "_")
    eventName = eventNameReplacements(matches.group(2).strip())
    eventStart = matches.group(3).strip()
    eventEnd = eventStart
    return dict(name= eventName, link = "http://liquipedia.net/starcraft2/" + eventLink, start = eventStart, end = eventEnd)
  raise ValueError('event line is malformed')


def formatJsonSection(section):
  sectionHeader = section[0][1:]
  dicts = map(jsonEventToDict, section[1:])
  filteredDicts = filter(filterEvents, dicts)
  formatted = map(formatEventRow, filteredDicts)
  return formatSectionRow(sectionHeader) + "".join(formatted)

def liquipediaEventsJsonToSidebar(data):
  src = liquipediaEventsJsonIntoSource(data)
  lines = liquipediaEventsIntoLines(src)
  split = splitByJsonSection(lines)
  formattedSections = map(formatJsonSection, split[1:])
  return formatTableHeader() + "".join(formattedSections)

def eventNameReplacements(eventName):
  newName = eventName
  newName = re.sub("[Ss]eason ([0-9])", "S\\1", newName)
  newName = re.sub("[Gg]lobal [Ss]tarCraft (II )?[Ll]eague", "GSL", newName)
  return newName

def filterEvents(event):
  eventName = event['name']
  eventLink = event['link']
  return re.match(".*[Qq]ualifier", eventName) == None and re.match(".*[Qq]ualifier.*", eventLink) == None

def liquipediaEventsIntoLines(events):
  return events.split('\n')

def formatEventRow(event):
  return u"|[{0}]({1}) | {2} | {3} |\n".format(event['name'], event['link'], event['start'], event['end'])

def formatSectionRow(sectionName):
  return "| **{0}**| | |\n".format(sectionName)

def formatTableHeader():
  return "| |Starts |Ends |\n|:-----------|:------------|:------------|\n"

def formatWikiHeader():
  return "#Starcraft Event List\nUpdated by /u/Automaton2000    \nSourced from [Liquipedia](http://wiki.teamliquid.net/starcraft2/Main_Page)\n\n"

def liquipediaStringToWiki(game, lines):
  output = formatWikiHeader()
  output += lines
  return output

def getCurrentLiquipediaEventsForWiki(game):
  wiki = liquipediaStringToWiki(game, liquipediaEventsJsonToSidebar(getLiquipediaEventsJson('starcraft2')))
  return wiki

def setWikiPage(prawLogin, subredditName, wikiPageName, game):
  subreddit = prawLogin.subreddit(subredditName)
  newContent = getCurrentLiquipediaEventsForWiki(game)
  subreddit.wiki[wikiPageName].edit(newContent, 'beep boop - backing up event data')
