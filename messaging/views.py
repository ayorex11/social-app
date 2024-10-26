from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateMessageSerializer, ChatSerializer,MessageSerializer, UpdateMessageSerializer, ReadReceiptsSerializer
from .models import Message, ReadReceipts, Chat
from Profile.models import Profile, follow_list, block_list 
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db import transaction


def check_block(profile, profile1):
	block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
	if block.exists():
		check_1 = True
	else:
		check_1 = False

	block_2 = block_list.objects.filter(profile=profile1, blocked_profile=profile)
	if block_2.exists():
		check_2 = True
	else:
		check_2 = False

	if check_1 == False and check_2 == False:
		return False
	else:
		return True



@swagger_auto_schema(methods=["POST"], request_body=CreateMessageSerializer())
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])

def send_message(request, username):
	user = request.user
	profile = get_object_or_404(Profile, user = user)
	profile1 = get_object_or_404(Profile, username=username)

	serializer = CreateMessageSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	validated_data = serializer.validated_data
	date_created = timezone.now()
	read = False

	body = validated_data['encrypted_body']
	try:
		with transaction.atomic():
			checkpoint = check_block(profile, profile1)
			if checkpoint == True:
				return Response({'message cannot be sent'}, status=status.HTTP_400_BAD_REQUEST)

			if profile1.private_account == True:
				follow = follow_list.objects.get(profile=profile1)
				if profile not in follow.followers.all():
					chat_1 = Chat.objects.filter(sender=profile1, receiver=profile)
					chat_2 = Chat.objects.filter(sender = profile, receiver=profile1)
					if not chat_1.exists() and not chat_2.exists():
						return Response({'you cannot start a chat with a private account'}, status=status.HTTP_400_BAD_REQUEST)

			chat, created = Chat.objects.get_or_create(sender=profile, receiver=profile1)
			chat2, created2 = Chat.objects.get_or_create(sender=profile1, receiver=profile)

			if "replying_to" in validated_data and validated_data["replying_to"]:
				if validated_data["replying_to"] not in chat.messages.all() and validated_data["replying_to"] not in chat2.messages.all():
					return Response({'replying to invalid message'}, status=status.HTTP_400_BAD_REQUEST)





			message = Message.objects.create(
									sender=profile,
									receiver = profile1,
									date_created=date_created,
									read=read,
									**validated_data)

			message.set_body(body)
			message.save()

			chat.last_message = message.encrypted_body
			chat.last_updated = date_created
			chat.messages.add(message)

			chat.save()

			chat2.last_message = message.encrypted_body
			chat2.last_updated = date_created
			chat2.messages.add(message)

			chat2.save()

			data = {'message':'success',
					'data': serializer.data}

			return Response(data, status=status.HTTP_201_CREATED)

	except Exception as e:
		return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_chats(request):
	user = request.user
	profile = get_object_or_404(Profile, user=user)

	chats = Chat.objects.filter(sender=profile).order_by('-last_updated') 
	decrypted_chats = []

	for chat in chats:
		decrypted_chats.append({
			'id' : chat.id,
			'receiver' : chat.receiver.username,
			'receiver_id' : chat.receiver.id,
			'last_message' : chat.get_body(),
			'last_updated' : chat.last_updated,
			'opened' : chat.opened
			})

	return Response(decrypted_chats, status=status.HTTP_200_OK)


					
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def open_chat(request, pk):
	user = request.user
	profile = get_object_or_404(Profile, user=user)

	chat = Chat.objects.get(id=pk)
	if profile != chat.sender:
		return Response({'message':'invalid request'}, status=status.HTTP_400_BAD_REQUEST)
	messages = []

	for ch in chat.messages.all():
		messages.append({
			'id': ch.id,
			'receiver': ch.receiver.username,
			'receiver_id': ch.receiver.id,
			'body': ch.get_body(),
			'date_created': ch.date_created,
			'read': ch.read,
			'replying_to': ch.replying_to.get_body() if ch.replying_to else None,
			'replying_to_id': ch.replying_to.id if ch.replying_to else None,
			})

	return Response(messages, status=status.HTTP_200_OK)



@swagger_auto_schema(methods=["PATCH"], request_body=UpdateMessageSerializer())
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])

def edit_message(request, pk):
	user  = request.user
	profile = get_object_or_404(Profile, user=user)

	message = Message.objects.get(id=pk)
	if message.sender != profile:
		return Response({'message':'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

	

	if timezone.now() - message.date_created > timedelta(days=1):
		return Response({'message':'message over a day cannot be edited'}, status=status.HTTP_400_BAD_REQUEST)

	else:
		serializer = UpdateMessageSerializer(message, data=request.data)
		serializer.is_valid(raise_exception=True)
		validated_data = serializer.validated_data
		body = validated_data['encrypted_body']
		message.set_body(body)
		message.save()
		data = {'message':'success',
				'data':body}

		return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=["PATCH"], request_body=ReadReceiptsSerializer())
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])

def edit_read_receipts(request):
	user  = request.user
	profile = get_object_or_404(Profile, user=user)

	message = ReadReceipts.objects.get(profile=profile)


	serializer = ReadReceiptsSerializer(message, data=request.data)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	validated_data = serializer.validated_data
	if validated_data['read_receipts'] == False:
		messages = Message.objects.filter(sender=profile)
		for me in messages:
			me.read = False
			me.save()

		messages2 = Message.objects.filter(receiver=profile)
		for mess in messages2:
			mess.read = False
			mess.save()

	else:
		messages = Message.objects.filter(sender=profile)
		for me in messages:
			me.read = True
			me.save()

		messages2 = Message.objects.filter(receiver=profile)
		for mess in messages2:
			mess.read = True
			mess.save()

	data = {'message':'success',
			'data':serializer.data}

	return Response(data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])

def mark_as_read(request, pk):

	user = request.user
	profile_test =  get_object_or_404(Profile, user=user)

	message = get_object_or_404(Message,id=pk)
	if message.sender == profile_test:
		return Response({'message':'You cannot mark your own message as read'}, status=status.HTTP_400_BAD_REQUEST)

	elif message.receiver != profile_test : 
		return Response({'message':'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

	else:
		read_receipt1 = get_object_or_404(ReadReceipts, profile=message.sender)
		read_receipt2 = get_object_or_404(ReadReceipts, profile=message.receiver)
		if read_receipt1.read_receipts == False or read_receipt2.read_receipts == False:
			message.read = False
			message.save()
			return Response({'message':'success'}, status=status.HTTP_200_OK)

		else:
			message.read = True
			message.save()
			return Response({'message':'success'}, status=status.HTTP_200_OK)