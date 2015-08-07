import unittest
import praw
import httplib
import re
from itertools import groupby

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
    eventLink = matches.group(1)
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
  return "|[{0}]({1}) | {2} | {3} |\n".format(event['name'], event['link'], event['start'], event['end'])

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
  output += formatTable(linesToEventStrings(game, lines))
  return output

def liquipediaStringToSidebar(game, lines):
  return formatTable(linesToEventStrings(game, lines))

def getCurrentLiquipediaEventsForWiki(game):
  wiki = liquipediaStringToWiki(game, liquipediaEventsIntoLines(cleanLiquipediaEvents(getLiquipediaEvents(game))))
  return wiki

def getCurrentLiquipediaEventsForSidebar(game):
  return liquipediaStringToSidebar(game, liquipediaEventsIntoLines(cleanLiquipediaEvents(getLiquipediaEvents(game))))

def getCurrentSidebar(prawLogin, subreddit):
  return prawLogin.get_settings(prawLogin.get_subreddit(subreddit))['description']

def setWikiPage(prawLogin, subredditName, wikiPageName, game):
  prawLogin.edit_wiki_page(prawLogin.get_subreddit(subredditName), wikiPageName, getCurrentLiquipediaEventsForWiki(game), "beep boop")

def replaceCarriageReturn(html):
  return html.replace("\r","")

def subEventTableIntoSidebar(sidebar, table):
  cleaned = replaceCarriageReturn(sidebar)
  return re.sub(r"\*\*Event List\*\*\n\n(\|[^\n]+\n)+", u"**Event List**\n\n" + unicode(table, "UTF-8"), cleaned)

def cleanHtml(html):
  return html.replace("&gt;",">").replace("&amp;","&")

def setSidebar(prawLogin, subreddit, game):
  currentSidebar = getCurrentSidebar(prawLogin, subreddit)
  newTable = getCurrentLiquipediaEventsForSidebar(game)
  newSidebar = cleanHtml(subEventTableIntoSidebar(currentSidebar, newTable))
  prawLogin.update_settings(prawLogin.get_subreddit(subreddit), description=newSidebar)
