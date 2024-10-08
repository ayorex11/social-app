from django.shortcuts import render
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CreatePostSerializer, PostSerializer, CreateCommentSerializer, CommentSerializer, LikeSerializer, CommentLikeSerializer
from .models import Post, Comment, Like, CommentLike
from Profile.models import Profile, follow_list, block_list 
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils import timezone
from datetime import datetime, timedelta, date
from notifs.models import CommentNotification, Notification
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
            profile1 = post.profile


            block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
            if block.exists():
                return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

            block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
            if block_lists.exists():
                return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)



            follow_check = get_object_or_404(follow_list, profile=profile1)
            if profile1.private_account == True and profile != profile1:
                if profile not in follow_check.followers.all():
                    return Response({'message':'Not following Private Account.'}, status=status.HTTP_400_BAD_REQUEST)
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




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    try:
        with transaction.atomic():
            post = get_object_or_404(Post, id=pk)
            profile1 = post.profile


            block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
            if block.exists():
                return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

            block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
            if block_lists.exists():
                return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)



            follow_check = get_object_or_404(follow_list, profile=profile1)
            if profile1.private_account == True and profile != profile1:
                if profile not in follow_check.followers.all():
                    return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)

            
            like, created = Like.objects.get_or_create(post=post)
            if profile in like.people.all():
                return Response({'message': 'Post already liked'}, status=status.HTTP_400_BAD_REQUEST)
            like.people.add(profile)
            post.likes += 1
            post.save()

        
            title = 'Your post has received a new like'
            body = f'Your post "{post.body}" has been liked by {profile}'
            date_created = timezone.now() 
            read = False

            if profile != profile1:
                notif = Notification(
                    profile=profile1,
                    title=title,
                    body=body,
                    date_created=date_created,
                    read=read
                )
                notif.save()
            else:
                pass 

            data = {'message': 'success'}
            return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_likes(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    post = get_object_or_404(Post, id=pk)
    profile1 = post.profile

    block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
    if block.exists():
        return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

    block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
    if block_lists.exists():
        return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


    follow_check = get_object_or_404(follow_list, profile=profile1)
    if profile1.private_account == True and profile != profile1:
        if profile not in follow_check.followers.all():
            return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)
    likes, created = Like.objects.get_or_create(post=post)
    serializer = LikeSerializer(likes, many=False)
    data = {'message':'success',
            'data': serializer.data}

    return Response(data, status=status.HTTP_200_OK)


			
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_comment(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    try:
        with transaction.atomic():
            comment = get_object_or_404(Comment, id=pk)
            print(f"Retrieved Comment: {comment}")
            profile1 = comment.profile

            block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
            if block.exists():
                return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

            block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
            if block_lists.exists():
                return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


            follow_check = get_object_or_404(follow_list, profile=profile1)
            if profile1.private_account == True and profile!=profile1:
                if profile not in follow_check.followers.all():
                    return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)

            
            like, created = CommentLike.objects.get_or_create(comment=comment)
            if profile in like.people.all():
                return Response({'message':'Comment already liked'}, status=status.HTTP_400_BAD_REQUEST)

            like.people.add(profile)
            comment.likes += 1
            comment.save()

            
            title = 'Your comment has received a new like'
            body = f'Your comment "{comment.body}" has been liked by {profile}'
            date_created = timezone.now() 
            read = False

            if profile != profile1:
                notif = Notification(
                    profile=profile1,
                    title=title,
                    body=body,
                    date_created=date_created,
                    read=read
                )
                notif.save()
            else:
                pass 

            data = {'message': 'success'}
            return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comment_likes(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    comment = get_object_or_404(Comment, id=pk)
    profile1 = comment.profile

    block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
    if block.exists():
        return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

    block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
    if block_lists.exists():
        return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


    follow_check = get_object_or_404(follow_list, profile=profile1)
    if profile1.private_account == True and profile!=profile1:
        if profile not in follow_check.followers.all():
            return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)
    likes, created = CommentLike.objects.get_or_create(comment=comment)
    serializer = CommentLikeSerializer(likes, many=False)
    data = {'message':'success',
            'data': serializer.data}

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    try:
        with transaction.atomic():

            post = get_object_or_404(Post, id=pk)
            profile1 = post.profile

            block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
            if block.exists():
                return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

            block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
            if block_lists.exists():
                return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)



            follow_check = get_object_or_404(follow_list, profile=profile1)
            if profile1.private_account == True and profile!=profile1:
                if profile not in follow_check.followers.all():
                    return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)
            like, created = Like.objects.get_or_create(post=post)
            if profile not in like.people.all():
                return Response({'message': 'Post not previously liked'}, status=status.HTTP_400_BAD_REQUEST)
            post.likes -= 1
            post.save()

            like.people.remove(profile)


            data = {'message': 'success'}
            return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_comment(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    try:
        with transaction.atomic():

            comment = get_object_or_404(Comment, id=pk)
            profile1 = comment.profile

            block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
            if block.exists():
                return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

            block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
            if block_lists.exists():
                return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


            follow_check = get_object_or_404(follow_list, profile=profile1)
            if profile1.private_account == True and profile!=profile1:
                if profile not in follow_check.followers.all():
                    return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)
            like, created = CommentLike.objects.get_or_create(comment=comment)
            if profile not in like.people.all():
                return Response({'message': 'Comment not previously liked'}, status=status.HTTP_400_BAD_REQUEST)
            comment.likes -= 1
            comment.save()

            like.people.remove(profile)


            data = {'message': 'success'}
            return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def delete_post(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    post = get_object_or_404(Post, id=pk)
    if post.profile != profile:
        return Response({'message':'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])

def delete_comment(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    comment = get_object_or_404(Comment, id=pk)
    if comment.profile != profile:
        return Response({'message':'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_post(request, pk):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    post = get_object_or_404(Post, id=pk)
    profile1 = post.profile

    block = block_list.objects.filter(profile=profile, blocked_profile=profile1)
    if block.exists():
        return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

    block_lists = block_list.objects.filter(profile=profile1, blocked_profile=profile)
    if block_lists.exists():
        return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


    follow_check = get_object_or_404(follow_list, profile=profile1)
    if profile1.private_account == True and profile!=profile1:
        if profile not in follow_check.followers.all():
            return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)
    serializer1 = PostSerializer(post, many=False)
    comments = Comment.objects.filter(post=post)
    if comments:
        serializer = CommentSerializer(comments, many=True)
        data = {'message':'success',
                'post':serializer1.data,
                'comments': serializer.data}

        return Response(data, status=status.HTTP_200_OK)
    else:
        data = {'message':'success',
                'post':serializer1.data,
                'comments':'No comments yet'}

        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_posts(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    post = Post.objects.filter(profile=profile)
    if post:
        serializer = PostSerializer(post, many=True)
        data = {'message':'success',
                'posts': serializer.data}

        return Response(data, status=status.HTTP_200_OK)
    else:
        data = {'message':'success',
                'post': 'No posts made yet'}
        return Response(data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_post(request, username):
    user = request.user
    profile1 = get_object_or_404(Profile, user=user)
    profile = get_object_or_404(Profile, username=username)
    post = Post.objects.filter(profile=profile)

    block = block_list.objects.filter(profile=profile1, blocked_profile=profile)
    if block.exists():
        return Response ({'user already blocked'}, status=status.HTTP_400_BAD_REQUEST)

    block_lists = block_list.objects.filter(profile=profile, blocked_profile=profile1)
    if block_lists.exists():
        return Response ({'you are blocked by the user'}, status=status.HTTP_400_BAD_REQUEST)


    follow_check = get_object_or_404(follow_list, profile=profile)
    if profile.private_account == True and profile!=profile1:
        if profile1 not in follow_check.followers.all():
            return Response({'message':'Not following Private Account'}, status=status.HTTP_400_BAD_REQUEST)

    if post:
        serializer = PostSerializer(post, many=True)
        data = {'message':'success',
                'posts': serializer.data}

        return Response(data, status=status.HTTP_200_OK)

    else:
        data = {'message':'success',
                'post': 'No posts made yet'}

        return Response(data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def timeline(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    two_days_ago = timezone.now() - timedelta(days=2)
    

    follow = get_object_or_404(follow_list, profile=profile)
    

    posts = Post.objects.filter(
        profile__in=follow.following.all(),
        date_created__gte=two_days_ago
    ).order_by('-date_created') 


    serializer = PostSerializer(posts, many=True)
    

    data = {'posts': serializer.data}
    
    return Response(data, status=status.HTTP_200_OK)
