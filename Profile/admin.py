from django.contrib import admin
from .models import Profile, follow_list, pending_list, block_list

admin.site.register(Profile)
admin.site.register(follow_list)
admin.site.register(pending_list)
admin.site.register(block_list)