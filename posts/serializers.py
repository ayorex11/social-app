from rest_framework import serializers
from .models import Post, Comment, Like, CommentLike
from Profile.serializers import ProSerializer

class CreatePostSerializer(serializers.ModelSerializer):

	class Meta:
		model = Post
		fields = ['body','picture']


class PostSerializer(serializers.ModelSerializer):

	class Meta:
		model = Post
		fields = '__all__'

class CreateCommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['post', 'body', 'picture', 'parent']


class CommentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Comment
		fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
	people = ProSerializer(many=True)

	class Meta:
		model = Like
		fields = ['people',]

class CommentLikeSerializer(serializers.ModelSerializer):
	people = ProSerializer(many=True)

	class Meta:
		model = CommentLike
		fields = ['people',]

