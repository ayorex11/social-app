from rest_framework import serializers
from .models import Chat, Message, ReadReceipts
from Profile.serializers import ProSerializer


class CreateMessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = ['body', 'replying_to']


class ChatSerializer(serializers.ModelSerializer):
	receiver = ProSerializer(many=False)

	class Meta:
		model = Chat
		exclue = ['sender',]

class MessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = '__all__'


class UpdateMessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = ['body',]