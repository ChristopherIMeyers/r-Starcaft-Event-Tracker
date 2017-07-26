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

def getLiquipediaEventsJson():
  conn = httplib.HTTPConnection('wiki.teamliquid.net')
  conn.connect()
  request = conn.putrequest('GET','/starcraft2/api.php?format=json&action=query&titles=Liquipedia:Tournaments&prop=revisions&rvprop=content')
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
  eventLink = matches.group(1).strip().replace(" ", "_")
  eventName = eventNameReplacements(matches.group(2).strip())
  eventStart = matches.group(3).strip()
  eventEnd = matches.group(4).strip()
  return dict(name= eventName, link = "http://wiki.teamliquid.net/starcraft2/" + eventLink, start = eventStart, end = eventEnd)

def formatJsonSection(section):
  sectionHeader = section[0][1:]
  dicts = map(jsonEventToDict, section[1:])
  formatted = map(formatEventRow, dicts)
  return formatSectionRow(sectionHeader) + "".join(formatted)

def liquipediaEventsJsonToSidebar(data):
  src = liquipediaEventsJsonIntoSource(data)
  lines = liquipediaEventsIntoLines(src)
  split = splitByJsonSection(lines)
  formattedSections = map(formatJsonSection, split[1:])
  return formatTableHeader() + "".join(formattedSections)

def eventNameReplacements(eventName):
  return re.sub("[Ss]eason ([0-9])", "S\\1", eventName)







def getLiquipediaEvents(game):
  conn = httplib.HTTPConnection('wiki.teamliquid.net')
  conn.connect()
  request = conn.putrequest('GET','/' + game + '/api.php?format=txt&action=query&titles=Liquipedia:Tournament_News&prop=revisions&rvprop=content')
  conn.endheaders()
  conn.send('')
  return conn.getresponse().read()

def cleanLiquipediaEvents(events):
  strippedNoInclude = re.sub(r"<noinclude>.*?</noinclude>", "", events, flags=re.DOTALL)
  strippedHtml = re.sub(r"<!--.*?-->", r'', strippedNoInclude, flags=re.DOTALL)
  return strippedHtml

def liquipediaEventsIntoLines(events):
  return events.split('\n')

def isEventLine(str):
  return re.match("{{(TNL|TournamentNewsLine)\|link=\[\[.*}}", str) != None

def convertEventLineToEventDict(game, eventLine):
  matches = re.match("{{(?:TNL|TournamentNewsLine)\|link=\[\[(.*)\|(.*)\]\].*sdate=(.*)\|edate=(.*)}}", eventLine)
  if matches != None:
    eventName = matches.group(2)
    eventLink = matches.group(1).replace(" ", "_")
    eventStart = matches.group(3)
    eventEnd = matches.group(4)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/" + game + "/"+eventLink, start = eventStart, end = eventEnd)
  matches = re.match("{{(?:TNL|TournamentNewsLine)\|link=\[\[(.*)\]\].*sdate=(.*)\|edate=(.*)}}", eventLine)

  if matches != None:
    eventName = matches.group(1)
    eventLink = matches.group(1).replace(" ", "_")
    eventStart = matches.group(2)
    eventEnd = matches.group(3)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/" + game + "/"+eventLink, start = eventStart, end = eventEnd)

  matches = re.match("{{(?:TNL|TournamentNewsLine)\|link=\[\[(.*)\|(.*)\]\].*date=(.*)}}", eventLine)
  if matches != None:
    eventName = matches.group(2)
    eventLink = matches.group(1).replace(" ", "_")
    eventStart = matches.group(3)
    eventEnd = matches.group(3)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/" + game + "/"+eventLink, start = eventStart, end = eventEnd)

  matches = re.match("{{(?:TNL|TournamentNewsLine)\|link=\[\[(.*)\]\].*date=(.*)}}", eventLine)
  if matches != None:
    eventName = matches.group(1)
    eventLink = matches.group(1).replace(" ", "_")
    eventStart = matches.group(2)
    eventEnd = matches.group(2)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/" + game + "/"+eventLink, start = eventStart, end = eventEnd)
  return None

def isSectionLine(str):
  return re.match(".*box_header tnl-header.*", str) != None

