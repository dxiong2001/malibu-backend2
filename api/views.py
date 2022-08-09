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
        tweets = Tweet.objects.all()
        tweets_serializer=TweetSerializer(tweets, many=True)
        tweet_objects = tweets_serializer.data
        
        array_tweets=[]
        for t in tweet_objects:
            
            try:
                array_tweets.append(json.loads(t['tweet']))
            except:
                array_tweets.append(t['tweet'])
        return JsonResponse(array_tweets, safe=False)
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
    #     try:
    #         tweets = Tweet.objects.all()
    #         tweets_serializer=TweetSerializer(tweets, many=True)
    #         tweet_objects = tweets_serializer.data
            
    #         #print(tweet_objects)

    #         for t in tweet_objects:
    #             db_tweet_url = t['url']
    #             if(db_tweet_url==article_url):
    #                 return JsonResponse(json.loads(t['tweet']), safe=False)
            
    #     except:
    #         pass

    Tweet_ = getTweet2(url, article_url)
    
    return JsonResponse(Tweet_, safe=False)
    