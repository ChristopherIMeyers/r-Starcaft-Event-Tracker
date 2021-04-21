import json
import functions

def lambda_handler(event, context):
  prawLogin = functions.GetPraw()
  functions.setWikiPage(prawLogin)
  functions.setNewWikiPage(prawLogin)
  functions.updateSidebar(prawLogin)
  #functions.updateWidget(prawLogin)
  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }
