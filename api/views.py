import json
from django.http import JsonResponse
from .helper import *
from django.views.decorators.csrf import csrf_exempt
import urllib
import nltk.tokenize.texttiling as tt
from rest_framework.decorators import api_view
from api.homepage import get_articles, get_info
from datetime import date

from rq import Queue
from .worker import conn

q = Queue(connection=conn)

def tweetsApi(request, *args, **kwargs):

    param = "default"
    body_data = {}
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    

    # for url in urls:
    #     getTweet(url, 100, 0.2, 0)
    

    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    collection = dbname["api_home"]
    try:
        home = collection.find_one({'Date': today})['Info']
        return JsonResponse(home, safe=False)
    except:
        collection.delete_one({})
        try:
            body_data['params'] = dict(request.GET)
            param = body_data['params']['category'][0]
        except:
            pass
        urls = get_articles(param)
        info = get_info(urls)
    collection.insert_one({'Date': today, 'Info': info})

    
    
    return JsonResponse(info, safe=False)
        

# def tweetsApi(request, *args, **kwargs):
#     if request.method=='GET':
#         my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
#         dbname = my_client['Tweets']

#         collection_name = dbname["api_tweet"]
#         tweets = collection_name.find({})
        
#         tweet_list = list(tweets)
        
#         tweets_sorted = sorted(tweet_list, key=lambda d: d['visitedCnt'],reverse=True) 
#         if(len(tweet_list)>5):
#             tweets_sorted = tweets_sorted[0:5]
#         print(tweets_sorted)
#         tweets_return = []
#         for t in tweets_sorted:
#             return_tweet = t
#             return_tweet['_id'] = str(return_tweet['_id'])
#             tweets_return.append(return_tweet)
#         return JsonResponse(tweets_return, safe=False)
        
#     return JsonResponse("Invalid request", safe=False)


@api_view(['GET', 'POST'])
def api_home(request, *args, **kwargs):
    
    
    body_data = {}
    
    body_data['params'] = dict(request.GET)
    url = body_data['params']['url'][0]
    tweetNum = 0.2
    
    try:
        tweetNum = int(body_data['params']['tweetNum'][0])/100
    except:
        pass
    
    if url[-1]=="/":
        url = url[:-1]
    
    
    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    collection_name = dbname["api_tweet"]
    visitor_count = 0
    try:
        tweets = collection_name.find_one({'URL': url, 'tweetNum': tweetNum})
        print("found in db")
        num = tweets['visitedCnt']
        
        return_tweet = tweets
        return_tweet['visitedCnt']+=1
        return_tweet['_id'] = str(return_tweet['_id'])
        collection_name.update_one({'URL':url}, {"$set": {'visitedCnt': num+1}}, upsert=False)
        return JsonResponse(return_tweet, safe=False)
    except:
        print("not found in db")
        try:
            tweets = collection_name.find_one({'URL': url})
            visitor_count = tweets['visitedCnt']
        except:
            pass
        collection_name.delete_one({'URL':url})


    Tweet_ = getTweet(url, 100, tweetNum, visitor_count)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)

def tweetUpdate(request, *args, **kwargs):
    body_data = {}
    
    body_data['params'] = dict(request.GET)
    url = body_data['params']['url'][0]
    
    if url[-1]=="/":
        url = url[:-1]
    tweetNum = 0.2
    
    try:
        tweetNum = int(body_data['params']['tweetNum'][0])/100
    except:
        pass
    Tweet_ = updateTweet(url, 100, tweetNum)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)
    
def tweetEdit(request, *args, **kwargs):
    body_data = {}
    
    body_data['params'] = dict(request.GET)
    url = body_data['params']['url'][0]
    #tweetPercent = 0.25
    if url[-1]=="/":
        url = url[:-1]
    tweetNum = 0.2
    
        
    try:
        tweetNum = int(body_data['params']['tweetNum'][0])/100
    except:
        pass
    print(tweetNum)
    Tweet_ = editTweet(url, 100, tweetNum)
    Tweet_['_id'] = str(Tweet_['_id'])
    return JsonResponse(Tweet_, safe=False)

def tweetHome(request, *args, **kwargs):
    param = "default"
    body_data = {}
    try:
        body_data['params'] = dict(request.GET)
        param = body_data['params']['category'][0]
    except:
        pass
    urls = get_articles(param)
    # for url in urls:
    #     getTweet(url, 100, 0.2, 0)
    return JsonResponse(urls, safe=False)
