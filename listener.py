import os
import django

from image import generate_img



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genie.settings')
django.setup()

from whatsapp_api_client_python import API
import json
from datetime import datetime
import threading
from AIchat.models import Wmessage, Private_chat, Group, Special_chat
from datetime import datetime
from django.shortcuts import get_object_or_404
from RapidAPI import Message, Assistant
from whatsapp_api_client_python import API
import openai
import importlib.util
import sender
from news import get_headlines

def my_function(x,y):
    spec = importlib.util.find_spec("special_mode")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # use functions/classes from the imported module
    module.on_termpaper(x,y)




openai.api_key = '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'



#ID_INSTANCE = environ['ID_INSTANCE']
#API_TOKEN_INSTANCE = environ['API_TOKEN_INSTANCE']

ID_INSTANCE = '1101818429'
API_TOKEN_INSTANCE = '57caf663349e4ca9b51b4509c901259d7f53413acc514e24a1'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)


def main():
   greenAPI.webhooks.startReceivingNotifications(onEvent)

def onEvent(typeWebhook, body):
   if typeWebhook == 'incomingMessageReceived':
      threading.Thread(target=onIncomingMessageReceived, args=[body,]).start()
   elif typeWebhook == 'deviceInfo':   
      onDeviceInfo(body)              
   #elif typeWebhook == 'incomingCall':
    #  onIncomingCall(body)
   #elif typeWebhook == 'outgoingAPIMessageReceived':
    #  onOutgoingAPIMessageReceived(body)
   #elif typeWebhook == 'outgoingMessageReceived':
    #  onOutgoingMessageReceived(body)
   #elif typeWebhook == 'outgoingMessageStatus':
    #  onOutgoingMessageStatus(body)
   #elif typeWebhook == 'stateInstanceChanged':
    #  onStateInstanceChanged(body)
   #elif typeWebhook == 'statusInstanceChanged':
    #  onStatusInstanceChanged(body)

def onIncomingMessageReceived(body):
   idMessage = body['idMessage']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   senderData = body['senderData']
   messageData = body['messageData']

   if str(senderData['chatId']).endswith('g.us'):
      onIncomingGroupMessage(body)

   elif str(senderData['chatId']).endswith('c.us'):
      onIncomingPrivateMessage(body)

   else:
    pass


        

def onIncomingCall(body):
   idMessage = body['idMessage']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   fromWho = body['from']
   print(idMessage + ': ' 
      + 'Call from ' + fromWho 
      + ' at ' + str(eventDate))

def onDeviceInfo(body):
   eventDate = datetime.fromtimestamp(body['timestamp'])
   deviceData = body['deviceData']
   print('At ' + str(eventDate) + ': ' \
      + json.dumps(deviceData, ensure_ascii=False))

def onOutgoingMessageReceived(body):
   idMessage = body['idMessage']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   senderData = body['senderData']
   messageData = body['messageData']
   print(idMessage + ': ' 
      + 'At ' + str(eventDate) + ' Outgoing from ' \
      + json.dumps(senderData, ensure_ascii=False) \
      + ' message = ' + json.dumps(messageData, ensure_ascii=False))

def onOutgoingAPIMessageReceived(body):
   idMessage = body['idMessage']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   senderData = body['senderData']
   messageData = body['messageData']
   print(idMessage + ': ' 
      + 'At ' + str(eventDate) + ' API outgoing from ' \
      + json.dumps(senderData, ensure_ascii=False) + \
      ' message = ' + json.dumps(messageData, ensure_ascii=False))

def onOutgoingMessageStatus(body):
   idMessage = body['idMessage']
   status = body['status']
   eventDate = datetime.fromtimestamp(body['timestamp'])
   print(idMessage + ': ' 
      + 'At ' + str(eventDate) + ' status = ' + status)

def onStateInstanceChanged(body):
   eventDate = datetime.fromtimestamp(body['timestamp'])
   stateInstance = body['stateInstance']
   print('At ' + str(eventDate) + ' state instance = ' \
      + json.dumps(stateInstance, ensure_ascii=False))

def onStatusInstanceChanged(body):
   eventDate = datetime.fromtimestamp(body['timestamp'])
   statusInstance = body['statusInstance']
   print('At ' + str(eventDate) + ' status instance = ' \
      + json.dumps(statusInstance, ensure_ascii=False))


