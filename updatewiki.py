import praw
import functions
import settings

r = praw.Reddit(user_agent='r/starcraft event tracker script')
r.login(settings.reddituser, settings.redditpass)

functions.setWikiPage(r, "Starcraft", "eventlist")
