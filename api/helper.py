import json
from .parser import *
from .extraction import Summarizer, textrank

from nltk.tokenize import sent_tokenize
import nltk.tokenize.texttiling as tt

from api.models import Tweet
from api.serializers import TweetSerializer

from datetime import datetime
import pymongo
from django.conf import settings
from decouple import config
from bson.objectid import ObjectId
import pytz

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


def updateTweet(url, article_url, iterations):

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
    

    tz = pytz.timezone('America/Los_Angeles')
    date_now = datetime.now(tz)
    current_date = date_now.strftime("%m/%d/%Y, %H:%M:%S")

    Tweet_ = {'_id': ObjectId(),'url': article_url, 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList, 'updated_date': current_date}

    

    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection_name = dbname["api_tweet"]
    post = collection_name.find_one({"url":article_url})
    post['sections'] = SectionList
    post['updated_date'] = current_date 
    collection_name.update_one({'url':article_url}, {"$set": post}, upsert=False)
    
    return post

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
    
    title, subtitle, author, date, image = getArticleInfo(page_content)
    publisher = getArticlePublisher(page_content)
    authorEntity = createSingularEntity(author)
    publisherEntity = createSingularEntity(publisher)
    
    SectionList = processSection(article_sections, article_subtitles, attributed_quotes, summary, authorEntity, iterations = iterations)

    tz = pytz.timezone('America/Los_Angeles')
    date_now = datetime.now(tz)
    current_date = date_now.strftime("%m/%d/%Y, %H:%M:%S")

    Tweet_ = {'_id': ObjectId(),'url': article_url, 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList, 'updated_date': current_date}
    print(Tweet_['_id'])
    
    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    dbname = my_client['Tweets']

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection_name = dbname["api_tweet"]
    collection_name.insert_one(Tweet_)
    
    return Tweet_


    