def onIncomingGroupMessage(body):
    idMessage = body['idMessage']
    eventDate = datetime.fromtimestamp(body['timestamp'])
    senderData = body['senderData']
    messageData = body['messageData']

    group, created = Group.objects.get_or_create(chat_id = senderData['chatId'])
    if created:
        group.groupname = senderData['chatName']
        first_group_msg = '''Hello everyone! 👋

I am Rapid, your new group assistant 🤖 made by Daniel eze. I am here to help make your group chats more fun, informative, and interesting. I can answer your questions, provide insights, and even engage in some light-hearted banter.

Don't worry, I won't spam the group with unnecessary messages. I'll only respond when I'm mentioned or quoted, so feel free to reach out to me anytime.

And just to add some flair to our chats, I come with a range of WhatsApp stickers that you can use to spice up your conversations. 🎉

Let's make this group even better together!
some functionalities:
🌃 /image TEXT 👉 Generate an image based on TEXT , the more detail the better
/query _question_ 👉 get answer to _question_ without context of recent group messages
/news  👉 returns some current news in 9ja
🌎/worldnews 👉 to get top 5 world news

'''
        #send_message(None,first_group_msg, group)
        print('new group\t  -------created')

    if messageData['typeMessage'] == 'textMessage' :
        print('simple text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['textMessageData']['textMessage'],
            date = eventDate,
            is_reaction = False,
            sender = senderData['sender'],
            sender_name = senderData['chatName'],
            quoted_message = None,
            groupchat = group
        ).save()

    elif messageData['typeMessage'] == 'extendedTextMessage' :
        print('extended text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['extendedTextMessageData']['text'],
            date = eventDate,
            is_reaction = False,
            sender = senderData['sender'],
            sender_name = senderData['chatName'],
            quoted_message = None,
            groupchat = group
        ).save()

    elif messageData['typeMessage'] == 'quotedMessage' or 'reactionMessage' :
        try:
            quoted_message = Wmessage.objects.get(message_id = messageData['quotedMessage']['stanzaId']).text
        except:
            quoted_message = ''

        
        print('quoted text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['extendedTextMessageData']['text'],
            date = eventDate,
            is_reaction = True,
            sender = senderData['sender'],
            sender_name = senderData['chatName'],
            quoted_message = messageData['quotedMessage']['stanzaId'],
            groupchat = group
        ).save()
        if quoted_message == '/news selection list':
            category = messageData['extendedTextMessageData']['text'].strip().lower()
            get_headlines(category,group)
            return None

        elif quoted_message == '/worldnews selection list':
            category = messageData['extendedTextMessageData']['text'].strip().lower()
            get_headlines(category,group,country=None)
            return None
    elif messageData['typeMessage'] == 'listResponseMessage' :
    
        quoted_message = Wmessage.objects.get(message_id = messageData['listResponseMessage']['stanzaId']).text
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['listResponseMessage']['title'],
            date = eventDate,
            is_reaction = True,
            sender = senderData['sender'],
            #quoted_message = messageData['quotedMessage']['stanzaId'],
            chat = group
        ).save()
        if quoted_message == '/news selection list':
            category = messageData['listResponseMessage']['title']
            get_headlines(category,group)
        elif quoted_message == '/worldnews selection list':
            category = messageData['listResponseMessage']['title']
            get_headlines(category,group,country=None)
        return None
    else: pass
    
    group.save()
    message = Wmessage.objects.get(message_id=idMessage)
                    
    if '@2348062233878' in  message.text or message.is_reaction and messageData['quotedMessage']['participant'] == '2348062233878@c.us':

        if len(message.text)< 400:

        
            messags = Wmessage.objects.filter(groupchat=group).order_by('-date')[:10]
            messages = []

            #get last 50 group messeges
            for mes in messags:
                if mes.sender == '2348062233878@c.us':
                    x = Message('assistant', mes.text + '\n')
                    messages.append(x.message())
                else:
                    x = Message('user', mes.text + '\n')
                    messages.append(x.message())

            messages.reverse()

            last_content = messages[-1]['content'].replace('@2348062233878',"hey Rapid ")
            messages.pop()
            messages.append({'role':'user', 'content': last_content})
    
            #create messages dictionary

            #user_message = Message('user', message.sender + ': '+ message.text + '\n')
            chatID=senderData['chatId']
            

            if '@2348062233878' in  message.text:
                
                if message.is_reaction:
                    
                    try:
                        quoted_text = Wmessage.objects.get(message_id=message.quoted_message).text

                    except:
                        quoted_text = ''
                        

                    if '/qoc' in message.text:
                        qocq(message,quoted_text,group)
                        
                    else:
                        contrib(message,messages,group)
                    
                

                elif '/query' in message.text:
                    query(message,group)
                    
                elif '/qoc' in message.text:
                    qoc(message,messages,group)
                    
                elif '/image' in message.text:
                    try:
                        prompt = message.text.replace('/image','')
                        file = generate_img(prompt,message)
                        result = greenAPI.sending.sendFileByUpload(group.chat_id,file,fileName='generated',quotedMessageId=message.message_id)
                    except:
                        send_message2(None,'oops, server is busy. Try again later',group)
                elif message.text.startswith('/news'):      
                    #result = greenAPI.sending.sendListMessage(group.chat_id, '', sender.news_sections,title='Select news category', buttonText= 'Choose', footer='_note that this is for 9ja news. use /worldnews for world news_')
                    msg = 'reply this message with your desired category general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
                    result = greenAPI.sending.sendMessage(group.chat_id, msg)
                    Wmessage.objects.create(
                                    message_id = result.data['idMessage'],
                                    text = '/news selection list',
                                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    is_reaction = False,
                                    sender = '2348062233878@c.us',
                                    quoted_message = None,
                                    groupchat = group
                                ).save()
                    return None
                elif message.text.startswith('/worldnews'):

                    #result = greenAPI.sending.sendListMessage(group.chat_id, '', sender.news_sections, title='Select news category', buttonText= 'Choose', footer='_note that this is for world news. use /news for 9ja news_')
                    msg = 'reply this message with your desired category general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
                    result = greenAPI.sending.sendMessage(group.chat_id, msg)
                    Wmessage.objects.create(
                                    message_id = result.data['idMessage'],
                                    text = '/worldnews selection list',
                                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    is_reaction = False,
                                    sender = '2348062233878@c.us',
                                    quoted_message = None,
                                    groupchat = group
                                ).save()

                else:
                    contrib(message,messages,group)
                    

            elif message.is_reaction and messageData['quotedMessage']['participant'] == '2348062233878@c.us':
                try:
                    quoted_text = Wmessage.objects.get(message_id=message.quoted_message).text

                except:
                    quoted_text = ''
                
                if '/query' in message.text:
                    query(message,group)
                    
                elif '/qoc' in message.text:
                    qocq(message,quoted_text,group)
                    
                elif '/image' in message.text:
                    try:
                        prompt = message.text.replace('/image','')
                        file = generate_img(prompt,message)
                        result = greenAPI.sending.sendFileByUpload(group.chat_id,file,fileName='generated',quotedMessageId=message.message_id)
                    except:
                        send_message2(None,'oops, server is busy. Try again later',group)
                elif message.text.startswith('/news'):      
                    #result = greenAPI.sending.sendListMessage(group.chat_id, '', sender.news_sections,title='Select news category', buttonText= 'Choose', footer='_note that this is for 9ja news. use /worldnews for world news_')
                    msg = 'reply this message with your desired category general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
                    result = greenAPI.sending.sendMessage(group.chat_id, msg)
                    Wmessage.objects.create(
                                    message_id = result.data['idMessage'],
                                    text = '/news selection list',
                                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    is_reaction = False,
                                    sender = '2348062233878@c.us',
                                    quoted_message = None,
                                    groupchat = group
                                ).save()
                    return None
                elif message.text.startswith('/worldnews'):

                    #result = greenAPI.sending.sendListMessage(group.chat_id, '', sender.news_sections, title='Select news category', buttonText= 'Choose', footer='_note that this is for world news. use /news for 9ja news_')
                    msg = 'reply this message with your desired category general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
                    result = greenAPI.sending.sendMessage(group.chat_id, msg)
                    Wmessage.objects.create(
                                    message_id = result.data['idMessage'],
                                    text = '/worldnews selection list',
                                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    is_reaction = False,
                                    sender = '2348062233878@c.us',
                                    quoted_message = None,
                                    groupchat = group
                                ).save()
                else:
                    contrib(message,messages,group)
                    

            else: pass
        else:
            response = 'if you want me to read your long text, use the private assistant '
            send_message(message,response, group)
            Wmessage.objects.filter(message_id = message.message_id).delete()


