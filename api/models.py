from djongo import models
import uuid

# Create your models here.

# class Tweet(models.Model):

#     url = models.TextField(default="")
#     tweet = models.JSONField()


class Entity(models.Model):
    name = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    screen_name = models.CharField(max_length = 200)
    profile_image = models.TextField(default="")

    class Meta:
        abstract = True


class Point(models.Model):
    author = models.EmbeddedField(
        model_container=Entity
    )
    text = models.TextField(default="")

    class Meta:
        abstract = True

class Section(models.Model):
    points = models.ArrayField(
        model_container=Point
    )

    class Meta:
        abstract = True

class Tweet(models.Model):
    url = models.CharField(max_length = 200)
    title = models.CharField(max_length = 200)
    subtitle = models.CharField(max_length = 200)
    time = models.CharField(max_length = 200)
    publisher = models.EmbeddedField(
        model_container=Entity
    )
    author = models.EmbeddedField(
        model_container=Entity
    )
    image = models.CharField(max_length = 200)
    sections = models.ArrayField(
        model_container=Section
    )
    updated_date=models.CharField(max_length=200)
    