r-Starcaft-Event-Tracker [![Build Status](https://travis-ci.org/ChristopherIMeyers/r-Starcaft-Event-Tracker.png?branch=master)](https://travis-ci.org/ChristopherIMeyers/r-Starcaft-Event-Tracker)
========================

The r/Starcraft Event Tracker

Update AWS Server
---
```bash
sudo yum install python27
sudo yum install python27-pip
sudo python27 -m pip install praw
```

Update Script on Server
---
```bash
cp eventtracker/settings.py settings.py
rm -r eventtracker
wget https://github.com/ChristopherIMeyers/r-Starcaft-Event-Tracker/archive/master.zip
unzip master.zip
rm master.zip
mv r-Starcaft-Event-Tracker-master eventtracker
mv settings.py eventtracker/settings.py
```

Project Goals
---

1. Showcase currently live (and very soon to be live) events with link
2. Showcase upcoming events
3. Show a simple calendar of events (on the wiki?)
4. Pull data from multiple sources
5. Allow manual entry for events
5. Export data into google calendar for others to use
6. Integrate into sidebar


Known Data Sources
---

1. Team Liquid calendar [link](http://www.teamliquid.net/calendar/2014/01/)
2. Liquipedia upcoming tournaments [api](http://wiki.teamliquid.net/starcraft2/api.php?format=txt&action=query&titles=Liquipedia:Tournament_News&prop=revisions&rvprop=content) [wiki](http://wiki.teamliquid.net/starcraft2/Liquipedia:Tournament_News)


