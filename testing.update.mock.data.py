import functions

latestSc1Content = functions.getLiquipediaEventsJson('starcraft')
latestSc2Content = functions.getLiquipediaEventsJson('starcraft2')

open('lpevents.1.json.txt', 'w').write(latestSc1Content)
open('lpevents.2.json.txt', 'w').write(latestSc2Content)

