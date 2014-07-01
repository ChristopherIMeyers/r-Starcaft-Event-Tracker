import unittest
import praw
import httplib
import re
from itertools import groupby

def getLiquipediaEvents():
  conn = httplib.HTTPConnection('wiki.teamliquid.net')
  conn.connect()
  request = conn.putrequest('GET','/starcraft2/api.php?format=txt&action=query&titles=Liquipedia:Tournament_News&prop=revisions&rvprop=content')
  conn.endheaders()
  conn.send('')
  return conn.getresponse().read()

def liquipediaEventsIntoLines(events):
  return events.split('\n')

def isEventLine(str):
  return re.match("{{TNL\|link=\[\[.*}}", str) != None

def convertEventLineToEventDict(eventLine):
  matches = re.match("{{TNL\|link=\[\[(.*)\|(.*)\]\].*sdate=(.*)\|edate=(.*)}}", eventLine)
  if matches != None:
    eventName = matches.group(2)
    eventLink = matches.group(1)
    eventStart = matches.group(3)
    eventEnd = matches.group(4)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/starcraft2/"+eventLink, start = eventStart, end = eventEnd)
  matches = re.match("{{TNL\|link=\[\[(.*)\]\].*sdate=(.*)\|edate=(.*)}}", eventLine)
  if matches != None:
    eventName = matches.group(1)
    eventLink = matches.group(1).replace(" ", "_")
    eventStart = matches.group(2)
    eventEnd = matches.group(3)
    return dict(name= eventName, link = "http://wiki.teamliquid.net/starcraft2/"+eventLink, start = eventStart, end = eventEnd)
  return None

def isSectionLine(str):
  return re.match(".*box_header tnl-header.*", str) != None

def getSectionName(str):
  return re.match(".*box_header tnl-header.*>([A-Z]+)", str).group(1)

def splitBySection(lines):
  return [list(group) for k, group in groupby(lines, lambda x: isSectionLine(x)) if not k]

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

def linesToEventStrings(lines):
  sections = splitBySection(lines)
  eventLines = (filter(isEventLine, sections[1]), filter(isEventLine, sections[2]), filter(isEventLine, sections[3]))
  eventDicts = (map(convertEventLineToEventDict, eventLines[0]), map(convertEventLineToEventDict, eventLines[1]), map(convertEventLineToEventDict, eventLines[2]))
  return (map(formatEventRow, eventDicts[0]), map(formatEventRow, eventDicts[1]), map(formatEventRow, eventDicts[2]))

def formatTable(eventStrings):
  output = formatTableHeader()
  output += formatSection("Upcoming", eventStrings[0])
  output += formatSection("Ongoing", eventStrings[1])
  output += formatSection("Completed", eventStrings[2])
  return output

def liquipediaStringToWiki(lines):
  output = formatWikiHeader()
  output += formatTable(linesToEventStrings(lines))
  return output

def liquipediaStringToSidebar(lines):
  return formatTable(linesToEventStrings(lines))

def getCurrentLiquipediaEvents():
  wiki = liquipediaStringToWiki(liquipediaEventsIntoLines(getLiquipediaEvents()))
  return wiki

def setWikiPage(prawLogin):
  prawLogin.edit_wiki_page(prawLogin.get_subreddit("Starcraft"), "eventlist", getCurrentLiquipediaEvents(), "beep boop")

def subEventTableIntoSidebar(sidebar, table):
  return re.sub(r"\*\*Event List\*\*\n\n(\|[^\n]+\n)+", "**Event List**\n\n" + table, sidebar)
