import argparse
import json
import os
import pickle

from bs4 import BeautifulSoup
import dateparser
import requests

from common import AllocineReview

ROOT_URL = "http://www.allocine.fr"
DEFAULT_OUTPUT_PATH = "allocine_dataset/pickle"

def format_text(comment):
    output_text = ""
    for content in comment.contents:        
        content_str = str(content)        
        content_soup = BeautifulSoup(content_str, 'html.parser')
        spoiler = content_soup.find("span", {"class": "spoiler-content"})
        if spoiler:
            output_text += spoiler.text.strip()
        else:
            output_text += content_str.strip()
    return output_text

def parse_page(page_url):    
    ratings, reviews, dates, helpfuls = [], [], [], []
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')   

    # We iterate on review cards to avoid other reviews (Meilleurs films à l'affiche)
    for rating_parent in soup.find_all("div", {"class": "review-card-review-holder"}):
        rating_raw = rating_parent.find("span", {"class": "stareval-note"})  # <span class="stareval-note">4,0</span>
        rating_str = str(rating_raw.contents)[2:5] # "4,0"
        rating = float(rating_str.replace(',', '.')) # 4.0        
        ratings.append(rating)

    for review_raw in soup.find_all("div", attrs={"class": "content-txt review-card-content"}):        
        review_text = format_text(review_raw)       
        reviews.append(review_text) 

    for date_raw in soup.find_all("span", attrs={"class": "review-card-meta-date light"}):
        date_str = date_raw.text.strip() # Publiée le 24 mai 2011
        date_str = date_str[11:] # 24 mai 2011
        date = dateparser.parse(date_str).date() # 2011-05-24
        dates.append(date)

    for helpful_raw in soup.find_all("div", {"class": "reviews-users-comment-useful js-useful-reviews"}):
        helpful_str = helpful_raw.get("data-statistics") # "{"helpfulCount":21,"unhelpfulCount":0}"
        helpful_dic = json.loads(helpful_str) # {"helpfulCount": 21, "unhelpfulCount": 0}
        helpful = [helpful_dic["helpfulCount"], helpful_dic["unhelpfulCount"]] # [21, 0]        
        helpfuls.append(helpful)    

    assert(len(ratings) == len(reviews) == len(dates) == len(helpfuls)) 

    return ratings, reviews, dates, helpfuls

def parse_film(film_url):
    r = requests.get(film_url)
    if r.status_code == requests.codes.not_found:
        # if url is not foud : film does not exist
        return None
    elif len(r.history) > 1: 
        # if there is more than one element in history, the request was redirected
        # and that means there are no "critiques/spectateurs" page      
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    
    #print("> Film url: " + film_url)
    
    # Find number of pages
    pagination = soup.find("div", {"class": "pagination-item-holder"})
    if pagination:
        #print(pagination)
        pages = pagination.find_all("span")
        #print([page.text for page in pages])
        page_number = int([page.text for page in pages][-1])
    else:
        page_number = 1
    #print("  pages: " + str(page_number))
    
    # Iterate over pages
    out_reviews = [] #defaultdict(tuple)

    for page_id in range(0, page_number):            
        page_url = url = "{film_url}/?page={page_num}".format(
            film_url=film_url,
            page_num=page_id+1)
        ratings, reviews, dates, helpfuls = parse_page(page_url)
        
        for rating, review_text, date, helpful in zip(ratings, reviews, dates, helpfuls):
            allocine_review = AllocineReview(
                rating, 
                review_text, 
                date, 
                helpful
            )
            out_reviews.append(allocine_review)            
    return out_reviews
            
    # TODO => only keep x comments (random ?)

def parse_allocine(root_url, start_id, max_id):   
    #FILM_ID = 22092
    reviews = {}
    for film_id in range(start_id, max_id+1):
        
        if film_id % 100 == 0:
            print("Progress: {}/{}".format(film_id, max_id))
            
        film_url = "{root}/film/fichefilm-{film_id}/critiques/spectateurs".format(
            root=root_url,
            film_id=film_id
        )
        film_reviews = parse_film(film_url)
        if film_reviews:
            reviews[film_id] = film_reviews
    
    return reviews

parser = argparse.ArgumentParser()
parser.add_argument('--root-url', type=str, default=ROOT_URL)
parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_PATH)
parser.add_argument('--start-id', type=int, default=0)
parser.add_argument('--max-id', type=int, required=True)
args = parser.parse_args()

if __name__ == '__main__':    
    allocine_reviews = parse_allocine(args.root_url, args.start_id, args.max_id)

    out_file = "allocine_{}_{}.pickle".format(args.start_id, args.max_id)
    out_path = os.path.join(args.output, out_file)

    with open(out_path, 'wb') as handle:
        pickle.dump(allocine_reviews, handle, protocol=pickle.HIGHEST_PROTOCOL)