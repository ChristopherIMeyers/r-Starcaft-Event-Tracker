import praw
import functions
import settings

prawLogin = praw.Reddit(user_agent='r/starcraft event tracker script')
prawLogin.login(settings.reddituser, settings.redditpass)

functions.setSidebar(prawLogin)