def onIncomingPrivateMessage(body):
    idMessage = body['idMessage']
    eventDate = datetime.fromtimestamp(body['timestamp'])
    senderData = body['senderData']
    messageData = body['messageData']

    private_chat, created = Private_chat.objects.get_or_create(chat_id = senderData['chatId'])

    if created:
        #send first message to client
        first_msg = 'Welcome, I am Rapid! Your A.I powered companion on Whatsapp!\n💬 Ask me about anything, 🍔Recipes, ✈️Travelling, 🏋️‍♀️Fitness,📱Marketing, really.. anything, in any language!\n*Functionalities*\n⭐️Use  /clear 👉 In case Rapid  is not responding in the best way, you can clear the context of a conversation and start over\n🔐/setaccess _access token_ 👉 use this function to subscribe. chat up 07064950025 to get _access token_\n🌃 /image TEXT 👉 Generate an image based on TEXT , the more detail the better\n🌃 /image_var TEXT 👉 send along with an image to generate a variation of the image. sent image must be less than 4MB\n🫴/help  this provides you with helpful informations\n😄/termplates  👉  this provides you with helpful termplates for performing certain tasks like termpaper writing, videoscripts, blog etc and guess what?  ..it can even return your work as microsoft document🤓\n📰/news _topic_ 👉 returns some current news on the _topic_\n🌎/worldnews 👉 to get top 5 world news\n🎤 Audio Messages 👉 You can ask whatever you want using audio messages in any language\n*Note: I can also make mistakes*'
        send_message2(None,first_msg,private_chat)
        print('new chat\t  -------created')
        return None
    
    if private_chat.in_specialmode:
        my_function(private_chat,body)
        return None

    if messageData['typeMessage'] == 'textMessage' :
        print('simple text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['textMessageData']['textMessage'],
            date = eventDate,
            is_reaction = False,
            sender = senderData['sender'],
            quoted_message = None,
            chat = private_chat
        ).save()

    elif messageData['typeMessage'] == 'extendedTextMessage' :
        print('extended text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['extendedTextMessageData']['text'],
            date = eventDate,
            is_reaction = False,
            sender = senderData['sender'],
            quoted_message = None,
            chat = private_chat
        ).save()
    elif messageData['typeMessage'] == 'listResponseMessage' :
    
        try:
            quoted_message = Wmessage.objects.get(message_id = messageData['listResponseMessage']['stanzaId']).text
        except:
            quoted_message = ''
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['listResponseMessage']['title'],
            date = eventDate,
            is_reaction = True,
            sender = senderData['sender'],
            #quoted_message = messageData['quotedMessage']['stanzaId'],
            chat = private_chat
        ).save()
        if quoted_message == '/news selection list':
            category = messageData['listResponseMessage']['title']
            get_headlines(category,private_chat)

        elif quoted_message == '/worldnews selection list':
            category = messageData['listResponseMessage']['title']
            get_headlines(category,private_chat,country=None)

        elif messageData['listResponseMessage']['title'] == 'termpaper':
            if private_chat.is_subscribed:
                send_message2(None,'You are now in template_mode, to cancel use "/exit"',private_chat)
                my_function(private_chat,body)
                private_chat.in_specialmode = True
                private_chat.save()
                
                return None

            else: 
                msg = 'template mode is an advanced functionality that can even return your work in microsoft document format. chat up 07064950025 to subscribe with just 2000 naira. Thanks'
                send_message2(None,msg,private_chat)

            data = greenAPI.groups.getGroupData('2348139546829-1535297420@g.us').data
            
            participants=data['participants']
            if private_chat.chat_id in [x['id'] for x in participants]:
                
                access_token = private_chat.access_token
                msg = f'....but since you are in mech 4th year class, you will be subscribed for free. your access token is _{access_token}_.\nuse the function "/setaccess {access_token}" to subscribe and then try again. But I will also be glad if you can donate 1000 naira to help the project.\n acc no: 7064950025\n Eze daniel Opay'
                send_message2(None,msg,private_chat)
            return None
        return None
        

    elif messageData['typeMessage'] == 'quotedMessage' or 'reactionMessage' :
        try:
            quoted_message = Wmessage.objects.get(message_id = messageData['quotedMessage']['stanzaId']).text
        except:
            quoted_message = ''
        print('quoted text' + '\t'+ str(eventDate) + '\t' + senderData['chatId'] + '\t' + senderData['chatName'])
        Wmessage.objects.create(
            message_id = idMessage,
            text = messageData['extendedTextMessageData']['text'],
            date = eventDate,
            is_reaction = True,
            sender = senderData['sender'],
            quoted_message = messageData['quotedMessage']['stanzaId'],
            chat = private_chat
        ).save()
        if quoted_message == '/news selection list':
            category = messageData['extendedTextMessageData']['text'].strip().lower()
            get_headlines(category,private_chat)
            return None

        elif quoted_message == '/worldnews selection list':
            category = messageData['extendedTextMessageData']['text'].strip().lower()
            get_headlines(category,private_chat,country=None)
            return None
        



    

    else: return None
    
    private_chat.save()

    message = Wmessage.objects.get(message_id=idMessage)

    if len(message.text)< 120 or private_chat.is_subscribed:

        if private_chat.is_subscribed:
            messags = Wmessage.objects.filter(chat=private_chat).order_by('-date')
            if len(messags)==25:
                txt = 'use the /clear function to clear the database and have better response'
                send_message(None,txt,private_chat)

        else:
            messags = Wmessage.objects.filter(chat=private_chat).order_by('-date')[:5]
        messages = []

        #get last 50 group messeges
        for mes in messags:
            x = Message('user', mes.text + '\n')
            messages.append(x.message())

        messages.reverse()
        #create messages dictionary

        #user_message = Message('user', message.sender + ': '+ message.text + '\n')
        chatID=senderData['chatId']

        if message.text.startswith('/image'):
            if private_chat.is_subscribed:
                prompt = message.text.replace('/image','')
                try:
                    file = generate_img(prompt,message)
                    result = greenAPI.sending.sendFileByUpload(private_chat.chat_id,file,fileName='generated',quotedMessageId=message.message_id)
                except:
                    send_message2(None,'oops, server is busy. Try again later',private_chat)
            else: 
                msg = 'subscribe to generate image from text. To get your acces token, chat up 07064950025'
                send_message2(None,msg,private_chat)
        elif message.text.startswith('/help'):
            msg = 'here is a list of help:'
            send_message(None,msg,private_chat)

        elif message.text.startswith('/news'):

            #result = greenAPI.sending.sendListMessage(private_chat.chat_id, '*', sender.news_sections, title='Select news category', buttonText= 'Choose', footer='_note that this is for 9ja news. use /worldnews for world news_')
            msg = 'reply this message with your desired category general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
            result = greenAPI.sending.sendMessage(private_chat.chat_id, msg)
            Wmessage.objects.create(
                            message_id = result.data['idMessage'],
                            text = '/news selection list',
                            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            is_reaction = False,
                            sender = '2348062233878@c.us',
                            quoted_message = None,
                            chat = private_chat
                        ).save()
        elif message.text.startswith('/worldnews'):

           # result = greenAPI.sending.sendListMessage(private_chat.chat_id, '*', sender.news_sections, title='Select news category', buttonText= 'Choose', footer='_note that this is for world news. use /news for 9ja news_')
            msg = 'reply this message with your desired category\n general\nscience\nentertainment\nhealth\nbusiness\ntechnology\nsports'
            result = greenAPI.sending.sendMessage(private_chat.chat_id, msg)
            Wmessage.objects.create(
                            message_id = result.data['idMessage'],
                            text = '/worldnews selection list',
                            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            is_reaction = False,
                            sender = '2348062233878@c.us',
                            quoted_message = None,
                            chat = private_chat
                        ).save()

        elif message.text.lower().startswith('/templates'):
            message_text = 'this is a list of special templates for your works. it makes work much more easier and faster. it can be used for different kinds of work ranging from academic to social content writing.'
            result = greenAPI.sending.sendListMessage(private_chat.chat_id, message_text, sender.sections, title='list of templates', buttonText= 'Choose', footer='_only termpaper functionality is enabled for now_')


        elif message.text.startswith('/add-templates'):
            #
            pass
        elif message.text.startswith('/setaccess'):
            accessT = message.text.replace('/setaccess','').strip()
            if accessT == str(private_chat.access_token):
                private_chat.is_subscribed = True
                private_chat.save()
                send_message2(None, 'you are successfully subscribed. enjoy full functionality!!!', private_chat)
                
            elif private_chat.chat_id == '2347064950025@c.us':
                #print(private_chat.access_token)
                private_chat.is_subscribed = True
                private_chat.save()
                send_message2(None, 'you are successfully subscribed. enjoy full functionality!!!', private_chat)
            else:
                send_message2(None, 'wrong access token. Try again or get your access token by chatting up 07064950025', private_chat)
            
        elif message.text.startswith('/clear'):
            Wmessage.objects.filter(chat = private_chat).delete()
            msg = 'Done. You are as good as new'
            send_message(None,msg,private_chat)

        else:
            #simple professional assistant
            p_contrib(messages,private_chat)

    else:
        msg = 'subscribe at www.dummy.com to have more send more texts'
        send_message(msg,private_chat)
        Wmessage.objects.filter(message_id = message.message_id).delete()



