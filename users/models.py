from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, userid, nickname, email, password, **extra_fields):
        if not email:
            raise ValueError('Email을 입력해주세요.')
        if not userid:
            raise ValueError('Id를 입력해주세요.')
        if not nickname:
            raise ValueError('Nickname을 입력해주세요.')
        email = self.normalize_email(email)
        userid = self.model.normalize_username(userid)
        nickname = self.model.normalize_username(nickname)
        user = self.model(userid=userid, email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_user(self, userid, nickname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(userid, nickname, email, password, **extra_fields)

    def create_superuser(self, userid, nickname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=True일 필요가 있습니다.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=True일 필요가 있습니다.')
        return self._create_user(userid, nickname, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    userid = models.CharField(_("userid"), max_length=20, unique=True, validators=[username_validator])
    nickname = models.CharField(_("nickname"), max_length=12, unique=True, validators=[username_validator])
    email = models.EmailField(_("email_address"), unique=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "userid"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['email', 'nickname']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
