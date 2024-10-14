from django.db import models
from Profile.models import Profile
from django.dispatch import receiver
from django.db.models.signals import post_save
from cryptography.fernet import Fernet

class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='message_sender', null=False, blank=False, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name='message_receiver', null=False, blank=False, on_delete=models.CASCADE)
    encrypted_body = models.TextField(blank=False)  
    date_created = models.DateTimeField()  
    read = models.BooleanField(default=False)
    replying_to = models.ForeignKey('self', related_name='base_message', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.sender.__str__()  

    def set_body(self, body):
        
        key = self.get_key()
        fernet = Fernet(key)
        self.encrypted_body = fernet.encrypt(body.encode()).decode()

    def get_body(self):
        
        key = self.get_key()
        fernet = Fernet(key)
        return fernet.decrypt(self.encrypted_body.encode()).decode()

    @staticmethod
    def get_key():
    	with open("fernet_key.txt", "rb") as key_file:
    		return key_file.read().strip()

    class Meta:
    	ordering = ['-date_created',]
    	
        

class Chat(models.Model):
	sender = models.ForeignKey(Profile, related_name='messages_sender', null=False, blank=False, on_delete=models.CASCADE)
	receiver = models.ForeignKey(Profile, related_name='messages_receiver', null=False, blank=False, on_delete=models.CASCADE)
	last_message = models.CharField(max_length=1000, blank=False)
	last_updated = models.DateTimeField(null=True)
	messages = models.ManyToManyField(Message, related_name='chat_messages', blank=True)
	opened = models.BooleanField(default=False)

	def __str__(self):
		return self.last_message

	def get_body(self):

		key = self.get_key()
		fernet = Fernet(key)
		return fernet.decrypt(self.last_message.encode()).decode()

	@staticmethod
	def get_key():
		with open("fernet_key.txt", "rb") as key_file:
			return key_file.read().strip()

class ReadReceipts(models.Model):
	profile = models.ForeignKey(Profile, related_name='profile_receipts', null=False, blank=False, on_delete=models.CASCADE)
	read_receipts = models.BooleanField(default=True)

	def __str__(self):
		return self.profile.__str__()

@receiver(post_save, sender=Profile)

def create_read_receipts(sender, instance, created, **kwargs):
	if created:
		ReadReceipts.objects.create(profile=instance)

post_save.connect(create_read_receipts, sender=Profile)

