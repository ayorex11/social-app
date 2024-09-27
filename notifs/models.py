from django.db import models
from Profile.models import Profile

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
