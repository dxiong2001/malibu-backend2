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

        # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
        collection_name = dbname["api_tweet"]
        tweets = collection_name.find({})
        tweet_len = collection_name.find({})
        if(len(list(tweet_len))>5):
            tweets = tweets[0:5]
        
        tweets_return = []
        for t in tweets:
            return_tweet = t
            return_tweet['_id'] = str(return_tweet['_id'])
            tweets_return.append(return_tweet)
        return JsonResponse(tweets_return, safe=False)
        
    return JsonResponse("Invalid request", safe=False)



@api_view(['GET', 'POST'])
def api_home(request, *args, **kwargs):
    
    
    body_data = {}
    # try:
    #     body_data = json.loads(body) # string of JSON data -> python dict
    # except:
    #     pass

    # print(body_data)
    body_data['params'] = dict(request.GET)
    article_url = body_data['params']['url'][0]
    url = urllib.parse.unquote(article_url)
    
    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection_name = dbname["api_tweet"]
    tweets = collection_name.find({})
    for t in tweets:
        print(t)
        if t['url'] == url:
            return_tweet = t
            return_tweet['_id'] = str(return_tweet['_id'])
            return JsonResponse(return_tweet, safe=False)

    Tweet_ = getTweet(url, article_url, 50)
    Tweet_['_id'] = str(Tweet_['_id'])
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
    

    Tweet_ = updateTweet(url, article_url, 200)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)
    
    