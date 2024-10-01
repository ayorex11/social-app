from django.contrib import admin
from .models import Notification, CommentNotification

admin.site.register(Notification)
admin.site.register(CommentNotification)
