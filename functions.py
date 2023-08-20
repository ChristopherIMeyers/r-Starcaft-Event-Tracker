import praw
import re
import json
from itertools import groupby
import os
from io import StringIO
import gzip
import requests

subredditName = 'starcraft'

if os.path.exists('settings.py'):
  import settings
  def GetPraw():
    return praw.Reddit(client_id = settings.client_id,
                       client_secret = settings.client_secret,
                       username = settings.reddituser,
                       password = settings.redditpass,
                       user_agent = 'r/starcraft event tracker script')

def getLiquipediaEventsJson(game):
  request = requests.get('https://liquipedia.net/' + game + '/api.php?format=json&action=query&titles=Liquipedia:Tournaments&prop=revisions&rvprop=content',
                         headers={'User-Agent': 'reddit.com/r/starcraft event list bot'})
  return request.text

def liquipediaEventsJsonIntoSource(data):
  jsonData = json.loads(data)
  return list(jsonData['query']['pages'].values())[0]['revisions'][0]['*']

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
  matches = re.match("\*\*(?P<link>[^\|]+)\|(?P<name>[^\|]+)\|( *icon[a-z]*=[^\|]+\|)* *startdate=(?P<startdate>[^\|]+)\| *enddate=(?P<enddate>[^\|]+)", event)
  if matches != None:
    eventLink = matches.group('link').strip().replace(" ", "_")
    eventName = eventNameReplacements(matches.group('name').strip())
    eventStart = dateReplacements(matches.group('startdate').strip())
    eventEnd = dateReplacements(matches.group('enddate').strip())
    return dict(name= eventName, link = eventLink, start = eventStart, end = eventEnd)
  matches = re.match("\*\*(?P<link>[^\|]+)\|(?P<name>[^\|]+)\|( *icon[a-z]*=[^\|]+\|)* *startdate=(?P<startdate>[^\|]+)", event)
  if matches != None:
    eventLink = matches.group('link').strip().replace(" ", "_")
    eventName = eventNameReplacements(matches.group('name').strip())
    eventStart = dateReplacements(matches.group('startdate').strip())
    eventEnd = dateReplacements(eventStart)
    return dict(name= eventName, link = eventLink, start = eventStart, end = eventEnd)
  raise ValueError('event line is malformed' + event)


def formatJsonSection(section):
  sc1 = section[0]
  sc2 = section[1]

  sectionHeader = sc1[0][1:]

  dicts1 = list(map(jsonEventToDict, sc1[1:]))
  filteredDicts1 = list(filter(filterEvents, dicts1))
  formatted1 = list(map(formatEventRow('starcraft'), filteredDicts1))

  dicts2 = list(map(jsonEventToDict, sc2[1:]))
  filteredDicts2 = list(filter(filterEvents, dicts2))
  formatted2 = list(map(formatEventRow('starcraft2'), filteredDicts2))

  formattedBoth = formatted1 + formatted2

  return formatSectionRow(sectionHeader) + "".join(formattedBoth)

def liquipediaEventsJsonToZippedData(data1, data2):
  src1 = liquipediaEventsJsonIntoSource(data1)
  lines1 = liquipediaEventsIntoLines(src1)
  split1 = splitByJsonSection(lines1)

  src2 = liquipediaEventsJsonIntoSource(data2)
  lines2 = liquipediaEventsIntoLines(src2)
  split2 = splitByJsonSection(lines2)

  return list(zip(split1[1:], split2[1:]))

def liquipediaEventsJsonToSidebar(data1, data2):
  zipped = liquipediaEventsJsonToZippedData(data1, data2)
  formattedSections = list(map(formatJsonSection, zipped))
  return formatTableHeader() + "".join(formattedSections)

def liquipediaEventsJsonToNewSidebar(data1, data2):
  def prependTableHaders(section):
    return formatNewTableHeader() + section + '\n'

  zipped = liquipediaEventsJsonToZippedData(data1, data2)
  formattedSections = list(map(formatJsonSection, zipped))
  sectionsWithHeaders = list(map(prependTableHaders, formattedSections))
  return "".join(sectionsWithHeaders)

