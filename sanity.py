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
    self.assertTrue(len(functions.getLiquipediaEventsJson()), 3000)

  def test_liquipediaEventsJsonIntoSource(self):
    data = open('lpevents.json.txt', 'r').read()
    self.assertEqual(len(functions.liquipediaEventsJsonIntoSource(data)), 1406)

  def test_liquipediaEventsJsonToSidebar(self):
    inputData = codecs.open('lpevents.json.txt', 'r', "utf-8").read()
    expectedData = codecs.open('lpevents.json.output.txt', 'r', "utf-8").read()
    self.assertEqual(functions.liquipediaEventsJsonToSidebar(inputData), expectedData)

  def test_intoLines(self):
    self.assertEqual(len(functions.liquipediaEventsIntoLines(functions.getLiquipediaEventsJson())), 1)

  def test_formatEventRow(self):
    eventObj = dict(name= "2013 DH Summer", link = "http://wiki.teamliquid.net/starcraft2/2013_DreamHack_Open/Summer", start = "15 Jun", end = "17 Jun")
    expectedOutput = "|[2013 DH Summer](http://wiki.teamliquid.net/starcraft2/2013_DreamHack_Open/Summer) | 15 Jun | 17 Jun |\n"
    self.assertEqual(functions.formatEventRow(eventObj), expectedOutput)

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
