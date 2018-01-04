import unittest
import praw
import httplib
import re
import json
from itertools import groupby
import codecs

import functions

class CheckSanity(unittest.TestCase):
  def test_http(self):
    self.assertTrue(len(functions.getLiquipediaEventsJson('starcraft2')), 3000)

  def test_liquipediaEventsJsonIntoSource(self):
    data1 = open('lpevents.1.json.txt', 'r').read()
    data2 = open('lpevents.2.json.txt', 'r').read()
    self.assertEqual(len(functions.liquipediaEventsJsonIntoSource(data1)), 854)
    self.assertEqual(len(functions.liquipediaEventsJsonIntoSource(data2)), 1406)

  def test_liquipediaEventsJsonToSidebar(self):
    inputData1 = codecs.open('lpevents.1.json.txt', 'r', "utf-8").read()
    inputData2 = codecs.open('lpevents.2.json.txt', 'r', "utf-8").read()
    expectedData = codecs.open('lpevents.json.output.txt', 'r', "utf-8").read()
    self.assertEqual(functions.liquipediaEventsJsonToSidebar(inputData1, inputData2), expectedData)

  def test_intoLines(self):
    self.assertEqual(len(functions.liquipediaEventsIntoLines(functions.getLiquipediaEventsJson('starcraft2'))), 1)

  def test_formatEventRow(self):
    eventObj = dict(name= "2013 DH Summer", link = "somelink", start = "15 Jun", end = "17 Jun")
    expectedOutput = "|[2013 DH Summer](http://liquipedia.net/somegame/somelink) | 15 Jun | 17 Jun |\n"
    self.assertEqual(functions.formatEventRow('somegame')(eventObj), expectedOutput)

  def test_formatSectionRow(self):
    sectionName = "Upcoming"
    expectedOutput = "| **Upcoming**| | |\n"
    self.assertEqual(functions.formatSectionRow(sectionName), expectedOutput)

  def test_eventNameReplacements(self):
    self.assertEqual(functions.eventNameReplacements("Season 2"), "S2")
    self.assertEqual(functions.eventNameReplacements("season 2"), "S2")
    self.assertEqual(functions.eventNameReplacements("abcseason 2abc"), "abcS2abc")
    self.assertEqual(functions.eventNameReplacements("xxxglobal StarCraft II leaguexxx"), "xxxGSLxxx")
    self.assertEqual(functions.eventNameReplacements("xxxGlobal starCraft II Leaguexxx"), "xxxGSLxxx")
    self.assertEqual(functions.eventNameReplacements("xxxglobal StarCraft leaguexxx"), "xxxGSLxxx")
    self.assertEqual(functions.eventNameReplacements("xxxGlobal starCraft Leaguexxx"), "xxxGSLxxx")

if __name__ == '__main__':
  unittest.main()
