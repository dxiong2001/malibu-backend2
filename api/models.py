from django.db import models
import uuid

# Create your models here.
class Entity(models.Model):
    name = models.CharField(max_length=200)
    userName = models.CharField(max_length=200)
    screenName = models.CharField(max_length = 200)
    profileImg = models.TextField()

class Quote(models.Model):
    author = models.ForeignKey(Entity, on_delete=models.CASCADE)
    text = models.TextField()

class Section(models.Model):
    text = models.TextField()
    quotes = models.ManyToManyField(Quote)

class Tweet(models.Model):
    _id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    subtitle = models.TextField()
    time = models.TextField()
    publisher = models.ForeignKey(Entity, on_delete=models.CASCADE,related_name='publisher')
    author = models.ForeignKey(Entity, on_delete=models.CASCADE,related_name='author')
    image = models.TextField()
    sections = models.ManyToManyField(Section)