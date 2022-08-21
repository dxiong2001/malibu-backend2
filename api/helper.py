import json
from .parser import *
from .extraction import Summarizer, textrank

from nltk.tokenize import sent_tokenize
import nltk.tokenize.texttiling as tt

from api.models import Tweet
from api.serializers import TweetSerializer

from datetime import datetime


def processSection(section_list, section_titles, quotes, summary, author_entity, iterations):
    SectionList = []
    
    sentences1 = []
    for s in section_list:
        sentences1.append(sent_tokenize(s.replace("\n","").strip()))
    

    for s in range(len(section_list)):
        

        # text_to_rank = "\n\n".join(section_list[s])
        
        Points = []

        
        text_rank = summary.generate([section_list[s].strip()], top = 3, iterations=iterations)
        text = text_rank[0]
        sorted_text = text

        try:
            indices = {c: i for i, c in enumerate(sentences1[s])}
            sorted_text = sorted(text, key=indices.get)
        except:
            pass
        
        if(len(section_titles)>1 and section_titles[s] != "Introduction" ):
            sorted_text.insert(0, section_titles[s])
        
        
        
        for sort in sorted_text:
            isQuote = False
            
            for q in quotes[s]:
                
                
                if sort in q[1].replace("\n",""):
                    Points.append(createQuote(q[0], sort))
                    isQuote = True
                    break
            if not isQuote:
                Points.append({'author': author_entity, 'text': sort})
        
        
        SectionList.append({'points': Points})
        
    return SectionList


def getTweet(url, article_url, iterations):

    texttiler = tt.TextTilingTokenizer(w=30, k=40)
    summary = Summarizer(texttiler)

    page_content = get_html(url)
    body_content = getArticleBody(page_content)
    article_sections, article_p, article_p2, article_subtitles = getArticleBodySections(body_content)
    
    if(len(article_sections)==1):
        article_body_text = "\n\n".join(article_p)
        article_sections = summary.texttile(article_body_text)
    
    article_people = get_names(article_sections)
    attributed_quotes = get_quotes(article_sections, article_people)
    #print(attributed_quotes)
    title, subtitle, author, date, image = getArticleInfo(page_content)
    publisher = getArticlePublisher(page_content)
    authorEntity = createSingularEntity(author)
    publisherEntity = createSingularEntity(publisher)
    
    SectionList = processSection(article_sections, article_subtitles, attributed_quotes, summary, authorEntity, iterations = iterations)

    date_now = datetime.now()
    current_date = date_now.strftime("%m/%d/%Y, %H:%M:%S")

    Tweet_ = {'url': article_url, 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}

    print(current_date)
    
    
    # print("--- %s seconds ---" % (time.time() - start_time))
    
    
    tweet_obj = Tweet.objects.filter(url = article_url)

    
    if(len(tweet_obj)>0):
        
        tweets_serializer=TweetSerializer(tweet_obj[0])
        tweet_object = tweets_serializer.data
        
        print("filtered")
        
        Tweet_['updated_date'] = current_date
        Tweet_['created_date'] = json.loads(tweet_object['tweet'])['created_date']
        json_tweet = json.dumps(Tweet_)
        Tweet.objects.filter(url = article_url).update(tweet = json_tweet)
    else:
        Tweet_['created_date'] = current_date
        json_tweet = json.dumps(Tweet_)
        serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
        if serializer.is_valid():
            serializer.save()
            print("valid")
        else:
            print("not valid:\n", serializer.errors)
    
    
    return Tweet_


    
# def getTweet2(url, article_url, iterations):

#     texttiler = tt.TextTilingTokenizer(w=30, k=40)
#     summary = Summarizer(texttiler)

#     page_content = get_html(url)
#     body_content = getArticleBody(page_content)
#     article_sections, article_p, article_p2, article_subtitles = getArticleBodySections(body_content)
    
#     if(len(article_sections)==1):
#         article_body_text = "\n\n".join(article_p)
#         article_sections = summary.texttile(article_body_text)
    
#     article_people = get_names(article_sections)
#     attributed_quotes = get_quotes(article_sections, article_people)
#     #print(attributed_quotes)
#     title, subtitle, author, date, image = getArticleInfo(page_content)
#     publisher = getArticlePublisher(page_content)
#     authorEntity = createSingularEntity(author)
#     publisherEntity = createSingularEntity(publisher)
    
#     SectionList = processSection(article_sections, article_subtitles, attributed_quotes, summary, authorEntity, iterations = iterations)

#     Tweet_ = {'_id': "1235", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}

#     json_tweet = json.dumps(Tweet_)
    
    
#     # print("--- %s seconds ---" % (time.time() - start_time))
    
    
#     objects = Tweet.objects.filter(url = article_url)
    
#     if(len(objects)>0):
#         # print("filtered objects")
#         # for obj in objects:
#         #     obj.tweet = json_tweet
#         #     obj.save()
#         #     break
#         Tweet.objects.filter(url = article_url).update(tweet = json_tweet)
#     else:
#         serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
#         if serializer.is_valid():
#             serializer.save()
#             print("valid")
#         else:
#             print("not valid or error")
    
    
#     return Tweet_

# def getTweet1(url, article_url):
#     page_content = get_html(url)
#     processed_text = getArticleTextSections(page_content)
#     article_section = processArticleSections(processed_text)
#     # print("--- %s seconds ---" % (time.time() - start_time))
#     # start_time = time.time()


#     texttiler = tt.TextTilingTokenizer(w=30, k=40)
#     summary = Summarizer(texttiler)
#     sections, summarized_sections = summary.generate(article_section, 1)
#     #sections, summarized_sections = q.enqueue(summary.generate, article_section)
#     # print("--- %s seconds ---" % (time.time() - start_time))
#     # start_time = time.time()

#     quotes = getQuotes(processed_text)

#     title, subtitle, author, date, image = getArticleInfo(page_content)
#     publisher = getArticlePublisher(page_content)
#     people, people_extended = getNamedEntities(processed_text)
#     attributed_quotes = attribute_quote(people_extended, quotes)

#     authorEntity = createSingularEntity(author)
#     publisherEntity = createSingularEntity(publisher)

#     QuotesList = []
#     for a in attributed_quotes:
#         QuotesList.append(createQuote(a[0],a[1]))

#     SectionList = quoteToSection(sections, summarized_sections, QuotesList)
#     SectionList = processFirstSection(SectionList)
#     #print(generateEntitiesList(people))
    
#     #print(url)
#     #print(title, author,date,image)
#     #print(attributed_quotes)




#     Tweet_ = {'_id': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}
#     # data['headers'] = dict(request.headers)
#     # data['content_type'] = request.content_type
    
#     json_tweet = json.dumps(Tweet_)
    
    
#     # print("--- %s seconds ---" % (time.time() - start_time))
    
#     objects = Tweet.objects.filter(url = article_url)
#     print(Tweet.objects.all())
#     if(len(objects)>0):
#         print("filtered objects")
#         for obj in objects:
#             obj.tweet = json_tweet
#             obj.save()
#     else:
#         serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
#         if serializer.is_valid():
#             serializer.save()
#             print("valid")
#         else:
#             print("not valid or error")
    
    
#     return Tweet_

