r-Starcaft-Event-Tracker [![Build Status](https://travis-ci.org/ChristopherIMeyers/r-Starcaft-Event-Tracker.png?branch=master)](https://travis-ci.org/ChristopherIMeyers/r-Starcaft-Event-Tracker)
========================

The r/Starcraft Event Tracker

Update AWS Server
---
```bash
sudo yum install python27
sudo python27 -m pip install --upgrade pip
sudo python27 -m pip install --upgrade praw
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

Settings.py
---
```python
reddituser=''
redditpass=''
client_id=''
client_secret=''
```
