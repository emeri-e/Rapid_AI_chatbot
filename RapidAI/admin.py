

# Register your models here.
from django.contrib import admin
from .models import Wmessage, Group


class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "text","date","groupchat",)

class GroupAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "news_category_wait","worldnews_category_wait","images","text_requests","is_subscribed",)
    




admin.site.register(Wmessage, MessageAdmin)
admin.site.register(Group, GroupAdmin)