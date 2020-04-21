from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    #additional fields
    profile_pic = models.ImageField(upload_to = 'profile_pics',blank=True)
    fav_actor = models.CharField(max_length=256)
    movie1 = models.CharField(max_length=256,default="Avatar")
    movie2 = models.CharField(max_length=256,default="Spectre")
    movie3 = models.CharField(max_length=256,default="Johnny English Reborn")
    movie4 = models.CharField(max_length=256,default="Die Another Day")
    replacer = models.IntegerField(default=4)

    def __str__(self):
        return self.user.username
  