from datetime import datetime
import time
from AIchat.models import Special_chat, Private_chat, Wmessage
from listener import send_message, send_message2
from RapidAPI import Message, Assistant
import sender
from whatsapp_api_client_python import API
import docx


ID_INSTANCE = '1101816615'
API_TOKEN_INSTANCE = 'ba2c3bd2272b4c9ca86eb87dc3f4967f44538c21a8844681b1'

greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)



def on_termpaper(privatechat,body):
    idMessage = body['idMessage']
    eventDate = datetime.fromtimestamp(body['timestamp'])
    senderData = body['senderData']
    messageData = body['messageData']

    special_chat, created = Special_chat.objects.get_or_create(chat= privatechat)
    if created:
        print('new special chat ......created')

    if messageData['typeMessage'] == 'textMessage' :
            text = messageData['textMessageData']['textMessage']
            
    elif messageData['typeMessage'] == 'extendedTextMessage' :
            text = messageData['extendedTextMessageData']['text']

    elif messageData['typeMessage'] == 'quotedMessage':
            text = messageData['extendedTextMessageData']['text']
    else: text =''

    if text.startswith('/exit'):
        Wmessage.objects.filter(special_chat= special_chat).delete()
        special_chat.delete()
        privatechat.in_specialmode = False
        privatechat.save()
        send_message2(None,'sucessfully canceled', privatechat)
        return None


    
    
    if special_chat.topic_wait:
        print('in topic wait')

        if messageData['typeMessage'] == 'textMessage' :
            topic = messageData['textMessageData']['textMessage']
            
        elif messageData['typeMessage'] == 'extendedTextMessage' :
            topic = messageData['extendedTextMessageData']['text']

        elif messageData['typeMessage'] == 'quotedMessage':
            topic = messageData['extendedTextMessageData']['text']
        else:
            send_message2(None,'enter a valid form of topic', privatechat)
            return None

        txt = f'pls, help me write a termpaper on the topic: {topic}'
        Wmessage.objects.create(
            message_id = idMessage,
            text = txt,
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_reaction = False,
            sender = senderData['sender'],
            quoted_message = None,
            special_chat = special_chat
        ).save()
        special_chat.topic_wait = False
        special_chat.chapters_wait = True
        special_chat.save()

        msg = 'pls enter the number of chapters you want'
        send_message(None,msg, privatechat)
       
    elif special_chat.chapters_wait:
        print('in chapters wait')
        if messageData['typeMessage'] == 'textMessage' :
            chpts = messageData['textMessageData']['textMessage']
            
        elif messageData['typeMessage'] == 'extendedTextMessage' :
            chpts = messageData['extendedTextMessageData']['text']

        elif messageData['typeMessage'] == 'quotedMessage':
            chpts = messageData['extendedTextMessageData']['text']
        else:
            msg = 'enter a valid number of chapters'
            send_message2(None,msg, privatechat)
            return None

        if chpts.isnumeric():
            txt = f'number of chapters should be {int(chpts)}'
            
            Wmessage.objects.create(
                message_id = idMessage,
                text = txt,
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                is_reaction = False,
                sender = senderData['sender'],
                quoted_message = None,
                special_chat = special_chat
            ).save()
            special_chat.chapters_wait = False
            special_chat.subtopics_wait = True
            special_chat.save()
            msg = 'explain how the subsections of each chapter will be. (example: chapter 1 will have 1 subsections, chapter 2 will ....)'
            send_message(None, msg, privatechat)
            
        else:
            msg = 'pls, enter a numeric value:'
            send_message2(None, msg, privatechat)



    elif special_chat.subtopics_wait:
        print('in subtopics wait')
        if messageData['typeMessage'] == 'textMessage' :
            detail = messageData['textMessageData']['textMessage']
            
        elif messageData['typeMessage'] == 'extendedTextMessage' :
            detail = messageData['extendedTextMessageData']['text']

        elif messageData['typeMessage'] == 'quotedMessage':
            detail = messageData['extendedTextMessageData']['text']
        else:
            send_message2(None,'enter a valid form of detailing', privatechat)
            return None

        txt = f'the details are: {detail}'
        Wmessage.objects.create(
            message_id = idMessage,
            text = txt,
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_reaction = False,
            sender = senderData['sender'],
            quoted_message = None,
            special_chat = special_chat
        ).save()

        #generating first table of contents
        messages = get_messages(special_chat)
        print(messages)
        toc = generate_toc(messages)
        
        result = greenAPI.sending.sendListMessage(privatechat.chat_id, toc['content'] , sender.choice_sections, title='Table of Contents', buttonText= 'Choose', footer='_Do you like it?_')
        #saving toc
        Wmessage.objects.create(
            message_id = result.data['idMessage'],
            text = toc['content'],
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_reaction = False,
            sender = '2348062233878@c.us',
            quoted_message = None,
            special_chat = special_chat
        ).save()

        special_chat.subtopics_wait = False
        special_chat.choice_wait = True
        special_chat.save()
        

    elif special_chat.choice_wait:
        print('in choice  wait')
        if messageData['typeMessage'] == 'listResponseMessage' :
            if messageData['listResponseMessage']['title'] == 'Yes':
                msg = 'Now, enter all the subsections in order and separated by commas. Eg 1.1,1.2,1.3,2.1,2.2,..... '
                send_message2(None, msg, privatechat)

                special_chat.choice_wait = False
                special_chat.subtopicsList_wait = True
                special_chat.save()
            elif messageData['listResponseMessage']['title'] == 'No':
                Wmessage.objects.filter(special_chat = special_chat).order_by('-date')[0].delete()
                #generating first table of contents
                messages = get_messages(special_chat)
                print(messages)
                toc = generate_toc(messages)
                
                
                result = greenAPI.sending.sendListMessage(privatechat.chat_id, toc['content'] , sender.choice_sections, title='Another Table of Contents', buttonText= 'Choose', footer='_Do you like it?_')
                #saving toc
                Wmessage.objects.create(
                    message_id = result.data['idMessage'],
                    text = toc['content'],
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    is_reaction = False,
                    sender = '2348062233878@c.us',
                    quoted_message = None,
                    special_chat = special_chat
                ).save()

            else: 
                msg = 'error, select an option or exit with /exit'
                send_message2(None, msg, privatechat)
            
        else:
            msg = 'select one of the options or exit with /exit'
            send_message2(None, msg, privatechat)

    elif special_chat.subtopicsList_wait:
        if messageData['typeMessage'] == 'textMessage' :
            subs = messageData['textMessageData']['textMessage']
            sublist = [str(x).strip() for x in str(subs).split(sep=',')]
            
            try:
                if all(isinstance(float(e), (int, float)) for e in sublist):
                    special_chat.set_subtopics(sublist)
                    special_chat.save()
            except: 
                msg = 'use only numbers and dot(.)'
                send_message2(None, msg, privatechat)
                return None
            special_chat.subtopicsList_wait = False
            special_chat.words_count_wait = True
            special_chat.save()

            msg = 'enter word count for each subtopic in the format: 1000,500,600,....  it must have same length as number of subtopics'
            send_message2(None, msg, privatechat)



        else:
            msg = 'use simple text (1.1,1.2,2.1,...)'
            send_message2(None, msg, privatechat)
            return None


    elif special_chat.words_count_wait:
        if messageData['typeMessage'] == 'textMessage' :
            counts = messageData['textMessageData']['textMessage']
            
            try:
                wordCountlist = [int(x.strip()) for x in counts.split(sep=',')]
                sbtps= special_chat.get_subtopics()
                if len(wordCountlist) == len(sbtps):
                    special_chat.set_words_count(wordCountlist)
                else: 
                    msg = 'the words count must be same number of subtopics'
                    send_message2(None, msg, privatechat)
                    return None
            except: 
                msg = 'use only integers'
                send_message2(None, msg, privatechat)
                return None
            
            msg = 'there are two forms of response: as a microsoft doc file or as normal whatsapp message'
            result = greenAPI.sending.sendListMessage(privatechat.chat_id, msg , sender.response_choice_sections, title='response format', buttonText= 'Choose', footer='')

            special_chat.words_count_wait = False
            special_chat.response_type_wait = True
            special_chat.save()


        else:
            msg = 'use simple text (1000,500,700,...)'
            send_message2(None, msg, privatechat)
            return None
        
    elif special_chat.response_type_wait:
        messages = get_messages(special_chat)
        data = dict(zip(special_chat.subtopics, special_chat.words_count))
        if messageData['typeMessage'] == 'listResponseMessage' :
            if messageData['listResponseMessage']['title'] == 'as doc file':
                file = write_doc(special_chat)
                print('file is' + file)
                result = greenAPI.sending.sendFileByUpload(privatechat.chat_id, file, fileName='document')
                Wmessage.objects.filter(special_chat= special_chat).delete()
                privatechat.in_specialmode = False
                privatechat.save()
                send_message2(None, '_termpaper mode terminated_', privatechat)
            elif messageData['listResponseMessage']['title'] == 'whatsapp text':
                pass

            else: 
                msg = 'error, select an option or exit with /exit'
                send_message2(None, msg, privatechat)
            
        else:
            msg = 'select one of the options or exit with /exit'
            send_message2(None, msg, privatechat)
    elif special_chat.is_done:
        pass
    else:
        message = 'pls enter topic:'
        send_message(None,message,privatechat)
        special_chat.topic_wait = True
        special_chat.save()
        print(special_chat.topic_wait)

