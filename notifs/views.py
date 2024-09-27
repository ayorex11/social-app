from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from .models import Notification
from Profile.models import Profile
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_notifications(request):
	user = request.user
	profile = get_object_or_404(Profile, user=user)
	notifs = Notification.objects.filter(profile=profile)
	serializer = NotificationSerializer(notifs, many=True)

	data = {'message': 'success',
			'data': serializer.data}

	return Response(data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])

def mark_as_read(request, pk):
	user = request.user
	profile = get_object_or_404(Profile, user=user)
	notif = Notification.objects.get(id=pk)
	if notif.profile != profile:
		return response({'message': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

	notif.read = True
	notif.save()
	return Response({'message': 'success'}, status=status.HTTP_200_OK)
