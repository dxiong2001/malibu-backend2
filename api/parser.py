#imports 
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import sent_tokenize
import re
import unicodedata
import spacy
from decouple import config
import os

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nlp = spacy.load("en_core_web_sm")


def get_html(url):
  page = requests.get(url)
  return BeautifulSoup(page.content, 'html.parser')


def getArticleTextSections(page_content):
  body_text = page_content.find('div', class_='Article-bodyText')
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
  author = article_info.split("|")[0].replace("\n                    ","").replace("\n              ","")[2:]
  date = article_info.split("|")[1].replace("\n    \n    Updated ","").replace("\n  \n","")

  image_html = page_content.findAll('img', class_ = 'SingleImage-image Article-thumbnail wp-post-image')[0]
  image = image_html.get("src")

  subtitle = header.find('p', class_='Article-excerpt').get_text()

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
  
  key = 'Bearer ' + os.getenv('BEARER', 'Optional default value')
  headers = {
      'Authorization': key,
  }
  querystring = {"q": name,"page":"1","count":"1"}
  url = "https://api.twitter.com/1.1/users/search.json"

  response = requests.request("GET", url, headers=headers, params=querystring)
  data = response.json()[0]
  
  is_verified = data['verified']
  screen_name = data['screen_name']
  user_name = data['name']
  profile_img = data['profile_image_url']

  return is_verified, screen_name, user_name, profile_img

def getImage(name):
  #Important note!: daily limit is 100 requests
  #used today so far: 2
  url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

  querystring = {"q": name,"pageNumber":"1","pageSize":"1","autoCorrect":"true"}

  headers = {
    "X-RapidAPI-Key": os.getenv('X_RAPID_KEY', 'Optional default value'),
    "X-RapidAPI-Host": os.getenv('X_RAPID_HOST', 'Optional default value'),
  }

  response = requests.request("GET", url, headers=headers, params=querystring)
  return response.json()['value'][0]['url']


def createEntity(name, userName, screenName, profileImg):
  return {'name': name, 'userName': userName, 'screenName': screenName, 'profileImg': profileImg}

def createQuote(name, quote):
  is_verified, screen_name, user_name, profile_img = getTwitterInfo(name)
  author = createEntity(name, user_name, screen_name, profile_img)
  return {'author': author, 'text': quote}
  
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
