from django.contrib import admin
from .models import Profile, follow_list

admin.site.register(Profile)
admin.site.register(follow_list)