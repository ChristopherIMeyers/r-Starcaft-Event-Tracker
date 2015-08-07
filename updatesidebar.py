import praw
import functions
import settings

prawLogin = praw.Reddit(user_agent='r/starcraft event tracker script')
prawLogin.login(settings.reddituser, settings.redditpass)

functions.setSidebar(prawLogin, "Starcraft", "starcraft2")
functions.setSidebar(prawLogin, "HeroesOfTheStorm", "heroes")
