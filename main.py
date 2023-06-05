#from typing import Final
import os
import django

from image import generate_img



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rapid_tele.settings')
django.setup()

import json
from datetime import datetime
import threading
from RapidAI.models import Wmessage, Private_chat, Group, Special_chat
from datetime import datetime
from django.shortcuts import get_object_or_404
from RapidAPI import Message, Assistant
import openai
from news import get_headlines
from asgiref.sync import sync_to_async



from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

def init_api():
    with open(".env") as env:
        for line in env:
            key,value=line.strip().split("=")
            os.environ[key]=value

init_api()
print('Starting up bot...')

openai.api_key = os.environ.get('OPEN_API_KEY')
TOKEN =os.environ.get('TELE_TOKEN')
BOT_USERNAME = '@Rapid_AI_bot'


# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')


# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')

@sync_to_async
def filter_message(group):
    msgs = Wmessage.objects.filter(groupchat=group).order_by('-date')[:10]
    return msgs

@sync_to_async
def filter_message_p(chat, all = False):
    if all:
        msgs = Wmessage.objects.filter(chat=chat).order_by('-date') 
        return msgs

    msgs = Wmessage.objects.filter(chat=chat).order_by('-date')[:10]
    return msgs

@sync_to_async
def delete_message(id):
    Wmessage.objects.filter(message_id = id).delete()

@sync_to_async
def check(msgs):
    return len(msgs) == 25
@sync_to_async
def delete_messages(p_chat):
    Wmessage.objects.filter(chat = p_chat).delete()

@sync_to_async
def get_messages(messags):
    messages = []

    #get last 50 group messeges
    for mes in messags:
        if mes.sender_name == 'Rapid_AI_bot':
            x = Message('assistant', mes.text + '\n')
            messages.append(x.message())
        else:
            x = Message('user', mes.text + '\n')
            messages.append(x.message())
    return messages

@sync_to_async
def save_message(chat, message):
    if message.chat.type == 'supergroup':
        Wmessage.objects.create(
                message_id = message.message_id,
                text = message.text,
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                is_reaction = False,
                sender = message.from_user.id,
                sender_name = message.from_user.username,
                quoted_message = None,
                groupchat = chat
            ).save()
    else:
        Wmessage.objects.create(
                message_id = message.message_id,
                text = message.text,
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                is_reaction = False,
                sender = message.from_user.id,
                sender_name = message.from_user.username,
                quoted_message = None,
                chat = chat
            ).save()

def query(text: str) -> str:
    system_prompt = ''' you are a brilliant assistant. provide insightfull and very brief responses '''
    msgx = text.replace('/query','').replace(BOT_USERNAME, '')
    sys_message = Message('system', system_prompt).message()
    messages = []

    msg = Message('user', msgx).message()
    messages.append(sys_message)
    messages.append(msg)
    conversation = Assistant()
    response_msg = conversation.ask_assistant(messages)
    return response_msg['content']

def contrib(messages, is_group = True):
    if is_group:
        system_prompt = '''your name is Rapid made by Daniel eze.you a sarcastic, very funny and most importantly very concise whatsapp group bot. note that the last statement was addressed to you. also be very brief and also use whatsapp emojis to express you self. the last group messages are: '''
    else:
        system_prompt = '''your name is rapid made by Daniel eze.you a smart personal assistant. use enough whatsapp stickers when necessary. the last messages are: '''

    sys_message = Message('system', system_prompt).message()
    messages.insert(0,sys_message)
    conversation = Assistant()
    
    
    try:
        response_msg = conversation.ask_assistant(messages)
        response_message = response_msg['content'].lower().replace('as an ai language model','').replace("i'm sorry,","").replace('as i am an ai language model','').replace("i am sorry","").replace('is there anything else i can assist you with?','').replace('is there anything else i can help you with?','')
    except:
        response_message = 'oops an error occured'
    return response_message
def handle_response(text: str) -> str:
    # Create your own response logic
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good!'

    if 'i love python' in processed:
        return 'Remember to subscribe!'

    return 'I don\'t understand'
@sync_to_async
def get_or_create_group(chat_id):
    return Group.objects.get_or_create(chat_id=chat_id)

