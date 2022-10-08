from api.parser import get_html
from bs4 import BeautifulSoup
import requests
import random

def get_articles(category):
    page_content = get_html("https://www.popsci.com/")
    homepage_secondary1 = page_content.find_all('section', class_ = "col col-12 col-md-12 col-lg-6 flex-basic-2 article-section")
    homepage_secondary2 = page_content.find_all('section', class_ = "col-6 col-md-12 col-lg-3 four-cols flex-basic-4")
    
    a_tags = []

    if("science" in category):
        
        a_tags += homepage_secondary1[0].find_all('a', href=True)
    if("tech" in category):
        a_tags += homepage_secondary1[1].find_all('a', href=True)
    if("space" in category):
        a_tags += homepage_secondary2[0].find_all('a', href=True)
    if("lifehacks" in category):
        a_tags += homepage_secondary2[1].find_all('a', href=True)
    if("animals" in category):
        a_tags += homepage_secondary2[2].find_all('a', href=True)
    if("health" in category):
        a_tags += homepage_secondary2[3].find_all('a', href=True)
    if(category=="default"):
        a_tags = page_content.find('div',class_="article-container featured_story Article-featuredStory--oneColumn row").find_all('a', href=True)
        for h1 in homepage_secondary1:
            a_tags += h1.find_all('a', href=True)
        for h2 in homepage_secondary2:
            a_tags += h2.find_all('a', href=True)
    else:
        if(len(a_tags < 5)):
            a_tags+=page_content.find('div',class_="article-container featured_story Article-featuredStory--oneColumn row").find_all('a', href=True)[0]
    
    links = []
    for a in a_tags:
        if a['href'] not in links and a.get('class') is None and '/popsci-plus/' not in a['href'] and '/category/' not in a['href']:
            links.append(a['href'])
            # if(len(links)==5):
            #     break

    returned_links = []

    for i in range(5):
        rand_num = random.randint(0, len(links)-1)
        returned_links.append(links[rand_num])
        links.remove(links[rand_num])

    return returned_links

def get_info(urls):
    return_info = []
    for u in urls:
        return_info.append(get_title_picture(u))

    return return_info

def get_title_picture(url):
    page = requests.get(url)
    page_content = BeautifulSoup(page.content, 'html.parser')
    publisher = page_content.find('img', class_='header__logo').get("alt")
    header = page_content.find('div', class_='Article-header')
    title = header.find('h1', class_='u-entryTitle').get_text()
    image_html = page_content.findAll('img', class_ = 'SingleImage-image Article-thumbnail wp-post-image')[0]
    image = image_html.get("src")
    return {'_id': '','URL': url, 'author': '', 'time': '', 'title': title, 'subtitle': '', 'image': image, 'publisher': publisher, 'visitedCnt': '', 'tweetNum': '', 'numWords': 0, 'sections': '', 'updatedAt': ''}


def get_search_results(url):
    page = requests.get(url)
    page_content = BeautifulSoup(page.content, 'html.parser')
    cards = page_content.find_all('div', class_="search-item col-lg-3 col-md-6 col-sm-12 d-flex align-items-stretch")
    results = []
    for c in cards:
        title = c.find('h5', class_="card-title").get_text()
        image = c.find('img', class_ ="card-img-top article-image u-image-16-9").get_text()
        url_card = c.find('a', class_="article-item__title").get('href')
        results.append({'URL': url_card, 'title': title, 'image': image,})
        if(len(results)>5):
            break
    return results