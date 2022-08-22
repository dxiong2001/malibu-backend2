import json
from django.http import JsonResponse
from .helper import *
from django.views.decorators.csrf import csrf_exempt
import urllib
import nltk.tokenize.texttiling as tt
from rest_framework.decorators import api_view


from api.models import Tweet
from api.serializers import TweetSerializer

from rq import Queue
from .worker import conn

q = Queue(connection=conn)

def tweetsApi(request, *args, **kwargs):
    if request.method=='GET':
        tweets = list(Tweet.objects.values())
        
        if(len(tweets)>5):
            tweets = tweets[0:5]
        
        # tweet_objects = tweets_serializer.data
        
        # array_tweets=[]
        # i = 0
        # for t in tweet_objects:
            
        #     array_tweets.append(json.loads(t['tweet']))
            
        #     if i==4:
        #         break
        #     i+=1
        return JsonResponse(tweets, safe=False)
    return JsonResponse("Invalid request", safe=False)



@api_view(['GET', 'POST'])
def api_home(request, *args, **kwargs):
    # start_time = time.time()
    # body = request.body
    
    body_data = {}
    # try:
    #     body_data = json.loads(body) # string of JSON data -> python dict
    # except:
    #     pass

    # print(body_data)
    body_data['params'] = dict(request.GET)
    article_url = body_data['params']['url'][0]
    url = urllib.parse.unquote(article_url)
    
    # if request.method=="GET":
    tweets = list(Tweet.objects.values())
    for t in tweets:
        print(t)
        if t['url'] == url:
            return JsonResponse(t, safe=False)

    Tweet_ = getTweet(url, article_url, 50)
    
    return JsonResponse(Tweet_, safe=False)

def tweetUpdate(request, *args, **kwargs):
    body_data = {}
    # try:
    #     body_data = json.loads(body) # string of JSON data -> python dict
    # except:
    #     pass

    # print(body_data)
    body_data['params'] = dict(request.GET)
    article_url = body_data['params']['url'][0]
    url = urllib.parse.unquote(article_url)
    

    Tweet_ = getTweet(url, article_url, 200)
    
    return JsonResponse(Tweet_, safe=False)
    