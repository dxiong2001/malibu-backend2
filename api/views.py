import json
from django.http import JsonResponse
from .helper import *
from django.views.decorators.csrf import csrf_exempt
import urllib
import nltk.tokenize.texttiling as tt
from rest_framework.decorators import api_view
from bson import json_util
from api.models import Tweet
from api.serializers import TweetSerializer

from rq import Queue
from .worker import conn

q = Queue(connection=conn)

def tweetsApi(request, *args, **kwargs):
    if request.method=='GET':
        my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
        dbname = my_client['Tweets']

        collection_name = dbname["api_tweet"]
        tweets = collection_name.find({})
        
        tweet_list = list(tweets)
        
        tweets_sorted = sorted(tweet_list, key=lambda d: d['visitedCnt'],reverse=True) 
        if(len(tweet_list)>5):
            tweets_sorted = tweets_sorted[0:5]
        print(tweets_sorted)
        tweets_return = []
        for t in tweets_sorted:
            return_tweet = t
            return_tweet['_id'] = str(return_tweet['_id'])
            tweets_return.append(return_tweet)
        return JsonResponse(tweets_return, safe=False)
        
    return JsonResponse("Invalid request", safe=False)



@api_view(['GET', 'POST'])
def api_home(request, *args, **kwargs):
    
    
    body_data = {}
    
    body_data['params'] = dict(request.GET)
    url = body_data['params']['url'][0]
    article_percent = 0.2
    
    try:
        article_percent = int(body_data['params']['tweetNum'][0])/100
    except:
        pass
    
    if url[-1]=="/":
        url = url[:-1]
    
    
    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    collection_name = dbname["api_tweet"]
    
    try:
        tweets = collection_name.find_one({'URL': url})

        num = tweets['visitedCnt']
        
        return_tweet = tweets
        return_tweet['visitedCnt']+=1
        return_tweet['_id'] = str(return_tweet['_id'])
        collection_name.update_one({'URL':url}, {"$set": {'visitedCnt': num+1}}, upsert=False)
        return JsonResponse(return_tweet, safe=False)
    except:
        pass
    

    Tweet_ = getTweet(url, 50, article_percent)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)

def tweetUpdate(request, *args, **kwargs):
    body_data = {}
    
    body_data['params'] = dict(request.GET)
    url = body_data['params']['url'][0]
    
    if url[-1]=="/":
        url = url[:-1]
    article_percent = 0.2
    
    try:
        article_percent = int(body_data['params']['tweetNum'][0])/100
    except:
        pass
    Tweet_ = updateTweet(url, 200, article_percent)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)
    
    