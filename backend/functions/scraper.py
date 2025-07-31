from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import unicodedata
import time
import requests
import re
import os
import json
import bs4

def imdb_scraper(imdb_link, serial, identifier=False):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--enable-unsafe-swiftshader')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)

    driver.get(imdb_link)
    time.sleep(2)

    title = driver.find_element(By.TAG_NAME, 'h1').text
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    full_image_dir = directory['video_full_image_dir']
    os.makedirs(full_image_dir, exist_ok=True)
    thumbnail_dir = directory['video_thumbnail_dir']
    os.makedirs(thumbnail_dir, exist_ok=True)
        
    try:
        description_tag = driver.find_element(By.CSS_SELECTOR, '[data-testid="plot"]')
        span_tags = description_tag.find_elements(By.TAG_NAME, 'span')
        description = ''
        for span in span_tags:
            if span.text.strip():
                description = span.text.strip()
                break
    except Exception as e:
        description = ''

    all_genres = []
    try:
        script_tag = driver.find_element(By.ID, '__NEXT_DATA__')
        json_data = json.loads(script_tag.get_attribute('innerHTML'))
        genres = json_data['props']['pageProps']['aboveTheFoldData']['genres']['genres']
        for genre in genres:
            all_genres.append(genre['text'])
    except Exception as e:
        print(f"Error extracting genres: {e}")
        all_genres = []

    all_interests = []
    try:
        interests = json_data['props']['pageProps']['aboveTheFoldData']['interests']['edges']
        for interest in interests:
            all_interests.append(interest['node']['primaryText']['text'])
    except Exception as e:
        print(f"Error extracting interests: {e}")
        all_interests = []

    rating = 0.0
    try:
        rating = json_data['props']['pageProps']['aboveTheFoldData']['ratingsSummary']['aggregateRating']
    except Exception as e:
        print(f"Error extracting rating: {e}")
        rating = 0.0

    age_rating = None
    try:
        age_rating = json_data['props']['pageProps']['aboveTheFoldData']['certificate']['rating']
    except Exception as e:
        print(f"Error extracting age rating: {e}")
        age_rating = None

    is_tv_series = False
    try:
        is_tv_series = json_data['props']['pageProps']['aboveTheFoldData']['titleType']['isSeries']
    except Exception as e:
        print(f"Error determining if it is a TV series: {e}")
        is_tv_series = False

    release_year = None
    full_release_date = None
    try:
        release_year = json_data['props']['pageProps']['aboveTheFoldData']['releaseYear']['year']
        release_date = json_data['props']['pageProps']['aboveTheFoldData']['releaseDate']
        full_release_date = f"{release_date['day']}-{release_date['month']}-{release_date['year']}"
    except Exception as e:
        print(f"Error extracting release date: {e}")
        release_year = None
        full_release_date = None

    runtime_duration = None
    try:
        runtime_duration = json_data['props']['pageProps']['aboveTheFoldData']['runtime']['displayableProperty']['value']['plainText']
    except Exception as e:
        print(f"Error extracting runtime duration: {e}")
        runtime_duration = None

    thumbnail_filename = serial
    try:
        thumbnail_url = driver.find_element(By.CSS_SELECTOR, '[data-testid="hero-media__poster"]').find_element(By.TAG_NAME, 'img').get_attribute('src')
        thumbnail_response = requests.get(thumbnail_url, headers={'User-Agent': options.arguments[0]})
        if identifier == True:
            pass
        else:
            with open(f'{thumbnail_dir}{thumbnail_filename}.jpg', 'wb') as f:
                f.write(thumbnail_response.content)
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
        
    json_ld = None
    try:
        script_tag = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
        json_ld = json.loads(script_tag.get_attribute('innerHTML'))
    except Exception as e:
        print(f"Error extracting JSON-LD script: {e}")

    full_image_file = serial
    try:
        full_image_url = json_ld.get('image', '')
        full_image_response = requests.get(full_image_url, headers={'User-Agent': options.arguments[0]})
        if identifier == True:
            pass
        else:
            with open(f'{full_image_dir}{full_image_file}.jpg', 'wb') as f:
                f.write(full_image_response.content)
    except Exception as e:
        full_image_file = None
        print(f"Error downloading thumbnail: {e}")

    breakers = [
        'Director',
        'Directors',
        'Stars',
        'Star',
        'Cast',
        'Casts',
        'Writer',
        'Writers',
        'Creator',
        'Creators'
    ]

    def extract_names_and_urls(primary_tags, breakers):
        result = []
        try:
            for primary_tag in primary_tags:
                if primary_tag.is_displayed():
                    sibling_tags = primary_tag.find_elements(By.XPATH, "following-sibling::*")

                    for sibling in sibling_tags:
                        text = sibling.text.strip()

                        if text in breakers:
                            break
                        
                        link_elements = sibling.find_elements(By.TAG_NAME, 'a')
                        
                        for link_element in link_elements:
                            name = link_element.text.strip()
                            url = link_element.get_attribute('href')

                            if name and url:
                                result.append({"name": name, "url": url})
                    
                    if result:
                        break
        except Exception as e:
            print(f"Error extracting names and URLs: {e}")
            result = []
        return result
    print('28')

    all_directors = extract_names_and_urls(driver.find_elements(By.XPATH, "//*[contains(text(), 'Director') or contains(text(), 'Directors')]"), breakers)
    all_writers = extract_names_and_urls(driver.find_elements(By.XPATH, "//*[contains(text(), 'Writer') or contains(text(), 'Writers')]"), breakers)
    all_stars = extract_names_and_urls(driver.find_elements(By.XPATH, "//*[contains(text(), 'Star') or contains(text(), 'Stars')]"), breakers)
    all_creators = extract_names_and_urls(driver.find_elements(By.XPATH, "//*[contains(text(), 'Creator') or contains(text(), 'Creators')]"), breakers)
    
    thumbnail_added = True if thumbnail_filename is not None else False
    full_image_added = True if full_image_file is not None else False
    
    popularity = 'N/A'
    if identifier == True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }


        response = requests.get(imdb_link, headers=headers)
        response.encoding = 'utf-8'
        html_content = response.text
        soup = bs4.BeautifulSoup(html_content, 'lxml')

        try:
            popularity_element = soup.find(attrs={'data-testid': 'hero-rating-bar__popularity__score'})
            if popularity_element:
                text = popularity_element.text.strip().replace(',', '')
                popularity = unicodedata.normalize('NFKD', text)
            else:
                popularity = 'N/A'
        except AttributeError:
            popularity = 'N/A'
            
    
    data = {
        'title': title,
        'description': description,
        'all_genres': all_genres,
        'main_genre': all_genres[0] if all_genres else None,
        'all_interests': all_interests,
        'rating': rating,
        'age_rating': age_rating,
        'is_tv_series': is_tv_series,
        'release_year': release_year,
        'full_release_date': full_release_date,
        'runtime_duration': runtime_duration,
        'thumbnail_url': thumbnail_url,
        'full_image_url': full_image_url,
        'all_directors': all_directors,
        'all_writers': all_writers,
        'all_stars': all_stars,
        'all_creators': all_creators,
        'all_directors_limited': [d['name'] for d in all_directors],
        'all_writers_limited': [w['name'] for w in all_writers],
        'all_stars_limited': [s['name'] for s in all_stars],
        'all_creators_limited': [c['name'] for c in all_creators],
        'thumbnail_added': thumbnail_added,
        'full_image_added': full_image_added,
        'thumbnail_location': directory['video_thumbnail_dir'],
        'full_image_location': full_image_dir,
        'popularity': popularity
    }

    driver.quit()

    return data
    

