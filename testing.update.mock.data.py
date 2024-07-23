import functions

latestSc1Content = functions.getLiquipediaEventsJson('starcraft')
latestSc2Content = functions.getLiquipediaEventsJson('starcraft2')

open('testdata/lpevents.1.json.txt', 'w').write(latestSc1Content)
open('testdata/lpevents.2.json.txt', 'w').write(latestSc2Content)

#compare to and eventually replace lpevents.json.output.txt
open('testdata/lpevents.json.output.new.txt', 'w').write(functions.liquipediaEventsJsonToSidebar(latestSc1Content, latestSc2Content))

#compare to and eventually replace newsidebar.output.txt
open('testdata/newsidebar.output.new.txt', 'w').write(functions.liquipediaEventsJsonToNewSidebar(latestSc1Content, latestSc2Content))



with open('testdata/lpevents.json.output.txt', 'r') as f:
  lpeventsJsonOutput = f.read()
with open('testdata/sidebar.old.txt', 'r') as f:
  sidebarOld = f.read()

#compare to and eventually replace sidebar.new.txt
open('testdata/sidebar.new.new.txt', 'w').write(functions.replaceNewEventTable(sidebarOld, lpeventsJsonOutput))
