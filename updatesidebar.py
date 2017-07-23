import praw
import functions
import settings

prawLogin = functions.GetPraw()

functions.setSidebar(prawLogin, "Starcraft", "starcraft2")
