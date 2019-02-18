import functions

latestSc1Content = functions.getLiquipediaEventsJson('starcraft')
latestSc2Content = functions.getLiquipediaEventsJson('starcraft2')

open('testdata/lpevents.1.json.txt', 'w').write(latestSc1Content)
open('testdata/lpevents.2.json.txt', 'w').write(latestSc2Content)

