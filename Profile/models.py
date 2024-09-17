from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

User = get_user_model()

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=500, blank=False, null=False)
	last_name = models.CharField(max_length=500, blank=True, null=True)
	username = models.CharField(max_length=250, blank=False, null = False, unique=True)
	profile_picture = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
	about_me = models.CharField(max_length=1000, blank=True, null=True)
	followers_count = models.IntegerField(default=0, blank=False, null=False)
	following_count = models.IntegerField(default=0, blank=False, null=False)
	private_account  = models.BooleanField(default=False)

	def __str__(self):
		return self.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user= instance, first_name=instance.first_name, last_name=instance.last_name, username=instance.username)

post_save.connect(create_profile, sender=User)


class follow_list(models.Model):
	profile = models.OneToOneField(Profile, related_name='followers_profile', on_delete=models.CASCADE)
	followers = models.ManyToManyField(Profile, related_name='followers_followers', blank=True, null=True)
	following = models.ManyToManyField(Profile, related_name='followers_following', blank=True, null=True)

	def __str__(self):
		return self.profile.__str__()

@receiver(post_save, sender=Profile)
def create_follow_list(sender, instance, created, **kwargs):
	if created:
		follow_list.objects.create(profile= instance)

post_save.connect(create_follow_list, sender=Profile)


