from django.shortcuts import render
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CreatePostSerializer, PostSerializer, CreateCommentSerializer, CommentSerializer, LikeSerializer
from .models import Post, Comment, Like
from Profile.models import Profile
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils import timezone
from datetime import datetime
from notifs.models import CommentNotification
from django.db import transaction


@swagger_auto_schema(methods=["POST"], request_body=CreatePostSerializer())
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])

def create_post(request):
	user = request.user 
	profile = get_object_or_404(Profile, user=user)
	serializer = CreatePostSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	validated_data = serializer.validated_data

	first_name = profile.first_name
	last_name = profile.last_name
	likes = 0 
	comment_count = 0 
	date_created = timezone.now() 

	post = Post(profile=profile, first_name=first_name, last_name=last_name, likes=likes, comment_count=comment_count, date_created=date_created, **validated_data)
	post.save()
	data = {'message':'success',
			'data':serializer.data}
	return Response(data, status=status.HTTP_201_CREATED)




@swagger_auto_schema(methods=["POST"], request_body=CreateCommentSerializer())
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([FormParser, MultiPartParser])
def comment(request):
    user = request.user 
    profile = get_object_or_404(Profile, user=user)
    
    serializer = CreateCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    validated_data = serializer.validated_data
    first_name = profile.first_name
    last_name = profile.last_name
    likes = 0
    reply_count = 0 
    date_created = timezone.now()
    print(validated_data)
    
    post_id = validated_data['post']
    
    try:
        with transaction.atomic():
            post = get_object_or_404(Post, id=post_id)
            post.comment_count += 1
            
            if 'parent' in validated_data and validated_data['parent']:
                parent_id = validated_data['parent']
                comment = get_object_or_404(Comment, id=parent_id)
                comment.reply_count += 1
                comment.save()
                
                if profile != post.profile:
                	if post.profile != comment.profile:
	                    title = f"{profile} replied to a comment {comment.body} on your post {post.body} \n {validated_data['body']}"
	                    notif = CommentNotification(
	                        profile=post.profile,
	                        post=post,
	                        comment=comment,
	                        title=title,
	                        date_created=timezone.now(),
	                        read=False
	                    )
	                    notif.save()

                if profile != comment.profile:
                    title_2 = f"{profile} replied to your comment {comment.body} \n {validated_data['body']}"
                    notif_2 = CommentNotification(
                        profile=comment.profile,
                        post=post,
                        comment=comment,
                        title=title_2,
                        date_created=timezone.now(),
                        read=False
                    )
                    notif_2.save()
            else:
                if profile != post.profile:
                    title = f"{profile} replied to your post {post.body} \n {validated_data['body']}"
                    notif = CommentNotification(
                        profile=post.profile,
                        post=post,
                        title=title,
                        date_created=timezone.now(),
                        read=False
                    )
                    notif.save()

            post.save()

            new_comment = Comment(
                profile=profile,
                first_name=first_name,
                last_name=last_name,
                likes=likes,
                reply_count=reply_count,
                date_created=date_created,
                **validated_data
            )
            new_comment.save()
        
        data = {'message': 'success', 'data': serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


