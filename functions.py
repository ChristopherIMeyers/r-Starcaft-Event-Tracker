import unittest
import praw
import httplib
import re
from itertools import groupby

import settings as settings

def getLiquipediaEvents():
  conn = httplib.HTTPConnection('wiki.teamliquid.net')
  conn.connect()
  request = conn.putrequest('GET','/starcraft2/api.php?format=txt&action=query&titles=Liquipedia:Tournament_News&prop=revisions&rvprop=content')
  conn.endheaders()
  conn.send('')
  return conn.getresponse().read()

def isEventLine(str):
  return re.match("{{TNL\|link=\[\[.*}}", str) != None

def isSectionLine(str):
  return re.match(".*box_header tnl-header.*", str) != None

def getSectionName(str):
  return re.match(".*box_header tnl-header.*>([A-Z]+)", str).group(1)

def splitBySection(lines):
  return [list(group) for k, group in groupby(lines, lambda x: isSectionLine(x)) if not k]

def formatEventRow(event):
  return "|[{0}]({1}) | {2} | {3} |".format(event['name'], event['link'], event['start'], event['end'])

def formatSectionRow(sectionName):
  return "| **{0}**| | |".format(sectionName)

def formatTableHeader():
  return "| |Starts |Ends |\n|:-----------|:------------|:------------|"

def formatWikiHeader():
  return "#Starcraft Event List\nUpdated by /u/Automaton2000    \nSourced from [Liquipedia](http://wiki.teamliquid.net/starcraft2/Main_Page)"