def get_messages(chat):
    messags = Wmessage.objects.filter(special_chat = chat).order_by('-date')
    messages = []

    #get last 50 special messeges
    for mes in messags:
        if mes.sender == '2348062233878@c.us':
            x = Message('assistant', mes.text + '\n')
            messages.append(x.message())
        else:
            x = Message('user', mes.text + '\n')
            messages.append(x.message())


    messages.reverse()
    return messages

def generate_toc(messages):
    system_prompt = '''you are a very smart project and termpaper writing assistant. write a nice table of contents for the student. stricly take note of the number of chapters and subsections the user wants. put the subsections in float numbers. the chat is:'''

    sys_message = Message('system', system_prompt).message()
    messages.insert(0,sys_message)
    conversation = Assistant()
    response_msg = conversation.ask_assistant(messages)
    return response_msg

def write_doc(special_chat):
    data = dict(zip(special_chat.get_subtopics(), special_chat.get_words_count()))
    system_prompt = '''you are a very smart project and termpaper writing assistant. write the said subsection in the given words count.if it is the first subsection of a chapter, then introduce the chapter briefly before writing the subsection. use headings and subheadings for chapters and subsections and also avoid additional comments. the chat is:'''
    text = []

    for key,value in data.items():
        print('gettng for  ' + key)
        send_message2(None, 'writing section:' + key, special_chat.chat)
        messages = get_messages(special_chat)
        sys_message = Message('system', system_prompt).message()
        add_message = Message('user', f'write section {key} in {str(value)} words').message()
        messages.insert(0,sys_message)
        messages.append(add_message)
        conversation = Assistant()
        response_msg = conversation.ask_assistant(messages)
        try:
            text.append(response_msg['content'])
        except:
            try:
                time.sleep(10)
                print('gettng for  ' + key)
                messages = get_messages(special_chat)
                sys_message = Message('system', system_prompt).message()
                add_message = Message('user', f'write section {key} in {str(value)} words').message()
                messages.insert(0,sys_message)
                messages.append(add_message)
                conversation = Assistant()
                response_msg = conversation.ask_assistant(messages)
                text.append(response_msg['content'])
            except: break


    doc = docx.Document()
    for x in text:
        doc.add_paragraph(x)
    doc.save('documents/'+ special_chat.chat.chat_id + str(special_chat.id) +'.docx')
    send_message2(None, 'Done, ensure to edit the file', special_chat.chat)
    return 'documents/'+ special_chat.chat.chat_id + str(special_chat.id) +'.docx'

    



