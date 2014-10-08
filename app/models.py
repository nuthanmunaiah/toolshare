from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse


class System(object):
    @staticmethod
    def get_share_zones():
        return ShareZone.objects.all()

    @staticmethod
    def get_or_create_share_zone(zip):
        share_zone, created = ShareZone.objects.get_or_create(zip=zip)
        return share_zone


class ShareZone(models.Model):
    zip = models.CharField(max_length=9, default='', blank=False)

    # TODO : Define get_tools method
    def get_tools(self):
        pass


class UserManager(BaseUserManager):
    def create_user(self):
        pass

    def create_superuser(self):
        pass


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=30, blank=False)
    middle_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    phone_num = models.CharField(max_length=11, default='', blank=True)

    email = models.EmailField(unique=True, blank=False)

    pickup_arrangements = models.TextField(max_length=100, default='', blank=True)

    reputation = models.PositiveIntegerField(default=0, blank=True)

    # TODO : Figure out a way to move address-related fields to a separate model
    apt_num = models.CharField(max_length=10, default='', blank=True)
    street = models.CharField(max_length=50, default='', blank=False)
    city = models.CharField(max_length=50, default='', blank=False)
    county = models.CharField(max_length=50, default='', blank=True)
    state = models.CharField(max_length=2, default='', blank=False)
    country = models.CharField(max_length=50, default='USA', blank=False)
    zip = models.CharField(max_length=9, default='', blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    # Foreign keys
    share_zone = models.ForeignKey(ShareZone)

    def Update(self):
        pass

    def Register(self, Tool):
        pass

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        full_name = self.first_name

        if self.middle_name:
            full_name = full_name + ' ' + self.middle_name

        if self.last_name:
            full_name = full_name + ' ' + self.last_name

        return full_name


class BlackoutDate(models.Model):
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()


class Tool(models.Model):
    name = models.CharField(max_length=20)
    pictureURL = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=10)
    blackoutDates = models.ForeignKey(BlackoutDate)


class Reservation(models.Model):
    # Foreign keys
    User = models.ForeignKey(User)
    get_message = models.CharField(max_length=50, default='', blank=False)
    get_date = models.DateField()
    get_status = models.CharField(max_length=20, default='', blank=False)


class UserProfile(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    phone_num = models.CharField(max_length=11, default='', blank=True)
    email = models.EmailField(unique=True, blank=False)
    pickup_arrangements = models.TextField(max_length=100, default='', blank=True)
    apt_num = models.CharField(max_length=10, default='', blank=True)
    street = models.CharField(max_length=50, default='', blank=False)
    city = models.CharField(max_length=50, default='', blank=False)
    county = models.CharField(max_length=50, default='', blank=True)
    state = models.CharField(max_length=2, default='', blank=False)
    country = models.CharField(max_length=50, default='USA', blank=False)
    zip = models.CharField(max_length=9, default='', blank=False)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})
