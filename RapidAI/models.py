
import json
from django.db import models
import uuid

#class User(models.Model):
 #   chat_id = models.CharField(max_length=100)
 #   username = models.CharField(max_length=50)
  #  phone = models.CharField(max_length= 20)



class Private_chat(models.Model):
    access_token = models.UUIDField(primary_key=False,
        default=uuid.uuid4,
        editable=False)
    chat_id = models.CharField(max_length=100)
    is_subscribed = models.BooleanField(default=False)
    in_specialmode = models.BooleanField(default=False)
    news_category_wait = models.BooleanField(default=False)
    worldnews_category_wait = models.BooleanField(default=False)
    images = models.IntegerField(default= 0)
    text_requests = models.IntegerField(default= 0)
    
    #user = models.ForeignKey( User, on_delete=models.CASCADE, related_name= "chats" )

class Special_chat(models.Model):
    chat = models.OneToOneField(Private_chat,on_delete=models.CASCADE,related_name='special_chat', default=None, null= True)
    topic_wait = models.BooleanField(default=False)
    description_wait = models.BooleanField(default=False)
    chapters_wait = models.BooleanField(default=False)
    subtopics_wait = models.BooleanField(default=False)
    subtopics = models.CharField(max_length=500)
    words_count = models.CharField(max_length=500)
    choice_wait = models.BooleanField(default=False)
    subtopicsList_wait = models.BooleanField(default=False)

    words_count_wait = models.BooleanField(default=False)
    response_type_wait = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)


    def set_subtopics(self, x):
        self.subtopics = json.dumps(x)
    def get_subtopics(self):
        return json.loads(self.subtopics)

    def set_words_count(self, x):
        self.words_count = json.dumps(x)
    def get_words_count(self):
        return json.loads(self.words_count)



class Group(models.Model):
    chat_id = models.CharField(max_length=100)
    groupname = models.CharField(max_length=50)
    is_subscribed = models.BooleanField(default=True)
    news_category_wait = models.BooleanField(default=False)
    worldnews_category_wait = models.BooleanField(default=False)
    images = models.IntegerField(default= 0)
    text_requests = models.IntegerField(default= 0)
    


class Wmessage(models.Model):
    message_id = models.CharField(max_length=60)
    text = models.TextField(max_length=1000)
    date = models.DateTimeField()
    is_reaction = models.BooleanField()
    sender = models.CharField(max_length=100)
    sender_name = models.CharField(max_length=100, default='', null=True, blank=True)

    quoted_message = models.CharField(max_length=60, null=True, blank=True)
    groupchat = models.ForeignKey( Group, on_delete=models.CASCADE, null=True, blank=True, related_name= "messages" )
    chat = models.ForeignKey( Private_chat, on_delete=models.CASCADE, null=True, blank=True, related_name= "messages" )
    special_chat = models.ForeignKey( Special_chat, on_delete=models.CASCADE, null=True, blank=True, related_name= "messages" )
