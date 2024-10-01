from rest_framework import serializers
from .models import Notification, CommentNotification

class NotificationSerializer(serializers.ModelSerializer):

	class Meta:
		model = Notification 
		exclude = ['profile',]

class CommentNotificationSerializer(serializers.ModelSerializer):

	class Meta:
		model = CommentNotification 
		exclude = ['profile',]