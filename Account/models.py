from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create(self, username, email, password, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self.create(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        if email is None:
            raise ValueError('The Email field must be set for superusers.')
        user = self.create(username, email, password, **extra_fields)
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
  

class User(AbstractBaseUser, PermissionsMixin):
  first_name = models.CharField(max_length = 250, blank=False, null =False)
  last_name = models.CharField(max_length=250, blank=True, null = True)
  email = models.EmailField(('email address'), unique = True)
  username = models.CharField(max_length=250, blank=False, null = False, unique=True)
  date_joined = models.DateTimeField(auto_now_add=True)
  created_at = models.DateField(auto_now_add = True)
  is_active = models.BooleanField(default = True)
  is_admin = models.BooleanField(default=False)


  objects = UserManager()
  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['email',]

  groups = models.ManyToManyField(
        Group,
        related_name='social_groups',  # Change this to something unique
        blank=True,
  )
  user_permissions = models.ManyToManyField(
        Permission,
        related_name='social_permissions',  # Change this to something unique
        blank=True,
  )

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
  def get_full_name(self):
    full = self.first_name + ' ' + self.last_name
    return full  
  def get_short_name(self):
    return self.username
  def __str__(self):
    return self.email 
  def has_perm(self, perm, obj=None):
    return True
  def has_module_perms(self, app_label):
    return True
  @property
  def is_staff(self):
    return self.is_admin