import os
import uuid
from datetime import date

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


def get_file_path(instance, filename):
    """
    Formatting file path of avatar data
    :param instance: Model instance
    :param filename: Name of uploaded file
    :return: File path for upload_to
    """
    ext = filename.split('.')[-1]
    today = date.today().strftime("%Y/%m/%d")
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars', today, filename)


class UserManager(BaseUserManager):

    def create_user(self, email, username, password):
        if not email:
            raise ValueError('Email Required')
        print(username)
        user = self.models(
            email=self.normalize_email(email),
            username=username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password):
        if not email:
            raise ValueError('Email Required')

        user = self.models(
            email=self.normalize_email(email),
            username=username)
        user.set_password(password)
        user.is_superuser = True
        user.save()
        return user


class Skill(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)
    bio = models.CharField(max_length=300, null=True)
    avatar = models.ImageField(null=True, upload_to=get_file_path)
    date_joined = models.DateField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    profile = models.CharField(max_length=300, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_long_name(self):
        return '{} {}'.format(self.username, self.email)

    def get_absolute_url(self):
        return reverse('profile', args=[str(self.id)])


class Project(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200)
    url = models.URLField(null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])


class Position(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=50)
    head_count = models.IntegerField(default=1)
    related_skills = models.ManyToManyField(Skill, blank=True)
    participants = models.ManyToManyField(User, through='Participant')

    def __str__(self):
        return self.position_name

    def get_absolute_url(self):
        return reverse('position_detail', args=[self.id])

    def get_member_count(self):
        """
        :return: Number of participants for a given position
        """
        return self.participant_set.filter(status='member').count()


class Participant(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='pending')
    created_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
