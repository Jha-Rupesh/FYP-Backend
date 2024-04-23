from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .manager import UserManager


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email Address'), unique=True)
    name = models.CharField('Name', max_length=150, null=True, blank=True)
    user_image = models.ImageField(upload_to='user_image/', blank=True, null=True)
    phone = models.CharField('Phone Number',max_length=15, unique=True, blank=True, null=True)
    address = models.CharField('Address', max_length=80, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class UserType(models.IntegerChoices):
        CLIENT = 1, _('Client')
        ADMIN = 2, _('Admin')
        Customer = 3, _('Customer')

    user_type = models.IntegerField(choices=UserType.choices, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_admin(self):
        "Is the user a admin?"
        return self.user_type == self.UserType.ADMIN

    @property
    def is_client(self):
        "Is the user a client?"
        return self.user_type == self.UserType.CLIENT

    @property
    def is_customer(self):
        "Is the user a customer?"
        return self.user_type == self.UserType.Customer

    def get_image(self):
        if not self.user_image:
            return '/media/user_image/user.jpg'
        else:
            return self.user_image