def eventNameReplacements(eventName):
  newName = eventName
  newName = re.sub("[Ss]eason ([0-9])", "S\\1", newName)
  newName = re.sub("[Gg]lobal [Ss]tarCraft (II )?[Ll]eague", "GSL", newName)
  return newName

def dateReplacements(dateString):
  newName = dateString
  newName = re.sub(" ", "&nbsp;", newName)
  return newName

def filterEvents(event):
  eventName = event['name']
  eventLink = event['link']
  return re.match(".*[Qq]ualifier", eventName) == None and re.match(".*[Qq]ualifier.*", eventLink) == None

def liquipediaEventsIntoLines(events):
  lines = events.split('\n')
  def f(x): return x != ''
  return list(filter(f, lines))

def formatEventRow(game):
  def formatEventRowInner(event):
    return "|[{0}](http://liquipedia.net/{1}/{2}) | {3} | {4} |\n".format(event['name'], game, event['link'], event['start'], event['end'])
  return formatEventRowInner

def formatSectionRow(sectionName):
  return "| **{0}**| | |\n".format(sectionName)

def formatTableHeader():
  return "| |Starts |Ends |\n|:-----------|:------------|:------------|\n"

def formatNewTableHeader():
  return "| | | |\n|:-----------|:------------|:------------|\n"

def getCurrentLiquipediaEventsForWiki():
  wiki = liquipediaEventsJsonToSidebar(getLiquipediaEventsJson('starcraft'), getLiquipediaEventsJson('starcraft2'))
  return wiki

def replaceNewEventTable(oldContent, newTable):
  oldContentNoReturns = re.sub("\r", "", oldContent)
  newContent = re.sub("(\| \|Starts \|Ends \|\n\|[^\n]+\n)(\|[^\n]+\n)*", newTable, oldContentNoReturns)
  return newContent

def getCurrentLiquipediaEventsForNewWiki():
  wiki = liquipediaEventsJsonToNewSidebar(getLiquipediaEventsJson('starcraft'), getLiquipediaEventsJson('starcraft2'))
  return wiki + '[^source: ^liquipedia](https://liquipedia.net/starcraft2/Main_Page) ^under ^[CC-BY-SA](https://liquipedia.net/starcraft2/Liquipedia:Copyrights)'

def getEventListWidget(subreddit):
  for widget in subreddit.widgets.sidebar:
    if isinstance(widget, praw.models.TextArea):
      if widget.shortName == 'Event List':
        return widget
  raise ValueError('Event List widget not found')


def setWikiPage(prawLogin):
  wikiPageName = 'eventlist'
  subreddit = prawLogin.subreddit(subredditName)
  newContent = getCurrentLiquipediaEventsForWiki()
  subreddit.wiki[wikiPageName].edit(newContent, 'beep boop - backing up event data')

def setNewWikiPage(prawLogin):
  wikiPageName = 'eventlistnew'
  subreddit = prawLogin.subreddit(subredditName)
  newContent = getCurrentLiquipediaEventsForNewWiki()
  subreddit.wiki[wikiPageName].edit(newContent, 'beep boop - backing up event data')

def updateSidebar(prawLogin):
  wikiPageName = "config/sidebar"
  subreddit = prawLogin.subreddit(subredditName)
  newTable = getCurrentLiquipediaEventsForWiki()
  oldContent = subreddit.wiki[wikiPageName].content_md
  newContent = replaceNewEventTable(oldContent, newTable)
  subreddit.wiki[wikiPageName].edit(newContent, 'beep boop - updating event data')

def updateWidget(prawLogin):
  newContent = getCurrentLiquipediaEventsForNewWiki()
  subreddit = prawLogin.subreddit(subredditName)
  widget = getEventListWidget(subreddit)
  widget.mod.update(text = newContent)
