import json
from django.http import JsonResponse
from .parser import *
from .extraction import Summarizer, textrank
from django.views.decorators.csrf import csrf_exempt
import urllib
import nltk.tokenize.texttiling as tt

from api.models import Tweet
from api.serializers import TweetSerializer


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
        


def api_home(request, *args, **kwargs):

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
    
    try:
        tweets = Tweet.objects.all()
        tweets_serializer=TweetSerializer(tweets, many=True)
        tweet_objects = tweets_serializer.data
        
        print(tweet_objects)

        for t in tweet_objects:
            db_tweet_url = t['url']
            if(db_tweet_url==article_url):
                return JsonResponse(json.loads(t['tweet']), safe=False)
        
    except:
        pass

    

    
    
    print("test")
    
    
    page_content = get_html(url)
    processed_text = getArticleTextSections(page_content)
    article_section = processArticleSections(processed_text)
    


    texttiler = tt.TextTilingTokenizer()
    summary = Summarizer(texttiler)
    sections, summarized_sections = summary.generate(article_section, 1)




    quotes = getQuotes(processed_text)

    title, subtitle, author, date, image = getArticleInfo(page_content)
    publisher = getArticlePublisher(page_content)
    people, people_extended = getNamedEntities(processed_text)
    attributed_quotes = attribute_quote(people_extended, quotes)

    authorEntity = createSingularEntity(author)
    publisherEntity = createSingularEntity(publisher)

    QuotesList = []
    for a in attributed_quotes:
        QuotesList.append(createQuote(a[0],a[1]))

    SectionList = quoteToSection(sections, summarized_sections, QuotesList)

    #print(generateEntitiesList(people))
    
    #print(url)
    #print(title, author,date,image)
    #print(attributed_quotes)
    Tweet_ = {'_id': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}
    # data['headers'] = dict(request.headers)
    # data['content_type'] = request.content_type
    
    json_tweet = json.dumps(Tweet_)
    serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
    
    
    
    
    if serializer.is_valid():
        serializer.save()
        print("valid")
    else:
        print("not valid or error")
    
    return JsonResponse([Tweet_],safe=False)