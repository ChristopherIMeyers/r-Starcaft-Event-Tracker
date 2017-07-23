import praw
import functions
import settings

prawLogin = functions.GetPraw()

functions.setWikiPage(prawLogin, "Starcraft", "eventlist", "starcraft2")
