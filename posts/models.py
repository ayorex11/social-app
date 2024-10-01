from django.db import models
from Profile.models import Profile

class Post(models.Model):
	profile = models.ForeignKey(Profile, related_name = 'post_creator', on_delete=models.CASCADE)
	first_name = models.CharField(max_length=500, blank=False, null=False )
	last_name = models.CharField(max_length=500, blank=False, null=False)
	body = models.CharField(max_length=1000, blank=False, null=False)
	picture = models.ImageField(upload_to='post_pic/', blank=True, null=True)
	likes = models.IntegerField(default=0)
	comment_count = models.IntegerField(default=0)
	date_created = models.DateTimeField()

	def __int__(self):
		return self.id 

	class Meta:
		ordering = ['-date_created',]


class Comment(models.Model):
	post = models.ForeignKey(Post, related_name = 'post_comment', on_delete=models.CASCADE)
	profile = models.ForeignKey(Profile, related_name='comment_creator', on_delete=models.CASCADE)
	first_name = models.CharField(max_length=500, blank=False, null=False )
	last_name = models.CharField(max_length=500, blank=False, null=False )
	body = models.CharField(max_length=1000, blank=False, null=False )
	picture = models.ImageField(upload_to='comment_pic/', blank=True, null=True)
	likes = models.IntegerField(default=0)
	reply_count = models.IntegerField(default=0)
	date_created = models.DateTimeField()
	parent = models.ForeignKey('self', related_name='replies', null=True, blank=True, on_delete=models.CASCADE)

	def __int__(self):
		return self.id

	class Meta:
		ordering = ['-date_created',]


class Like(models.Model):
	post= models.ForeignKey(Post, related_name='liked_post', on_delete=models.CASCADE)
	people = models.ManyToManyField(Profile, related_name='people_that_liked')

	def __str__(self):
		return self.post.__str__()