def getSectionName(str):
  return re.match(".*box_header tnl-header.*>([A-Z]+)", str).group(1)

def splitBySection(lines):
  sections = []
  section = []
  for line in lines:
    if isSectionLine(line):
      sections.append(section)
      section = []
    section.append(line)
  sections.append(section)
  return sections

def formatEventRow(event):
  return u"|[{0}]({1}) | {2} | {3} |\n".format(event['name'], event['link'], event['start'], event['end'])

def formatSectionRow(sectionName):
  return "| **{0}**| | |\n".format(sectionName)

def formatTableHeader():
  return "| |Starts |Ends |\n|:-----------|:------------|:------------|\n"

def formatWikiHeader():
  return "#Starcraft Event List\nUpdated by /u/Automaton2000    \nSourced from [Liquipedia](http://wiki.teamliquid.net/starcraft2/Main_Page)\n\n"

def formatSection(sectionName, sectionData):
  output = formatSectionRow(sectionName)
  if sectionData == []:
    return output
  return output + "".join(sectionData)

def linesToEventStrings(game, lines):
  curriedEventLineToEventDict = lambda x:convertEventLineToEventDict(game, x)
  sections = splitBySection(lines)
  eventLines = (filter(isEventLine, sections[1]), filter(isEventLine, sections[2]), filter(isEventLine, sections[3]))
  eventDicts = (map(curriedEventLineToEventDict, eventLines[0]), map(curriedEventLineToEventDict, eventLines[1]), map(curriedEventLineToEventDict, eventLines[2]))
  return (map(formatEventRow, eventDicts[0]), map(formatEventRow, eventDicts[1]), map(formatEventRow, eventDicts[2]))

def formatTable(eventStrings):
  output = formatTableHeader()
  output += formatSection("Upcoming", eventStrings[0])
  output += formatSection("Ongoing", eventStrings[1])
  output += formatSection("Completed", eventStrings[2])
  return output

def liquipediaStringToWiki(game, lines):
  output = formatWikiHeader()
  output += lines
  return output

def liquipediaStringToSidebar(game, lines):
  return formatTable(linesToEventStrings(game, lines))

def getCurrentLiquipediaEventsForWiki(game):
  wiki = liquipediaStringToWiki(game, liquipediaEventsJsonToSidebar(getLiquipediaEventsJson()))
  return wiki

def getCurrentLiquipediaEventsForSidebar(game):
  return liquipediaStringToSidebar(game, liquipediaEventsIntoLines(cleanLiquipediaEvents(getLiquipediaEvents(game))))

def getCurrentSidebar(prawLogin, subreddit):
  return prawLogin.get_settings(prawLogin.get_subreddit(subreddit))['description']

def setWikiPage(prawLogin, subredditName, wikiPageName, game):
  subreddit = prawLogin.subreddit(subredditName)
  newContent = getCurrentLiquipediaEventsForWiki(game)
  subreddit.wiki[wikiPageName].edit(newContent, 'beep boop - backing up event data')

def replaceCarriageReturn(html):
  return html.replace("\r","")

def subEventTableIntoSidebar(sidebar, table):
  cleaned = replaceCarriageReturn(sidebar)
  replace1 = re.sub(r"\*\*Event List\*\*\n\n(\|[^\n]+\n)+", u"**Event List**\n\n" + unicode(table, "UTF-8"), cleaned)
  return re.sub(r"#Schedule\n(\|[^\n]+\n)+", u"#Schedule\n" + unicode(table, "UTF-8"), replace1)

def cleanHtml(html):
  return html.replace("&gt;",">").replace("&amp;","&")

def getNewSidebar(prawLogin, subreddit, game):
  currentSidebar = getCurrentSidebar(prawLogin, subreddit)
  newTable = getCurrentLiquipediaEventsForSidebar(game)
  return cleanHtml(subEventTableIntoSidebar(currentSidebar, newTable))

def setSidebar(prawLogin, subreddit, game):
  newSidebar = getNewSidebar(prawLogin, subreddit, game)
  prawLogin.update_settings(prawLogin.get_subreddit(subreddit), description=newSidebar)
