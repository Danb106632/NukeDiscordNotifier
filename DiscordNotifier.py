import nuke
import nukescripts
from PySide2 import QtMultimedia

import json
import os

from discord_webhook import DiscordWebhook

jsonDirPath = os.path.dirname(__file__) 
jsonFilePath = jsonDirPath + '/json/DiscordNotifierSettings.json'


class DiscordPanel(nukescripts.PythonPanel):
    def __init__( self, userid, webhook ):
        nukescripts.PythonPanel.__init__( self, 'Discord Notifier' )  
        
        self.useridKnob = nuke.String_Knob('userid', 'Discord User ID:' , userid)
        self.webhookKnob = nuke.String_Knob('webhook', 'Discord Webhook URL:' , webhook)
        
        self.addKnob( self.useridKnob )
        self.addKnob( self.webhookKnob )
      
def getUserId(): 
  
    userId = '0'
    
    if not os.path.exists(jsonFilePath):
        createUserIdFile()
        
    with open(jsonFilePath, 'r') as file:
        try:
            userId = json.load(file)['userid']        
        except json.decoder.JSONDecodeError:
            nuke.tprint('Discord UserID error')
        
    return int(userId)

def getUserWebhook(): 
  
    userId = 'https://discord.com/api/webhooks/'
       
    if not os.path.exists(jsonFilePath):
        createUserIdFile()
        
    with open(jsonFilePath, 'r') as file:
        try:
            webhook = json.load(file)['webhook']        
        except json.decoder.JSONDecodeError:
            nuke.tprint('Discord UserID error')
        
    return webhook

def createUserIdFile():
    blank_data = {
        "userid": 0,
        "webhook": ""
    }
        
    json_object = json.dumps(blank_data, indent=4)
          
    os.makedirs(jsonDirPath+ '/json', exist_ok=True)
    with open(jsonFilePath, 'w') as file:
        file.write(json_object)   

def writeUserId(userId, webhook):
    with open(jsonFilePath, "w") as file:
    
        data = {
            "userid": int(userId),
            "webhook": str(webhook)
        } 
            
        json_object = json.dumps(data, indent=4)
        file.write(json_object)

def notifyUser():
    
    QtMultimedia.QSound.play(jsonDirPath+'/sounds/completed.wav')
    
    node = nuke.thisNode()
    
    indexTab, indexCheckbox = getKnobs(node)
    if ((node.knob(indexCheckbox)).getValue()) != 1:
        nuke.tprint('Write Notifiy disabled. Skipping notify...')
        return
    
    if(len(str(getUserId()))) != 18:
        nuke.tprint('Discord User ID error. Skipping notify...')
        return
    
    nuke.tprint('Notifiying Discord User ID!')
    
    content = "<@%s> %s finished rendering" % (getUserId(), node['name'].getValue())

    webhook = DiscordWebhook(url=getUserWebhook(), content=content)
    response = webhook.execute()
    
    print(response)
    
    if response.status_code == '404':
        nuke.say('Invalid Discord Webhook provided. You weren\'t notified!')
        

def getKnobs(node):
    indexTab = -1
    indexCheckbox = -1
    for index in range(node.numKnobs()):
        if 'discordTab' in node.knob(index).name():
            indexTab = index     
        if 'notifyCheckbox' in node.knob(index).name():
            indexCheckbox = index
    
    return indexTab, indexCheckbox     

def addSettings(node, indexTab, indexCheckbox):
    if indexTab == -1:
        tab = nuke.Tab_Knob('discordTab', 'Discord')
        node.addKnob(tab)

    if indexCheckbox == -1:
        checkBox = nuke.Boolean_Knob('notifyCheckbox', 'Notify on Discord', True)
        node.addKnob(checkBox)
        
def newNode():
    node = nuke.thisNode()
    indexTab = 0
    indexCheckbox = 0
    
    indexTab, indexCheckbox = getKnobs(node)
    
    addSettings(node, indexTab, indexCheckbox)

def main():
    
    if len(str(getUserId())) == 18 and getUserWebhook() != 'https://discord.com/api/webhooks/':
        nuke.tprint('Valid Discord User ID provided')
        nuke.addAfterRender(notifyUser)
        return
    
    Discord_Panel = DiscordPanel(str(getUserId()), getUserWebhook())
    Discord_Panel.setMinimumSize(400, 50)
    
    if Discord_Panel.showModalDialog():
        if len(Discord_Panel.useridKnob.value()) != 18:
            nuke.tprint('Invalid Discord User ID provided. Skipping notify...')
            return
        
        if Discord_Panel.webhookKnob.value() == 'https://discord.com/api/webhooks/':
            nuke.tprint('Invalid Discord Webhook provided. Skipping notify...')
            return
        
        writeUserId(Discord_Panel.useridKnob.value(), Discord_Panel.webhookKnob.value())
        nuke.addAfterRender(notifyUser) 
        
    nuke.tprint('No Discord User ID provided. Skipping notify...')
    return

nuke.addOnCreate(newNode, nodeClass='Write')
nuke.addOnScriptLoad(main)
