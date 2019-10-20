# pylint: disable=R0903

from django.db import models

from ..models import (
    CustomBaseModel,
    CustomBaseModelWithSoftDelete,
)


class BasicPost(CustomBaseModel):
    title = models.CharField(max_length=255)

    class Meta:
        managed = False

    def __str__(self):
        return self.title


class Category(CustomBaseModelWithSoftDelete):
    title = models.CharField(max_length=255)

    class Meta:
        managed = False

    def __str__(self):
        return self.title


class Post(CustomBaseModelWithSoftDelete):
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)

    class Meta:
        managed = False

    def __str__(self):
        return self.title


class Person(CustomBaseModelWithSoftDelete):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False

    def __str__(self):
        return self.name


class Member(CustomBaseModelWithSoftDelete):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(to='Person')

    class Meta:
        managed = False

    def __str__(self):
        return self.title
