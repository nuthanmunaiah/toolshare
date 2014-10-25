import datetime, hashlib, random
from django.utils import timezone
from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.template.loader import render_to_string

import app.constants
from app.email import send_email


class ShareZoneManager(models.Manager):
    def get_or_create(self, **kwargs):
        created = False
        try:
            share_zone = self.get(**kwargs)
        except ShareZone.DoesNotExist:
            share_zone = self.create(**kwargs)
            share_zone.save()
            created = True
        return [share_zone, created]


class ShareZone(models.Model):
    zip = models.CharField(max_length=9, default='', blank=False)

    objects = ShareZoneManager()

    class Meta:
        app_label = 'app'

    # TODO : Define get_tools method
    def get_tools(self):
        pass


class Address(models.Model):
    apt_num = models.CharField(max_length=10, blank=True)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50, default='', blank=True)
    state = models.CharField(max_length=2, default='', choices=app.constants.US_STATES)
    country = models.CharField(max_length=50, default='USA')
    zip = models.CharField(max_length=9)

    class Meta:
        app_label = 'app'


class UserManager(BaseUserManager):
    def _create_user(self, **extra_fields):
        # Separating the user fields and address fields for simplicity
        user_fields = self._get_fields(model='user', **extra_fields)
        address_fields = self._get_fields(model='address', **extra_fields)

        # ShareZone.zip is 9 characters wide for flexibility
        zip = (address_fields['zip'][:5]).ljust(9, '0')
        share_zone, created = ShareZone.objects.get_or_create(zip=zip)
        if created:
            share_zone.save(using=self._db)

        address = Address.objects.create(**address_fields)
        address.save(using=self._db)

        now = timezone.now()
        user_fields['email'] = self.normalize_email(user_fields['email'])
        user = self.model(date_joined=now, **user_fields)
        user.set_password(extra_fields['password1'])
        user.address = address
        user.share_zone = share_zone

        user.save(using=self._db)

        return user

    def create_user(self, **extra_fields):
        return self._create_user(**extra_fields)

    def _get_fields(self, model, **fields):
        _user_fields = ['date_joined', 'first_name', 'middle_name', 'last_name', 'phone_num', 'email',
                        'pickup_arrangements', 'reputation']
        _address_fields = ['apt_num', 'street', 'city', 'county', 'state', 'country', 'zip']

        _fields = _user_fields
        if model == 'address':
            _fields = _address_fields

        sliced_fields = dict()
        for k, v in fields.items():
            if k in _fields:
                sliced_fields[k] = v

        return sliced_fields


class User(AbstractBaseUser):
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    phone_num = models.CharField(max_length=11, blank=True)

    email = models.EmailField(unique=True)

    pickup_arrangements = models.TextField(max_length=100, blank=True)

    reputation = models.PositiveIntegerField(default=0, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    # Foreign keys
    address = models.ForeignKey(Address, unique=True)
    share_zone = models.ForeignKey(ShareZone, unique=True)

    class Meta:
        app_label = 'app'

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

    def email_user(self, subject, message, from_addr):
        send_email(subject, message, [self.email], from_addr)


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        SHA1_RE = re.compile('^[a-f0-9]{40}$')
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def create_inactive_user(self, site, send_email=True, **extra_fields):
        new_user = User.objects.create_user(**extra_fields)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        seed = salt + user.email
        activation_key = hashlib.sha1(seed.encode('utf-8')).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        for profile in self.all():
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                        profile.delete()
            except User.DoesNotExist:
                profile.delete()


class RegistrationProfile(models.Model):
    ACTIVATED = u"already_activated"

    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    class Meta:
        app_label = 'app'

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime_now())

    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        context = {'activation_key': self.activation_key,
                   'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                   'site': site}
        subject = 'Subject'
        #subject = render_to_string('', context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        #message = render_to_string('', context)
        message = 'hello world!!!'

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)