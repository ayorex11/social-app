from rest_framework import serializers
from .models import Chat, Message, ReadReceipts
from Profile.serializers import ProSerializer


class CreateMessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = ['encrypted_body', 'replying_to']


class ChatSerializer(serializers.ModelSerializer):
	receiver = ProSerializer(many=False)


	class Meta:
		model = Chat
		exclue = ['sender','messages']

class MessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = '__all__'


class UpdateMessageSerializer(serializers.ModelSerializer):

	class Meta:
		model = Message
		fields = ['encrypted_body',]

class ReadReceiptsSerializer(serializers.ModelSerializer):

	class Meta:
		model = ReadReceipts
		fields = ['read_receipts',]