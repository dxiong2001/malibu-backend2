#imports 
from multiprocessing import parent_process
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import sent_tokenize
import re
import unicodedata
import spacy
from decouple import config
import os


try:
  nltk.data.find('tokenizers/punkt')
  nltk.data.find('taggers/averaged_perceptron_tagger')
  
except:
  nltk.download('punkt')
  nltk.download('averaged_perceptron_tagger')
nlp = spacy.load("en_core_web_sm")


def get_html(url):
  page = requests.get(url)
  return BeautifulSoup(page.content, 'html.parser')


# extracts article body and removes extraneous "strong" tags
def getArticleBody(page_content):
  body_content = page_content.find('div', class_='Article-bodyText')
  remove_strong = body_content.find_all('strong')
  parent=[]
  for r in remove_strong:
    parent.append(r.find_parent("p"))
  # for r in remove_strong:
  #   r.extract()
  for p in parent:
    p.extract()
  return body_content

# extracts sections based on html h2 tags
def getArticleBodySections(body_content):
  section_list = []
  section_subtitles = ["Introduction"]
  section_p_list = []
  section_p_list2 = []
  first_tag = body_content.find()
  h2_list = body_content.findAll('h2')

  h2_list.insert(0, first_tag)
  tags_to_search = h2_list
  
  prior_tag = True
  for section in tags_to_search:
      next_tag = section
      sections = ""
      sections2 = []
      while True:
          if prior_tag:
            prior_tag = False
          else:
            next_tag = next_tag.nextSibling
          try:
              tag_name = next_tag.name
          except AttributeError:
              tag_name = ""
          
          if tag_name != "h2" and tag_name != "":
              if(tag_name =="p"):
                process_text1 = next_tag.get_text().replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace('…', '...').replace('–', '-')
                process_text2 = unicodedata.normalize('NFKD', process_text1)
                sections += (process_text2+" ")
                sections2.append(process_text2)
                section_p_list.append(process_text2)
          else:
              if next_tag is not None:
                section_subtitles.append(next_tag.get_text())
              section_list.append(sections)
              section_p_list2.append(sections2)
              break
  return section_list, section_p_list, section_p_list2, section_subtitles

def match_quotes(combined_sentences, quotes_incomplete):
  
  quotes_complete = []
  for q in quotes_incomplete:
    for c in combined_sentences:
      if(q in c and c not in quotes_complete):
        quotes_complete.append(c)
      
  return quotes_complete

def attribute_quote2(people, quotes):
  Quotes = []
  for q in quotes:
    found = False
    for p in people:
      for name in p:
        if name in q:
          Quotes.append((p[0],q))
          found = True
          break
        if found:
          break
      if found:
        break
  
  return Quotes

def get_names(section_list):
  joined_sentences = ' '.join(section_list)
  
  nlp_processed_text = nlp(joined_sentences)

  named_entities=[]
  for entities in nlp_processed_text.ents:
    named_entities.append((entities.text, entities.label_))
    #print(entities.text, entities.label_)
  
  people = []
  for n in named_entities:
    if(n[1]=="PERSON" and " " in n[0] and not any(i.isdigit() for i in n[0])):
      people.append(n[0])

  people_extended = []
  for p in range(len(people)):
    temp = []
    temp.append(people[p].strip())
    
    temp = temp + people[p].split()
    people_extended.append(temp)
  return people_extended

def get_quotes(section_list, people_extended):
  sentences1 = []
  for s in section_list:
    sentences1.append(sent_tokenize(s))

  quotes1 = []
  for s in sentences1:
    quotes2 = [re.findall('"([^"]*)"', paragraph) for paragraph in s]
    quotes3 = [q for q in quotes2 if q != []]
    quotes1.append(sum(quotes3,[]))

  completed_quotes = []
  for q in range(len(quotes1)):
    completed_quotes.append(match_quotes(sentences1[q], quotes1[q]))
  attributed_quotes=[]
  for c in completed_quotes:
    
    attributed_quotes.append(attribute_quote(people_extended, c))
  return attributed_quotes

def processText(article_content):
  processed_text=[]
  for art in article_content:
    p2 = art.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace('…', '...').replace('–', '-')
    processed_text.append(unicodedata.normalize('NFKD', p2))
  
  return processed_text

def getArticleTextSections(page_content):
  body_text = page_content.find('div', class_='Article-bodyText')
  remove_strong = body_text.find_all('strong')
  for r in remove_strong:
    r.extract()
  body_text_p = body_text.find_all('p', class_='')

  processed_text1 = [item.get_text() for item in body_text_p]
  processed_text2=[]
  for processed in processed_text1:
    p2 = processed.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace('…', '...').replace('–', '-')
    processed_text2.append(unicodedata.normalize('NFKD', p2))
  
  return processed_text2

def processArticleSections(processed_text):
  return '\n\n'.join(processed_text)  

def getCombinedText(processed_text):
  sentences = [sent_tokenize(sent) for sent in processed_text]

  combined_sentences = []
  for sent in sentences:
    combined_sentences += sent

  return combined_sentences




