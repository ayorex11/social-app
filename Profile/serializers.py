from rest_framework import serializers
from .models import Profile, follow_list

class ProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = Profile
		exclude = ['user',]
		read_only_fields = ['followers_count', 'following_count']


class MiniProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = Profile
		exclude = ['user','about_me','followers_count', 'following_count']

class ProSerializer(serializers.ModelSerializer):

	class Meta:
		model = Profile
		fields = ['id', 'username']

class FollowerSerializer(serializers.ModelSerializer):
	followers = ProSerializer(many=True)
	class Meta:
		model = follow_list
		fields = ['followers',]

class FollowingSerializer(serializers.ModelSerializer):
	following = ProSerializer(many=True)

	class Meta:
		model = follow_list
		fields = ['following',]