import praw
import functions
import settings

prawLogin = functions.GetPraw()

functions.setNewWikiPage(prawLogin, "Starcraft", "eventlistnew", "starcraft2")