def getQuotes(processed_text):
  combined_sentences = getCombinedText(processed_text)

  quotes_incomplete = [re.findall('"([^"]*)"', paragraph) for paragraph in processed_text]
  quotes_incomplete = [q for q in quotes_incomplete if q != []]
  quotes_incomplete2 = [j for i in quotes_incomplete for j in i]

  quotes_complete =[]

  i=0
  for comb in combined_sentences:
    
    if(quotes_incomplete2[i] in comb):
      if(comb not in quotes_complete):
        quotes_complete.append(comb)
      i = i + 1
      while i < len(quotes_incomplete2) and quotes_incomplete2[i] in comb:
          i = i + 1
      
    
    if(i==len(quotes_incomplete2)):
        break

  return quotes_complete

def getArticleInfo(page_content):

  #grab article information
  header = page_content.find('div', class_='Article-header')
  article_info = header.find('p', class_='Article-author').get_text()

  title = header.find('h1', class_='u-entryTitle').get_text()
  author = article_info.split("|")[0].replace("\n","").strip()[2:].strip()
  date = article_info.split("|")[1].replace("\n","").strip()

  image_html = page_content.findAll('img', class_ = 'SingleImage-image Article-thumbnail wp-post-image')[0]
  image = image_html.get("src")

  subtitle = header.find('p', class_='Article-excerpt').get_text().replace("\n","")

  return title, subtitle, author, date, image

def getArticlePublisher(page_content):
  publisher = page_content.find('img', class_='header__logo')
  return publisher.get("alt")


def getNamedEntities(processed_text):
  joined_sentences = ' '.join(getCombinedText(processed_text))
  
  nlp_processed_text = nlp(joined_sentences)

  named_entities=[]
  for entities in nlp_processed_text.ents:
    named_entities.append((entities.text, entities.label_))
    

  people = []
  for n in named_entities:
    if(n[1]=="PERSON" and " " in n[0] and not any(i.isdigit() for i in n[0])):
      people.append(n[0])

  people_extended = []
  for p in range(len(people)):
    temp = []
    temp.append(people[p])
    temp = temp+people[p].split()
    people_extended.append(temp)

  return people, people_extended

def attribute_quote(people, quotes):
  Quotes = []
  for q in quotes:
    for p in people:
      if p[1] in q or p[2] in q:
        Quotes.append((p[0],q))
  return Quotes



def getTwitterInfo(name):
  
  key = 'Bearer ' + config('BEARER')
  
  headers = {
      'Authorization': key,
  }
  querystring = {"q": name,"page":"1","count":"1"}
  url = "https://api.twitter.com/1.1/users/search.json"

  response = requests.request("GET", url, headers=headers, params=querystring)
  try:
    data = response.json()[0]
    
    #print(data)
    is_verified = data['verified']
    screen_name = data['screen_name']
    user_name = data['name']
    profile_img = data['profile_image_url']

    return is_verified, screen_name, user_name, profile_img
  except:
    return False, "NA", "NA", "NA"

def getImage(name):
  #Important note!: daily limit is 100 requests
  #used today so far: 0
  url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

  querystring = {"q": name,"pageNumber":"1","pageSize":"1","autoCorrect":"true"}

  headers = {
    "X-RapidAPI-Key": config('X_RAPID_KEY', 'Optional default value'),
    "X-RapidAPI-Host": config('X_RAPID_HOST', 'Optional default value'),
  }

  response = requests.request("GET", url, headers=headers, params=querystring)
  return response.json()['value'][0]['url']


def createEntity(name, userName, screenName, profileImg):
  return {'name': name, 'userName': userName, 'screenName': screenName, 'profileImg': profileImg}

def createQuote(name, quote):
  is_verified, screen_name, user_name, profile_img = getTwitterInfo(name)
  author = createEntity(name, user_name, screen_name, profile_img)
  return {'author': author, 'text': quote}
  
def createSingularEntity(name):
  is_verified, screen_name, user_name, profile_img = getTwitterInfo(name)
  return createEntity(name, user_name, screen_name, profile_img)



def generateEntitiesList(people):
  entities = []
  for p in people:
    is_verified, screen_name, user_name, profile_img = getTwitterInfo(p)
    entities.append(createEntity(p, user_name, screen_name, profile_img))
  return entities

def quoteToSection(sections, summarized_sections, quotes):
  SectionList = []
  i = 0
  for s in sections:
    Section={}
    Section['text'] = summarized_sections[i]
    Section['quotes'] = []
    for q in quotes:
      if(q['text'] in s):
        Section['quotes'].append(q)
    SectionList.append(Section)
    i+=1
  return SectionList

def processFirstSection(SectionList):
  section1 = SectionList[0]
  sent_nlp = nlp(section1['text'][0])
  named_entities=[]
  for entities in sent_nlp.ents:
    named_entities.append((entities.text, entities.label_))
  if(len(named_entities)==0 and len(section1['quotes'])==0):
    SectionList.pop(0)
  return SectionList
