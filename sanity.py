import unittest

import functions

class CheckSanity(unittest.TestCase):
  def test_http(self):
    content = functions.getLiquipediaEventsJson('starcraft2')
    self.assertEqual(content[:50], '{"batchcomplete":"","warnings":{"main":{"*":"Subsc')
    self.assertTrue(len(content) > 2500)
    self.assertTrue(len(content) < 3500)

  def test_liquipediaEventsJsonIntoSource(self):
    with open('testdata/lpevents.1.json.txt', 'r') as f:
      data1 = f.read()
    with open('testdata/lpevents.2.json.txt', 'r') as f:
      data2 = f.read()
    self.assertEqual(len(functions.liquipediaEventsJsonIntoSource(data1)), 3573)
    self.assertEqual(len(functions.liquipediaEventsJsonIntoSource(data2)), 1921)

  def test_liquipediaEventsJsonToSidebar(self):
    with open('testdata/lpevents.1.json.txt', 'r') as f:
      inputData1 = f.read()
    with open('testdata/lpevents.2.json.txt', 'r') as f:
      inputData2 = f.read()
    with open('testdata/lpevents.json.output.txt', 'r') as f:
      expectedData = f.read()
    self.assertEqual(functions.liquipediaEventsJsonToSidebar(inputData1, inputData2), expectedData)

  def test_liquipediaEventsJsonToNewSidebar(self):
    self.maxDiff = None
    with open('testdata/lpevents.1.json.txt', 'r') as f:
      inputData1 = f.read()
    with open('testdata/lpevents.2.json.txt', 'r') as f:
      inputData2 = f.read()
    with open('testdata/newsidebar.output.txt', 'r') as f:
      expectedData = f.read()
    self.assertEqual(functions.liquipediaEventsJsonToNewSidebar(inputData1, inputData2), expectedData)

  def test_eventTableReplacement(self):
    with open('testdata/lpevents.json.output.txt', 'r') as f:
      newTable = f.read()
    with open('testdata/sidebar.old.txt', 'r') as f:
      oldContent = f.read()
    with open('testdata/sidebar.new.txt', 'r') as f:
      expectedNew = f.read()
    actualNew = functions.replaceNewEventTable(oldContent, newTable)
    self.assertEqual(actualNew, expectedNew)

  def test_intoLines(self):
    self.assertEqual(len(functions.liquipediaEventsIntoLines(functions.getLiquipediaEventsJson('starcraft2'))), 1)

  def test_formatEventRow(self):
    eventObj = dict(name= "2013 DH Summer", link = "somelink", start = "15 Jun", end = "17 Jun")
    expectedOutput = "|[2013 DH Summer](http://liquipedia.net/somegame/somelink) | 15 Jun | 17 Jun |\n"
    self.assertEqual(functions.formatEventRow('somegame')(eventObj), expectedOutput)

  def test_isJsonSectionLine(self):
    self.assertEqual(functions.isJsonSectionLine("*Upcoming"), True)
    self.assertEqual(functions.isJsonSectionLine("**2019 WCS Summer | 2019 WCS Summer | startdate=Jul 12 | enddate=Jul 14 | icon=wcs"), False)

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

  def test_dateReplacements(self):
    self.assertEqual(functions.dateReplacements("Sep 07"), "Sep&nbsp;07")

if __name__ == '__main__':
  unittest.main()
