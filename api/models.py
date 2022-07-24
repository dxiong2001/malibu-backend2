from django.db import models
import uuid

# Create your models here.
class Entity(models.Model):
    name = models.CharField(max_length=200)
    userName = models.CharField(max_length=200)
    screenName = models.CharField(max_length = 200)
    profileImg = models.CharField()

class Quote(models.Model):
    author = models.ForeignKey(Entity, on_delete=models.CASCADE)
    text = models.CharField()

class Section(models.Model):
    text = models.CharField()
    quotes = models.ManyToManyField(Quote)

class Tweet(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField()
    subtitle = models.CharField()
    time = models.CharField()
    publisher = models.ForeignKey(Entity, on_delete=models.CASCADE)
    author = models.ForeignKey(Entity, on_delete=models.CASCADE)
    image = models.CharField()
    sections = models.ManyToManyField(Section)