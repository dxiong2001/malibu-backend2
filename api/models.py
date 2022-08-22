from django.db import models


# Create your models here.

# class Tweet(models.Model):

#     url = models.TextField(default="")
#     tweet = models.JSONField()


class Entity(models.Model):
    name = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    screen_name = models.CharField(max_length = 200)
    profile_image = models.TextField(default="")



class Point(models.Model):
    author = models.ForeignKey(Entity, on_delete=models.CASCADE)
    text = models.TextField(default="")
    

class Section(models.Model):
    points = models.ManyToManyField(Point)

    

class Tweet(models.Model):
    url = models.CharField(max_length = 200)
    title = models.CharField(max_length = 200)
    subtitle = models.CharField(max_length = 200)
    time = models.CharField(max_length = 200)
    publisher = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name = "publisher")
    author = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name = "author")
    image = models.CharField(max_length = 200)
    sections = models.ManyToManyField(Section)
    updated_date=models.CharField(max_length=200)
    