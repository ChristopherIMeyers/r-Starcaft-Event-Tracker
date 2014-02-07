import unittest
import praw
import httplib

def getLiquipediaEvents():
  conn = httplib.HTTPConnection('wiki.teamliquid.net')
  conn.connect()
  request = conn.putrequest('GET','/starcraft2/api.php?format=txt&action=query&titles=Liquipedia:Tournament_News&prop=revisions&rvprop=content')
  conn.endheaders()
  conn.send('')
  return conn.getresponse().read()

class CheckSanity(unittest.TestCase):
  def test_praw(self):
    r = praw.Reddit(user_agent='r/starcraft event tracker')
    frontpage = r.get_front_page()
    self.assertEqual(sum(1 for _ in frontpage), 25)

  def test_http(self):
    self.assertTrue(len(getLiquipediaEvents()) > 4000)
    

if __name__ == '__main__':
  unittest.main()