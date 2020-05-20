from django.db import models
from django.contrib.auth.models import User
from event.models import EventSource, DisposeUnit

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, default='')
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    bio = models.TextField(blank=True)
    is_poster = models.BooleanField(default=False)
    is_disposer = models.BooleanField(default=False)
    unit = models.TextField(blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)


class ConfirmString(models.Model):
 
   code = models.CharField(max_length=256)
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirm_string')
   c_time = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return self.user.username + ': ' + self.code

   class Meta:
       ordering = ['-c_time']
       verbose_name = '确认码'
       verbose_name_plural = '确认码'

class ApplyList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applylist')
    apply_permission = models.CharField(max_length=256)
    apply_unit = models.CharField(max_length=256)
    validation = models.CharField(max_length=256, default='')

    def __str__(self):
        return self.user.username + "代表" + self.apply_unit + "申请" + self.apply_permission + "权限"