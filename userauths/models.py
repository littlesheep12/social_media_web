from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.utils.text import slugify
import shortuuid
# Create your models here.

#Overwrite User-AbstractBaseUser

GENDER = (    
    ("male","Male"),
    ("femail","Female")
)

RELATIONSHIP = (
    ("single","Single"),
    ("married","married"),
    ("inlove","In Love"),
)

def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class User(AbstractUser):
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER, default="male")

    otp = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)
    
class Profile(models.Model):
    pid = ShortUUIDField(length = 7, max_length = 25, alphabet = 'adcdefjhijklmnopqrstuvwxyz')
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    cover_image = models.ImageField(upload_to = user_directory_path, blank=True, null=True, default = "cover.jpg")
    image = models.ImageField(upload_to = user_directory_path, blank=True, null=True, default = "default.jpg")

    full_name = models.CharField(max_length=1000, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER, default="male")

    bio = models.CharField(max_length=256, null=True, blank=True)
    about_me = models.TextField(max_length=256, null=True, blank=True)
    relationship = models.CharField(max_length=256, choices=RELATIONSHIP, default="single")

    country = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)

    working_at = models.CharField(max_length=256, null=True, blank=True)

    instagram = models.CharField(max_length=256, null=True, blank=True)
    whatsapp = models.CharField(max_length=256, null=True, blank=True)

    verified = models.BooleanField(default=False)

    followers = models.ManyToManyField(User, blank=True, related_name="followers")
    followings = models.ManyToManyField(User, blank=True, related_name="followings")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    blacked = models.ManyToManyField(User, blank=True, related_name="blacked")

    # slug = models.SlugField(unique=True, blank=True, null=True, default="default-slug")

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.full_name != "" or self.full_name != None:
            return self.full_name
        else:
            return self.user
    
    # def save(self, *args, **kwargs):
    #     if self.slug == "" or self.slug == None:
    #         uuid_key = shortuuid.uuid()
    #         uniqueid = uuid_key[:2]
    #         self.slug = slugify(self.full_name) + '-' + str(uniqueid.lower()) # leo-aa
    #     super(Profile, self).save(*args, **kwargs)

############################## 
# auto create the user profile
##############################
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user = instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)