@sync_to_async
def get_or_create_chat(chat_id):
    return Private_chat.objects.get_or_create(chat_id=chat_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text
    # Print a log for debugging
    '''print(message_type)
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')'''

    # React to group messages only if users mention the bot directly
    if message_type == 'supergroup':
        group, created = await get_or_create_group(update.message.chat.id)
        if created:
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
            await update.message.reply_text(first_group_msg)
            print('new group\t  -------created')
            return
            
            
        #check if it is news category selection
        if group.news_category_wait:
            category = text.strip().lower()
            group.news_category_wait = False
            threading.Thread(target= group.save).start()
            await get_headlines(category,update)
            await delete_message(update.message.message_id)
            return None

        if group.worldnews_category_wait:
            category = text.strip().lower()
            group.worldnews_category_wait = False
            threading.Thread(target= group.save).start()
            await get_headlines(category,update,country=None)
            await delete_message(update.message.message_id)
            return None


        # save message to database function
        await save_message(group,update.message)
        

        # Replace with your bot username
        if BOT_USERNAME in text or (update.message.reply_to_message and update.message.reply_to_message.from_user.username == 'Rapid_AI_bot'):
            if len(text)< 400:

        
                messags = await filter_message(group)
            

                messages = await get_messages(messags)
                messages.reverse()
                print(messages)

                last_content = messages[-1]['content'].replace(BOT_USERNAME,"hey Rapid ")
                messages.pop()
                messages.append({'role':'user', 'content': last_content})
        

                
                
                if '/query' in text:
                    response = query(text)
                    
                elif '/image' in text:
                    try:
                        prompt = text.replace('/image','')
                        file = generate_img(prompt,update.message)
                        await update.message.reply_photo(file, reply_to_message_id= update.message.message_id)
                        await delete_message(update.message.message_id)
                        return
                    except:
                        resp= 'oops, server is busy. Try again later' 
                        await update.message.reply_text(resp)
                        await delete_message(update.message.message_id)
                        return
                elif text.startswith('/news'):      
                    button_labels = [['general'],['science'],['entertainment'],['health'],['business'],['technology'],['sports']]

                    # Create a ReplyKeyboardMarkup object with the button labels
                    reply_markup = ReplyKeyboardMarkup(button_labels, resize_keyboard=True)

                    # Send a message with the buttons
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='_Note that this is for 9ja news. Use /worldnews for world news_ \nChoose an option:', reply_markup=reply_markup)
                    await delete_message(update.message.message_id)
                    group.news_category_wait = True
                    threading.Thread(target= group.save).start()
                    
                    return None
                elif text.startswith('/worldnews'):
                    button_labels = [['general'],['science'],['entertainment'],['health'],['business'],['technology'],['sports']]

                    # Create a ReplyKeyboardMarkup object with the button labels
                    reply_markup = ReplyKeyboardMarkup(button_labels, resize_keyboard=True)

                    # Send a message with the buttons
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='_Note that this is for world news news. Use /news for 9ja news_ \nChoose an option:', reply_markup=reply_markup)
                    await delete_message(update.message.message_id)
                    group.worldnews_category_wait = True
                    threading.Thread(target= group.save).start()
                    return None
                
                
                else:
                    response = contrib(messages)
                    
            else:
                resp = 'if you want me to read your long text, use the private assistant '
                await update.message.reply_text(resp)
                await delete_message(update.message.message_id)
                return

        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    
        print('Bot:', response)
        sent = await update.message.reply_text(response)
        await save_message(group, sent)
    else:
        private_chat, created = await get_or_create_chat(update.message.chat.id)

        if created:
            #send first message to client
            first_msg = 'Welcome, I am Rapid! Your A.I powered companion on Whatsapp!\n💬 Ask me about anything, 🍔Recipes, ✈️Travelling, 🏋️‍♀️Fitness,📱Marketing, really.. anything, in any language!\n*Functionalities*\n⭐️Use  /clear 👉 In case Rapid  is not responding in the best way, you can clear the context of a conversation and start over\n🔐/setaccess _access token_ 👉 use this function to subscribe. chat up 07064950025 to get _access token_\n🌃 /image TEXT 👉 Generate an image based on TEXT , the more detail the better\n🌃 /image_var TEXT 👉 send along with an image to generate a variation of the image. sent image must be less than 4MB\n🫴/help  this provides you with helpful informations\n😄/termplates  👉  this provides you with helpful termplates for performing certain tasks like termpaper writing, videoscripts, blog etc and guess what?  ..it can even return your work as microsoft document🤓\n📰/news _topic_ 👉 returns some current news on the _topic_\n🌎/worldnews 👉 to get top 5 world news\n🎤 Audio Messages 👉 You can ask whatever you want using audio messages in any language\n*Note: I can also make mistakes*'
            await update.message.reply_text(first_msg)
            print('new chat\t  -------created')
            return None

        
        if private_chat.in_specialmode:
            #my_function(private_chat,update)
            return None

        if private_chat.news_category_wait:
            category = text.strip().lower()
            private_chat.news_category_wait = False
            threading.Thread(target= private_chat.save).start()
            await get_headlines(category,update)
            await delete_message(update.message.message_id)
            return None

        if private_chat.worldnews_category_wait:
            category = text.strip().lower()
            private_chat.worldnews_category_wait = False
            threading.Thread(target= private_chat.save).start()
            await get_headlines(category,update,country=None)
            await delete_message(update.message.message_id)
            return None

        
        #save message to data base
        await save_message(private_chat, update.message)

        if len(text)< 120 or private_chat.is_subscribed:
            
            if private_chat.is_subscribed:
                messags = await filter_message_p(private_chat, all= True)
                checked = await check(messags)
                if checked:
                    txt = 'use the /clear function to clear the database and have better response'
                    await update.message.reply_text(txt)
                

            else:
                messags = await filter_message_p(private_chat)
            
            
            messages = await get_messages(messags)
            messages.reverse()
            print(messages)

            if text.startswith('/image'):
                if private_chat.is_subscribed:
                    prompt = text.replace('/image','')
                    try:
                        prompt = text.replace('/image','')
                        file = generate_img(prompt,update.message)
                        await update.message.reply_photo(file, reply_to_message_id= update.message.message_id)
                        await delete_message(update.message.message_id)
                        return
                    except:
                        resp= 'oops, server is busy. Try again later' 
                        await update.message.reply_text(resp)
                        await delete_message(update.message.message_id)
                        return
                else: 
                    msg = 'subscribe to generate image from text. To get your acces token, chat up 07064950025'
                    await update.message.reply_text(msg)
                    await delete_message(update.message.message_id)
                    return

            elif text.startswith('/news'):      
                    button_labels = [['general'],['science'],['entertainment'],['health'],['business'],['technology'],['sports']]

                    # Create a ReplyKeyboardMarkup object with the button labels
                    reply_markup = ReplyKeyboardMarkup(button_labels, resize_keyboard=True)

                    # Send a message with the buttons
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='_Note that this is for 9ja news. Use /worldnews for world news_ \nChoose an option:', reply_markup=reply_markup)
                    await delete_message(update.message.message_id)
                    private_chat.news_category_wait = True
                    threading.Thread(target= private_chat.save).start()
                    
                    return None
            elif text.startswith('/worldnews'):
                    button_labels = [['general'],['science'],['entertainment'],['health'],['business'],['technology'],['sports']]

                    # Create a ReplyKeyboardMarkup object with the button labels
                    reply_markup = ReplyKeyboardMarkup(button_labels, resize_keyboard=True)

                    # Send a message with the buttons
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='_Note that this is for world news news. Use /news for 9ja news_ \nChoose an option:', reply_markup=reply_markup)
                    await delete_message(update.message.message_id)
                    private_chat.worldnews_category_wait = True
                    threading.Thread(target= private_chat.save).start()
                    return None
                
            elif text.startswith('/clear'):
                await delete_messages(private_chat)
                msg = 'Done. You are as good as new'
                await update.message.reply_text(msg)
                return
                
            elif text.startswith('/setaccess'):
                accessT = text.replace('/setaccess','').strip()
                if accessT == str(private_chat.access_token):
                    private_chat.is_subscribed = True
                    threading.Thread(target= private_chat.save).start()
                    mesg = 'you are successfully subscribed. enjoy full functionality!!!'
                    await update.message.reply_text(mesg)
                    await delete_message(update.message.message_id)
                    return
                    
                elif update.message.from_user.username == 'Real_Daniels':
                    #print(private_chat.access_token)
                    private_chat.is_subscribed = True
                    threading.Thread(target= private_chat.save).start()
                    mesg = 'you are successfully subscribed. enjoy full functionality!!!'
                    await update.message.reply_text(mesg)
                    return
                else:
                    mesg = 'wrong access token. Try again or get your access token by chatting up 07064950025'
                    await update.message.reply_text(mesg)
                    await delete_message(update.message.message_id)
                    return
            else:
                    response = contrib(messages, is_group= False)
                    sent = await update.message.reply_text(response)
                    await save_message(private_chat, sent)
                    return
            

        


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    #app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=2)
