import json
from re import T
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
        
        return JsonResponse(tweets_serializer.data, safe=False)
    return JsonResponse("Invalid request", safe=False)
        


def api_home(request, *args, **kwargs):

    body = request.body
    
    body_data = {}
    try:
        body_data = json.loads(body) # string of JSON data -> python dict
    except:
        pass

    print(body_data)
    body_data['params'] = dict(request.GET)
    article_url = body_data['params']['url'][0]
    
    try:
        tweet_data = Tweet.get(url=article_url)
        return JsonResponse([json.loads(tweet_data['tweet'])], safe=False)
    except:
        pass

    

    #url='https%3A%2F%2Fwww.popsci.com%2Fscience%2Fomicron-coronavirus-variant%2F'
    
    
    url = urllib.parse.unquote(article_url)
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
    Tweet = {'_id': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}
    # data['headers'] = dict(request.headers)
    # data['content_type'] = request.content_type
    
    json_tweet = json.dumps(Tweet)
    new_tweet = json.dumps({'url': article_url, 'tweet': json_tweet})
    tweet_serializer = TweetSerializer(data=new_tweet)
    if tweet_serializer.is_valid():
        tweet_serializer.save()
    
    return JsonResponse([Tweet],safe=False)