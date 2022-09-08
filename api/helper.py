import json
from .parser import *
from .extraction import Summarizer, textrank
from .abstraction import abs_summarization

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
import math

def processRanking(sections, proportions, tweetNum, section_titles, sentences):
    SectionsRanked = []
    section_num = len(sections)
    section_len = []

    count_sent = sum( [ len(el) for el in sections])
    if(tweetNum > count_sent):
        tweetNum = count_sent
    return_count = tweetNum
    title_num = len(section_titles)
    print(tweetNum)
    if(tweetNum < 0):
        sorted_text = []
        for sec in sections:
            length_s = sum(map(len, sec))
            sorted_section = []
            count = 0
            for s in sec:
                sorted_section.append(s)
                count += len(s)
                if(count/length_s > 0.25):
                    break
            sorted_text.append(sorted_section)
        for s in range(section_num):
            
            title = False
            if len(section_titles)>1 and section_titles[s] != "Introduction":
                title = True

            try:
                indices = {c: i for i, c in enumerate(sentences[s])}
                sorted_text[s] = sorted(sorted_text[s], key=indices.get)
            except:
                pass

            if title:
                sorted_text[s].insert(0, section_titles[s])
            SectionsRanked.append(sorted_text[s])
    else:
        # print(section_titles)
        # print(section_len)
        
        for p in proportions:
            section_len.append(math.trunc(p*tweetNum))
        for s in range(title_num):
            #print(s)
            if(tweetNum==0):
                break
            if(section_titles[s]!="Introduction"):
                tweetNum-=1

        tweetNum -= sum(section_len)
        it = 0
        while tweetNum > 0:
            print(section_len)
            if(section_len[it]<len(sections[it])):
                section_len[it]+=1
                tweetNum-=1
            it = (it+1)%section_num
        print(section_len)
        for s in range(section_num):
            section = sections[s]
            len_s = len(section)
            title = False
            if len(section_titles)>1 and section_titles[s] != "Introduction":
                len_s -= 1
                title = True
            top = min(len_s, section_len[s])

            sorted_text = section[:top]

            try:
                indices = {c: i for i, c in enumerate(sentences[s])}
                sorted_text = sorted(sorted_text, key=indices.get)
            except:
                pass

            if title:
                sorted_text.insert(0, section_titles[s])
            SectionsRanked.append(sorted_text)
    return SectionsRanked, return_count
            
        



def processSection(url, section_list, section_titles, quotes, summarizer, author_entity, iterations, tweetNum):
    SectionList = []
    ranked_text = []
    section_proportions = []

    sentences1 = []
    for s in section_list:
        sentences1.append(sent_tokenize(s.replace("\n","").strip()))
    
    #abs_summ = abs_summarization(section_list)
    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    db = my_client['Tweets']

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection = db["api_rank"]
    if collection.count_documents({ 'URL': url }, limit = 1):
        db_obj = collection.find_one({'URL': url})
        ranked_text = db_obj['rankList']
        section_proportions = db_obj['proportions']
    else:
        
        section_len = []
        for s in range(len(section_list)):
            
            print("generate")
            # text_to_rank = "\n\n".join(section_list[s])
            
            
            #Points.append({'author': author_entity, 'text': abs_summ[s]})
            text_rank = summarizer.generate([section_list[s].strip()], iterations)
            text = text_rank[0]
            ranked_text.append(text)
            section_len.append(sum(map(len, text)))
        for s in section_len:
            section_proportions.append(s/sum(section_len))

        collection.insert_one({'_id': ObjectId(), "URL": url, "rankList": ranked_text, "proportions": section_proportions})


    sorted_text, num_tweets = processRanking(ranked_text, section_proportions, tweetNum, section_titles, sentences1)
    
    for s in range(len(section_list)):
        Points = []
        for sort in sorted_text[s]:
            isQuote = False
            
            for q in quotes[s]:
                
                
                if sort in q[1].replace("\n",""):
                    Points.append(createQuote(q[0], sort))
                    isQuote = True
                    break
            if not isQuote:
                Points.append({'author': author_entity, 'text': sort})
        
        
        SectionList.append({'points': Points})
    
    return SectionList, num_tweets


def updateTweet(article_url, iterations, tweetNum = 10):
    #25 -> 5 sections, #30 -> 4 sections #45 -> 3 sections, #50 -> 2 sections
    texttiler = tt.TextTilingTokenizer(w=30, k=40)
    summarizer = Summarizer(texttiler)

    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    db = my_client['Tweets']
    collection = db["api_rank"]

    collection_info = db["api_article"]

    db_obj = collection_info.find_one({'URL': article_url})
    article_sections = db_obj['sections']
    article_subtitles = db_obj['subtitles']
    attributed_quotes = db_obj['quotes']
    
    
    

    tz = pytz.timezone('America/Los_Angeles')
    date_now = datetime.now(tz)
    current_date = date_now.strftime("%m/%d/%Y, %H:%M:%S")

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection= db["api_tweet"]
    post = collection.find_one({'URL': article_url})

    authorEntity = post['author']
    SectionList, num_tweets = processSection(article_url, article_sections, article_subtitles, attributed_quotes, summarizer, authorEntity, iterations, tweetNum)


    post['sections'] = SectionList
    post['updatedAt'] = current_date
    post['tweetNum'] = num_tweets
    collection.update_one({'URL':article_url}, {"$set": post}, upsert=False)
    
    return post

def getTweet(article_url, iterations, tweetNum = -1):

    texttiler = tt.TextTilingTokenizer(w=30, k=40)
    summarizer = Summarizer(texttiler)

    my_client = pymongo.MongoClient(config('CONNECTION_STRING'))
    db = my_client['Tweets']

    page_content = get_html(article_url)
    body_content = getArticleBody(page_content)
    article_sections, article_p, article_p2, article_subtitles = getArticleBodySections(body_content)
    
    if(len(article_sections)==1):
        article_body_text = "\n\n".join(article_p)
        article_sections = summarizer.texttile(article_body_text)
    
    article_people = get_names(article_sections)
    attributed_quotes = get_quotes(article_sections, article_people)
    
    collection_info = db["api_article"]
    if not collection_info.count_documents({ 'URL': article_url }, limit = 1):
        collection_info.insert_one({'_id': ObjectId(), "URL": article_url, "sections": article_sections, "subtitles": article_subtitles, "quotes": attributed_quotes})

    title, subtitle, author, date, image = getArticleInfo(page_content)
    publisher = getArticlePublisher(page_content)
    authorEntity = createSingularEntity(author)
    publisherEntity = createSingularEntity(publisher)
    
    SectionList, num_tweets = processSection(article_url, article_sections, article_subtitles, attributed_quotes, summarizer, authorEntity, iterations, tweetNum)

    tz = pytz.timezone('America/Los_Angeles')
    date_now = datetime.now(tz)
    current_date = date_now.strftime("%m/%d/%Y, %H:%M:%S")

    Tweet_ = {'_id': ObjectId(),'URL': article_url, 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'visitedCnt': 1, 'tweetNum': num_tweets,'sections': SectionList, 'updatedAt': current_date}
    
    

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection
    collection = db["api_tweet"]
    collection.insert_one(Tweet_)
    
    return Tweet_


    


