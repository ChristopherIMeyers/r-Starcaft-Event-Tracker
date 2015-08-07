import unittest
import praw
import httplib
import re
from itertools import groupby

import functions

class CheckSanity(unittest.TestCase):
  def test_praw(self):
    r = praw.Reddit(user_agent='r/starcraft event tracker')
    frontpage = r.get_front_page()
    self.assertEqual(sum(1 for _ in frontpage), 25)

  def test_http(self):
    self.assertTrue(len(functions.getLiquipediaEvents()) > 3000)

  def test_intoLines(self):
    self.assertTrue(len(functions.liquipediaEventsIntoLines(functions.getLiquipediaEvents())) > 70)

  def test_isEventLine(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    maps = filter(functions.isEventLine, lines);
    self.assertEqual(len(maps), 13)
    f = open('lpevents.heroes.txt', 'r')
    lines = f.readlines()
    maps = filter(functions.isEventLine, lines);
    self.assertEqual(len(maps), 51)

  def test_getSections(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    maps = filter(functions.isSectionLine, lines);
    self.assertEqual(len(maps), 3)
    sections = map(functions.getSectionName, maps);
    self.assertEqual(sections, ['UPCOMING', 'ONGOING', 'COMPLETED'])

  def test_splitBySection(self):
    f = open('lpevents.txt', 'r')
    lines = f.readlines()
    splitLines = functions.splitBySection(lines)
    self.assertEqual(len(splitLines), 4)
    fileHeader = filter(functions.isEventLine, splitLines[0])
    upcoming = filter(functions.isEventLine, splitLines[1])
    ongoing = filter(functions.isEventLine, splitLines[2])
    completed = filter(functions.isEventLine, splitLines[3])
    self.assertEqual(fileHeader, [])
    self.assertEqual(upcoming, ['{{TNL|link=[[IEM_Season_VIII_-_Cologne|IEM Season VIII Cologne]]|league=iem|sdate=13 Feb|edate=16 Feb}}\n'])
    self.assertEqual(ongoing, ['{{TNL|link=[[2014_Proleague/Round_1/Playoffs|2014 Proleague]]|league=pl|sdate=29 Dec|edate=9 Aug}}\n', '{{TNL|link=[[ESET_Masters_2013|ESET Masters 2013]]|sdate=1 May|edate=}}\n', '{{TNL|link=[[2014_WCS_Season_1_Europe|2014 WCS S1 Europe]]|league=wcseu|sdate=21 Jan|edate= }}\n', '{{TNL|link=[[2014_WCS_Season_1_America|2014 WCS S1 America]]|league=wcsam|sdate=21 Jan|edate=6 Apr}}\n', '{{TNL|link=[[2014_Global_StarCraft_II_League_Season_1/Code_S|2014 GSL Season 1]]|league=gsl|sdate=15 Jan|edate=5 Apr}}\n', '{{TNL|link=[[Warer.com Invitational]]|sdate=23 Jan|edate=7 Feb}}\n', "{{TNL|link=[[Twitch_Ender%27s_Game_on_Blu-ray_Tournament|Ender's Game Tournament]]|sdate=5 Feb|edate=9 Feb}}\n"])
    self.assertEqual(completed, ['{{TNL|link=[[ASUS ROG Winter 2014|ASUS ROG Winter 2014]]|league=rog|sdate=31 Jan|edate=1 Feb}}\n', '{{TNL|link=[[IEM_Season_VIII_-_Sao_Paulo|IEM Season VIII Sao Paulo]]|league=iem|sdate=29 Jan|edate=1 Feb}}\n', '{{TNL|link=[[MLG_GameOn_Invitational|MLG GameOn Invitational]]|sdate=19 Jan|edate=26 Jan}}\n', '{{TNL|link=[[NationWars]]|sdate=17 Jan|edate=19 Jan}}\n', '{{TNL|link=[[Taiwan eSports League/2013-2014/Season 2|TeSL 2013-2014 Season 2]]|sdate=15 Nov|edate=12 Jan}}\n'])

  def test_formatEventRow(self):
    eventObj = dict(name= "2013 DH Summer", link = "http://wiki.teamliquid.net/starcraft2/2013_DreamHack_Open/Summer", start = "15 Jun", end = "17 Jun")
    expectedOutput = "|[2013 DH Summer](http://wiki.teamliquid.net/starcraft2/2013_DreamHack_Open/Summer) | 15 Jun | 17 Jun |\n"
    self.assertEqual(functions.formatEventRow(eventObj), expectedOutput)

  def test_formatSectionRow(self):
    sectionName = "Upcoming"
    expectedOutput = "| **Upcoming**| | |\n"
    self.assertEqual(functions.formatSectionRow(sectionName), expectedOutput)

  def test_convertEventLineToEventDict(self):
    exampleEventLine = "{{TNL|link=[[2014_Proleague/Round_1/Playoffs|2014 Proleague]]|league=pl|sdate=29 Dec|edate=9 Aug}}"
    expectedDict = dict(name= "2014 Proleague", link = "http://wiki.teamliquid.net/starcraft2/2014_Proleague/Round_1/Playoffs", start = "29 Dec", end = "9 Aug")
    self.assertEqual(functions.convertEventLineToEventDict(exampleEventLine), expectedDict)

    exampleEventLine = "{{TNL|link=[[NationWars]]|sdate=17 Jan|edate=19 Jan}}"
    expectedDict = dict(name= "NationWars", link = "http://wiki.teamliquid.net/starcraft2/NationWars", start = "17 Jan", end = "19 Jan")
    self.assertEqual(functions.convertEventLineToEventDict(exampleEventLine), expectedDict)

    exampleEventLine = "{{TNL|link=[[Warer.com Invitational]]|sdate=23 Jan|edate=7 Feb}}"
    expectedDict = dict(name= "Warer.com Invitational", link = "http://wiki.teamliquid.net/starcraft2/Warer.com_Invitational", start = "23 Jan", end = "7 Feb")
    self.assertEqual(functions.convertEventLineToEventDict(exampleEventLine), expectedDict)

  def test_liquipediaStringToWiki(self):
    f = open('lpevents.txt', 'r')
    wiki = functions.liquipediaStringToWiki(f.readlines())
    self.assertEqual(len(wiki), 1671)

  def test_subEventTableIntoSidebar(self):
    oldSidebar = "**Event List**\n\n| table|\n| cells|\n\n"
    expectedSidebar = "**Event List**\n\nnew table text\n\n"
    newTable = "new table text\n"
    newSidebar = functions.subEventTableIntoSidebar(oldSidebar, newTable)
    self.assertEqual(newSidebar, expectedSidebar)

  def test_subEventTableIntoSidebarReal(self):
    oldSidebar = open('sidebar.old.txt', 'r').read()
    expectedSidebar = open('sidebar.new.txt', 'r').read()
    newTable = open('newtable.txt', 'r').read()
    newSidebar = functions.subEventTableIntoSidebar(oldSidebar, newTable)
    self.assertEqual(newSidebar, expectedSidebar)

  def test_liquipediaStringToSidebar(self):
    f = open('lpevents.txt', 'r')
    sidebar = functions.liquipediaStringToSidebar(f.readlines())
    self.assertEqual(len(sidebar), 1541)

  def test_stabilityOfMultipleSidebarUpdatesWithLiveData(self):
    r = praw.Reddit(user_agent='r/starcraft event tracker')
    originalSidebar = functions.liquipediaStringToSidebar(open('lpevents.txt', 'r').readlines())
    newTable = functions.getCurrentLiquipediaEventsForSidebar()
    firstSidebar = functions.subEventTableIntoSidebar(originalSidebar, newTable)
    secondSidebar = functions.subEventTableIntoSidebar(firstSidebar, newTable)
    self.assertEqual(firstSidebar, secondSidebar)

if __name__ == '__main__':
  unittest.main()
