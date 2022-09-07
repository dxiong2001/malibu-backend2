from django.urls import path

from . import views


urlpatterns = [
    path('tweet/', views.api_home),
    path('tweets', views.tweetsApi),
    path('tweetUpdate/', views.tweetUpdate),
    path('tweetEdit/', views.tweetEdit)
]