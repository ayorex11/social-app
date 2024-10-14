from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateMessageSerializer, ChatSerializer,MessageSerializer, UpdateMessageSerializer
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

	body = validated_data['body']
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

			chat.last_message = body
			chat.last_updated = date_created
			chat.messages.add(message)

			chat.save()

			chat2.last_message = body
			chat2.last_updated = date_created
			chat2.messages.add(message)

			chat2.save()

			data = {'message':'success',
					'data': serializer.data}

			return Response(data, status=status.HTTP_201_CREATED)

	except Exception as e:
		return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






					



