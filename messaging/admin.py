from django.contrib import admin
from .models import Message, ReadReceipts, Chat

admin.site.register(Message)
admin.site.register(ReadReceipts)
admin.site.register(Chat)