import json
from django.http import JsonResponse
from .parser import *
from .extraction import Summarizer, textrank
import urllib
import nltk.tokenize.texttiling as tt


def api_home(request, *args, **kwargs):

    body = request.body

    data = {}
    try:
        data = json.loads(body) # string of JSON data -> python dict
    except:
        pass

    print(data)
    data['params'] = dict(request.GET)
    url = data['params']['url'][0]

    #url='https%3A%2F%2Fwww.popsci.com%2Fscience%2Fomicron-coronavirus-variant%2F'
    
    
    url = urllib.parse.unquote(url)
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
    Tweet = {'id_': "1232", 'author': authorEntity, 'time': date, 'title': title, 'subtitle': subtitle, 'image': image, 'publisher': publisherEntity, 'sections': SectionList}
    # data['headers'] = dict(request.headers)
    # data['content_type'] = request.content_type
    return JsonResponse(Tweet)