def qoc(message, messages,group):
    #msg = message.text
    system_prompt = f''' you are a whatsapp group chat informational bot respond to the statement: {message.text} from {message.sender}  while paying attention to the last chats below:'''
    msg = message.text.replace('/qoc','')

    sys_message = Message('system', system_prompt).message()
    messages.insert(0,sys_message)
    conversation = Assistant()
    response_msg = conversation.ask_assistant(messages)
    response_message = response_msg['content']
    send_message(message,response_message,group)
    

def qocq(message, quoted_text,group):
    system_prompt = ''' you a brilliant group bot,first statement below is from the indicated group member. while the second one is a response to the first question and also addressed to you. reply to the statements: '''
    msgx = message.text.replace('/qoc','')
    sys_message = Message('system', system_prompt).message()
    messages = []

    q_msg = Message('user', quoted_text).message()
    msg = Message('user', msgx).message()
    messages.append(sys_message)
    messages.append(q_msg)
    messages.append(msg)

    conversation = Assistant()
    response_msg = conversation.ask_assistant(messages)
    response_message = response_msg['content']
    send_message(message,response_message,group)


def query(message,group):
    system_prompt = ''' you are a brilliant assistant. provide insightfull and very brief responses '''
    msgx = message.text.replace('/query','')
    print(message)
    sys_message = Message('system', system_prompt).message()
    messages = []

    msg = Message('user', msgx).message()
    messages.append(sys_message)
    messages.append(msg)
    print(messages)
    conversation = Assistant()
    response_msg = conversation.ask_assistant(messages)
    response_message = response_msg['content']
    send_message(message,response_message,group)

