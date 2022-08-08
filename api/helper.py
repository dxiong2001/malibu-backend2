import json
from .parser import *
from .extraction import Summarizer, textrank

from nltk.tokenize import sent_tokenize
import nltk.tokenize.texttiling as tt

from api.serializers import TweetSerializer

def processSection(section_list,quotes, summary):
    SectionList = []

    sentences1 = []
    for s in section_list:
        sentences1.append(sent_tokenize(s))

    for s in range(len(section_list)):
        Section = {}
        Quotes = []
        for q in quotes[s]:
            Quotes.append(createQuote(q[0],q[1]))
        Section['quotes'] = Quotes

        # text_to_rank = "\n\n".join(section_list[s])
        print(section_list[s])
        text_rank = summary.generate([section_list[s]], top = 3)
        print(text_rank)
        text = text_rank[0]
        Section['text'] = text[0]
        

        text.pop(0)
        Section['parts'] = []
        print(text)
        indices = {c: i for i, c in enumerate(sentences1[0])}
        
        Section['parts'] = sorted(text, key=indices.get)
        SectionList.append(Section)
    return SectionList

    
def getTweet2(url, article_url):

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
    print(len(article_sections))
    SectionList = processSection(article_sections, attributed_quotes, summary)

    Tweet_ = {'_id': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}

    json_tweet = json.dumps(Tweet_)
    serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
    db_store = {'url': article_url, 'tweet': json_tweet}
    # print("--- %s seconds ---" % (time.time() - start_time))
    
    
    if serializer.is_valid():
        serializer.save()
        print("valid")
    else:
        print("not valid or error")
    
    return Tweet_

def getTweet1(url, article_url):
    page_content = get_html(url)
    processed_text = getArticleTextSections(page_content)
    article_section = processArticleSections(processed_text)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # start_time = time.time()


    texttiler = tt.TextTilingTokenizer(w=30, k=40)
    summary = Summarizer(texttiler)
    sections, summarized_sections = summary.generate(article_section, 1)
    #sections, summarized_sections = q.enqueue(summary.generate, article_section)
    # print("--- %s seconds ---" % (time.time() - start_time))
    # start_time = time.time()

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
    SectionList = processFirstSection(SectionList)
    #print(generateEntitiesList(people))
    
    #print(url)
    #print(title, author,date,image)
    #print(attributed_quotes)




    Tweet_ = {'_id': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}
    # data['headers'] = dict(request.headers)
    # data['content_type'] = request.content_type
    
    json_tweet = json.dumps(Tweet_)
    serializer = TweetSerializer(data={'url': article_url, 'tweet': json_tweet})
    db_store = {'url': article_url, 'tweet': json_tweet}
    # print("--- %s seconds ---" % (time.time() - start_time))
    
    
    if serializer.is_valid():
        serializer.save()
        print("valid")
    else:
        print("not valid or error")
    
    return Tweet_

