from django.db import models
from Profile.models import Profile
from posts.models import Post, Comment 

class Notification(models.Model):
	profile = models.ForeignKey(Profile, blank=False, null=False, related_name='notif_owner', on_delete=models.CASCADE)
	title = models.CharField(max_length=50, blank=False)
	body = models.CharField(max_length=100, blank=False)
	date_created = models.DateTimeField()
	read = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-date_created', ]

class CommentNotification(models.Model):
	profile = models.ForeignKey(Profile, blank=False, null=False, related_name='post_notif', on_delete=models.CASCADE)
	post = models.ForeignKey(Post, blank=False, null=False, related_name='post_being_replied', on_delete=models.CASCADE)
	comment = models.ForeignKey(Comment, blank=True, null=True, related_name='comment_notif', on_delete=models.CASCADE)
	title = models.CharField(max_length=50, blank=False)
	date_created= models.DateTimeField()
	read = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ['-date_created', ]
