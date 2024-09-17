from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,authentication_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, MiniProfileSerializer, FollowerSerializer, FollowingSerializer
from .models import Profile, follow_list
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from datetime import datetime


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
	serializer.save(user=request.user)
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