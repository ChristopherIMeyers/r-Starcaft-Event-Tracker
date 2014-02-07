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

def isEventLine(str):
  return re.match("{{TNL\|link=\[\[.*}}", str) != None

def isSectionLine(str):
  return re.match(".*box_header tnl-header.*", str) != None

def getSectionName(str):
  return re.match(".*box_header tnl-header.*>([A-Z]+)", str).group(1)

def splitBySection(lines):
  return [list(group) for k, group in groupby(lines, lambda x: isSectionLine(x)) if not k]

class CheckSanity(unittest.TestCase):
  def test_praw(self):
    r = praw.Reddit(user_agent='r/starcraft event tracker')
    frontpage = r.get_front_page()
    self.assertEqual(sum(1 for _ in frontpage), 25)

  def test_http(self):
    self.assertTrue(len(getLiquipediaEvents()) > 4000)

  def test_isEventLine(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    maps = filter(isEventLine, lines);
    self.assertEqual(len(maps), 13)

  def test_getSections(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    maps = filter(isSectionLine, lines);
    self.assertEqual(len(maps), 3)
    sections = map(getSectionName, maps);
    self.assertEqual(sections, ['UPCOMING', 'ONGOING', 'COMPLETED'])

  def test_splitBySection(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    splitLines = splitBySection(lines)
    self.assertEqual(len(splitLines), 4)
    fileHeader = filter(isEventLine, splitLines[0])
    upcoming = filter(isEventLine, splitLines[1])
    ongoing = filter(isEventLine, splitLines[2])
    completed = filter(isEventLine, splitLines[3])
    self.assertEqual(fileHeader, [])
    self.assertEqual(upcoming, ['{{TNL|link=[[IEM_Season_VIII_-_Cologne|IEM Season VIII Cologne]]|league=iem|sdate=13 Feb|edate=16 Feb}}\n'])
    self.assertEqual(ongoing, ['{{TNL|link=[[2014_Proleague/Round_1/Playoffs|2014 Proleague]]|league=pl|sdate=29 Dec|edate=9 Aug}}\n', '{{TNL|link=[[ESET_Masters_2013|ESET Masters 2013]]|sdate=1 May|edate=}}\n', '{{TNL|link=[[2014_WCS_Season_1_Europe|2014 WCS S1 Europe]]|league=wcseu|sdate=21 Jan|edate= }}\n', '{{TNL|link=[[2014_WCS_Season_1_America|2014 WCS S1 America]]|league=wcsam|sdate=21 Jan|edate=6 Apr}}\n', '{{TNL|link=[[2014_Global_StarCraft_II_League_Season_1/Code_S|2014 GSL Season 1]]|league=gsl|sdate=15 Jan|edate=5 Apr}}\n', '{{TNL|link=[[Warer.com Invitational]]|sdate=23 Jan|edate=7 Feb}}\n', "{{TNL|link=[[Twitch_Ender%27s_Game_on_Blu-ray_Tournament|Ender's Game Tournament]]|sdate=5 Feb|edate=9 Feb}}\n"])
    self.assertEqual(completed, ['{{TNL|link=[[ASUS ROG Winter 2014|ASUS ROG Winter 2014]]|league=rog|sdate=31 Jan|edate=1 Feb}}\n', '{{TNL|link=[[IEM_Season_VIII_-_Sao_Paulo|IEM Season VIII Sao Paulo]]|league=iem|sdate=29 Jan|edate=1 Feb}}\n', '{{TNL|link=[[MLG_GameOn_Invitational|MLG GameOn Invitational]]|sdate=19 Jan|edate=26 Jan}}\n', '{{TNL|link=[[NationWars]]|sdate=17 Jan|edate=19 Jan}}\n', '{{TNL|link=[[Taiwan eSports League/2013-2014/Season 2|TeSL 2013-2014 Season 2]]|sdate=15 Nov|edate=12 Jan}}\n'])



if __name__ == '__main__':
  unittest.main()
