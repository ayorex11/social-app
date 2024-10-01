from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,authentication_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, MiniProfileSerializer, FollowerSerializer, FollowingSerializer, PrivateAccountSerializer, PendingListSerializer, BlockListSerializer
from .models import Profile, follow_list, pending_list, block_list
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from datetime import datetime
from notifs.models import Notification


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_profile(request):
	user=request.user
	try:
		profile = Profile.objects.get(user=user)
	except:
		profile = Profile.objects.create(user= user, first_name=user.first_name, last_name=user.last_name, username=user.username)
	serializer=ProfileSerializer(profile, many=False)
	data={'message':'success',
		'data':serializer.data}
	return Response(data, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=["PATCH"], request_body=ProfileSerializer())
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])

def update_profile(request):
	user = request.user
	profile = get_object_or_404(Profile, user=user)
	serializer = ProfileSerializer(profile, data=request.data)
	serializer.is_valid(raise_exception=True)
	serializer.save(user=user)
	data = {'message': 'success',
			'data':serializer.data}
	pro = Profile.objects.get(user=user)
	if user.username.lower() != pro.username.lower():
		user.username = pro.username
		user.save()
	else:
		pass
	return Response (data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def search(request, username):
	try:
		profile = Profile.objects.get(username=username)
	except Profile.DoesNotExist:
		raise Http404
	serializer = MiniProfileSerializer(profile, many=False)
	data = {
		'message':'success',
		'data': serializer.data
	}
	return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def view_profile(request, pk):
	try:
		profile = Profile.objects.get(id=pk)
	except Profile.DoesNotExist:
		raise Http404
	serializer = ProfileSerializer(profile, many=False)
	data = {
		'message': 'success',
		'data': serializer.data
	}
	return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def view_my_followers(request):
	user = request.user
	profil = Profile.objects.get(user=user)
	follow = follow_list.objects.get(profile=profil)
	serializer = FollowerSerializer(follow, many=False)
	data = {
		'message': 'success',
		'data': serializer.data
	}
	return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def view_following(request):
	user = request.user
	profil = Profile.objects.get(user=user)
	follow = follow_list.objects.get(profile=profil)
	serializer = FollowingSerializer(follow, many=False)
	data = {
		'message': 'success',
		'data': serializer.data
	}
	return Response(data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def make_private(request):
	user = request.user
	profile = get_object_or_404(Profile, user=user)
	if profile.private_account == True:
		return Response({'account is already private'}, status=status.HTTP_400_BAD_REQUEST)
	profile.private_account = True
	profile.save()
	serializer = PrivateAccountSerializer(profile, many=False)
	data = {'message':'success',
			'serializer': serializer.data}
	return Response(data, status=status.HTTP_200_OK)



@swagger_auto_schema(methods=["PATCH"], request_body=PrivateAccountSerializer())
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unmake_private(request):
	user = request.user
	profile = get_object_or_404(Profile, user=user)
	if profile.private_account == False:
		return Response({'account is not private'}, status=status.HTTP_400_BAD_REQUEST)
	profile.private_account = False
	profile.save()
	serializer = PrivateAccountSerializer(profile, many=False)
	data = {'message':'success',
			'serializer': serializer.data}
	return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def follow(request, username):
	user = request.user
	followers_profile = get_object_or_404(Profile, user=user)
	followee_profile = get_object_or_404(Profile, username=username)
	followee = follow_list.objects.get(profile=followee_profile)

	block = block_list.objects.filter(profile=followers_profile, blocked_profile=followee_profile)
	if block.exists():
		return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

	block_lists = block_list.objects.filter(profile=followee_profile, blocked_profile=followers_profile)
	if block_lists.exists():
		return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)

	if followers_profile in followee.followers.all():
		return Response({'Already Following '}, status=status.HTTP_400_BAD_REQUEST)

	if followee_profile.private_account == True:
		if pending_list.objects.filter(profile=followee_profile, pending_follower=followers_profile).exists():
			return Response({'follow request sent'}, status=status.HTTP_400_BAD_REQUEST)
		pending = pending_list(profile=followee_profile, pending_follower=followers_profile)
		pending.save()
		title = 'New follow request'
		body = f'You have a new follow request from {followers_profile}'
		date_created = datetime.now()
		read = False
		notifs = Notification(profile=followee_profile, title=title, body=body, date_created=date_created, read=read)
		notifs.save()
		return Response({'your follow request is pending'}, status=status.HTTP_200_OK)
		



	followee.followers.add(followers_profile)
	followee_profile.save()

	followee_profile.followers_count += 1

	follower = follow_list.objects.get(profile=followers_profile)
	follower.following.add(followee_profile)
	followers_profile.following_count +=1
	followers_profile.save()

	title = 'You have a new follower'
	body = f'{followers_profile} just followed you.'
	date_created = datetime.now()
	read = False
	notifs = Notification(profile=followee_profile, title=title, body=body, date_created=date_created, read=read)
	notifs.save()

	return Response({f'You have followed {followee_profile} successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def unfollow(request, username):
	user = request.user
	followers_profile = get_object_or_404(Profile, user=user)
	followee_profile = get_object_or_404(Profile, username=username)

	followee = follow_list.objects.get(profile=followee_profile)
	if followers_profile not in followee.followers.all():
		return Response({'Not following '}, status=status.HTTP_400_BAD_REQUEST)
	followee.followers.remove(followers_profile)
	followee_profile.followers_count -= 1
	followee_profile.save()


	follower = follow_list.objects.get(profile=followers_profile)
	follower.following.remove(followee_profile)
	followers_profile.following_count -=1
	followers_profile.save()

	if followee_profile.private_account == True:
		return Response({f'You have unfollowed {followee_profile} successfully. You will need to be aproved to follow again'},
		 status=status.HTTP_200_OK)

	else :
		return Response({f'You have unfollowed {followee_profile} successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_pending_list(request):
	user = request.user 
	profile = get_object_or_404(Profile, user=user)
	if profile.private_account == False:
		return Response({'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)

	pending = pending_list.objects.filter(profile=profile)
	serializer = PendingListSerializer(pending, many=True)

	data = {'message':'success',
			'data': serializer.data}

	return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def approve(request, pk):
	user = request.user 
	profile = get_object_or_404(Profile, user=user)
	if profile.private_account == False:
		return Response({'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
	pending = pending_list.objects.get(id=pk)
	follower = pending.pending_follower
	profil = follow_list.objects.get(profile=profile)
	profil.followers.add(follower)
	profile.followers_count += 1
	profile.save()

	follower_profile = follow_list.objects.get(profile=follower)
	follower_profile.following.add(profile)
	follower.following_count += 1
	follower.save()
	pending.delete()
	#notification
	title = 'Your follow request has been approved'
	body = f'Your follow request sent to {profile} has been approved'
	date_created = datetime.now()
	read = False
	notifs = Notification(profile=follower, title=title, body=body, date_created=date_created, read=read)
	notifs.save()

	return Response({'message': 'success'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def disapprove(request, pk):
	user = request.user 
	profile = get_object_or_404(Profile, user=user)
	if profile.private_account == False:
		return Response({'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
	pending = pending_list.objects.get(id=pk)
	pending.delete()

	return Response({'message': 'success'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def block_user(request, username):
	user = request.user
	#me 
	user_blocking = get_object_or_404(Profile, user=user)
	#you
	user_blocked = get_object_or_404(Profile, username=username)

	#me
	blocker = follow_list.objects.get(profile = user_blocking)
	#you
	blockee = follow_list.objects.get(profile = user_blocked)
	
	block_lists = block_list.objects.filter(profile=user_blocking, blocked_profile=user_blocked)
	if block_lists.exists():
		return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)
	#if i am following you
	if user_blocking in blockee.followers.all():
		#and you are following me
		if user_blocked in blocker.followers.all():
			blockee.followers.remove(user_blocking)
			blocker.followers.remove(user_blocked)

			blocker.following.remove(user_blocked)
			blockee.following.remove(user_blocking)

			user_blocking.following_count -= 1
			user_blocking.followers_count -= 1
			user_blocking.save()

			user_blocked.following_count -= 1
			user_blocked.followers_count -= 1
			user_blocked.save()

			block = block_list(profile=user_blocking, blocked_profile=user_blocked)
			block.save()

			return Response({'user successfully blocked'}, status=status.HTTP_200_OK)

		blocker.following.remove(user_blocked)
		user_blocking.following_count -= 1
		user_blocking.save()

		blockee.followers.remove(user_blocking)
		user_blocked.followers_count -= 1
		user_blocked.save()

		block = block_list(profile=user_blocking, blocked_profile=user_blocked)
		block.save()

		return Response({'user successfully blocked'}, status=status.HTTP_200_OK)
	#if you are following me
	elif user_blocked in blocker.followers.all():
		blocker.followers.remove(user_blocked)
		user_blocking.followers_count -= 1
		user_blocking.save()

		blockee.following.remove(user_blocking)
		user_blocked.following_count -= 1
		user_blocked.save()
		block = block_list(profile=user_blocking, blocked_profile=user_blocked)
		block.save()

		return Response({'user successfully blocked'}, status=status.HTTP_200_OK)
	# we are not following each other
	else:
		block = block_list(profile=user_blocking, blocked_profile=user_blocked)
		block.save()

		return Response({'user successfully blocked'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def unblock(request, username):

	user = request.user

	blocker = get_object_or_404(Profile, user=user)
	blocked = get_object_or_404(Profile, username=username)

	block = block_list.objects.filter(profile=blocker, blocked_profile=blocked)
	if block.exists():
		block.delete()
		return Response({'user successfully unblocked'}, status=status.HTTP_200_OK)

	return Response({'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_block_list(request):
	user = request.user

	blocker = get_object_or_404(Profile, user=user)

	block = block_list.objects.filter(profile=blocker)

	serializer = BlockListSerializer(block, many=True)

	data = {'message':'success',
			'data':serializer.data}
	return Response(data, status=status.HTTP_200_OK)