def contrib(message, messages,group):
    system_prompt = '''your name is Rapid made by Daniel eze.you a sarcastic, very funny and most importantly very concise whatsapp group bot. note that the last statement was addressed to you. also be very brief and also use whatsapp emojis to express you self. the last group messages are: '''

    sys_message = Message('system', system_prompt).message()
    messages.insert(0,sys_message)
    conversation = Assistant()
    
    

    response_msg = conversation.ask_assistant(messages)
    print(response_msg)
    response_message = response_msg['content'].lower().replace('as an ai language model','').replace("i'm sorry,","").replace('as i am an ai language model','').replace("i am sorry","").replace('is there anything else i can assist you with?','').replace('is there anything else i can help you with?','')
    send_message(message,response_message,group)


def p_contrib(messages,chat):
    system_prompt = '''your name is rapid made by Daniel eze.you a smart personal assistant. use enough whatsapp stickers when necessary. the last messages are: '''

    sys_message = Message('system', system_prompt).message()
    messages.insert(0,sys_message)
    conversation = Assistant()
    
    

    response_msg = conversation.ask_assistant(messages)
    response_message = response_msg['content']
    send_message(None,response_message,chat)

def send_message(message,response,cht):
    chatID = cht.chat_id
    if message == None:
        result = greenAPI.sending.sendMessage(chatID,response)
    else:
        result = greenAPI.sending.sendMessage(chatID,response,quotedMessageId=message.message_id)
    msg_id = result.data['idMessage']



    if str(chatID).endswith('c.us'):
        if cht.in_specialmode:
            Wmessage.objects.create(
                message_id = msg_id,
                text = response,
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                is_reaction = False,
                sender = '2348062233878@c.us',
                quoted_message = None,
                special_chat = Special_chat.objects.get(chat = cht)
            )

        else:
            Wmessage.objects.create(
                message_id = msg_id,
                text = response,
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                is_reaction = False,
                sender = '2348062233878@c.us',
                quoted_message = None,
                chat = cht
            )

    elif str(chatID).endswith('g.us'):
         Wmessage.objects.create(
            message_id = msg_id,
            text = response,
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_reaction = False,
            sender = '2348062233878@c.us',
            quoted_message = None,
            groupchat = cht
        ) 

def send_message2(message, response, cht):
    chatID = cht.chat_id
    if message == None:
        result = greenAPI.sending.sendMessage(chatID,response)
    else:
        result = greenAPI.sending.sendMessage(chatID,response,quotedMessageId=message.message_id)


if __name__ == "__main__":
    main()
