from collections import defaultdict
import json
import re
import sys

from bs4 import BeautifulSoup
import dateparser
from etaprogress.progress import ProgressBar
import requests

###################
# SCRAP FILM LIST #
###################

def parse_list_page(page_url):
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    films = soup.find_all("a", {"class": "meta-title-link"})
    return [f.get('href') for f in films]


def get_film_urls(root_url, max_page=None):
    list_url = "{root}/films".format(root=root_url)
    r = requests.get(list_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    pagination = soup.find("div", {"class": "pagination-item-holder"})
    pages = pagination.find_all("span")
    page_number = int([page.text for page in pages][-1])

    if max_page:
        if max_page > page_number:
            print("Error: max_page is greater than the actual number of pages")
            return []
        else:
            page_number = max_page

    out_urls = []
    bar = ProgressBar(page_number, max_width=40)

    for page_id in range(1, page_number+1):
        # Log progress
        bar.numerator = page_id
        print(bar, end='\r')
        sys.stdout.flush()

        # Extend out list with new urls
        page_url = "{list_url}/?page={page_num}".format(
            list_url=list_url,
            page_num=page_id)
        film_urls = parse_list_page(page_url)
        out_urls.extend(film_urls)

    return out_urls


###################
# SCRAP FILM PAGE #
###################


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


def parse_film_page(page_url):
    ratings, reviews, dates, helpfuls = [], [], [], []
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # We iterate on reviews to avoid other reviews (Meilleurs films à l'affiche)
    for rating_parent in soup.find_all("div", {"class": "review-card-review-holder"}):
        rating_raw = rating_parent.find("span", {"class": "stareval-note"})  # <span class="stareval-note">4,0</span>
        rating_str = str(rating_raw.contents)[2:5]  # "4,0"
        rating = float(rating_str.replace(',', '.'))  # 4.0
        ratings.append(rating)

    for review_raw in soup.find_all("div", attrs={"class": "content-txt review-card-content"}):
        review_text = format_text(review_raw)
        reviews.append(review_text)

    for date_raw in soup.find_all("span", attrs={"class": "review-card-meta-date light"}):
        date_str = date_raw.text.strip()  # Publiée le 24 mai 2011
        date_str = date_str[11:]  # 24 mai 2011
        date = dateparser.parse(date_str).date()  # 2011-05-24
        dates.append(date)

    for helpful_raw in soup.find_all("div", {"class": "reviews-users-comment-useful js-useful-reviews"}):
        helpful_str = helpful_raw.get("data-statistics")  # "{"helpfulCount":21,"unhelpfulCount":0}"
        helpful_dic = json.loads(helpful_str)  # {"helpfulCount": 21, "unhelpfulCount": 0}
        helpful = [helpful_dic["helpfulCount"], helpful_dic["unhelpfulCount"]]  # [21, 0]
        helpfuls.append(helpful)

    return ratings, reviews, dates, helpfuls


def parse_film(film_url, max_reviews=None):
    ratings, reviews, dates, helpfuls = [], [], [], []
    r = requests.get(film_url)
    if r.status_code == requests.codes.not_found:
        # if url is not foud : film does not exist
        print("Error code {}. Skipping: {}".format(
            r.status_code,
            film_url
        ))
        return None
    elif len(r.history) > 1:
        # if there is more than one element in history, the request was redirected
        # and that means there are no "critiques/spectateurs" page
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # print("> Film url: " + film_url)

    # Find number of pages
    pagination = soup.find("div", {"class": "pagination-item-holder"})
    page_number = 1
    if pagination:
        pages = pagination.find_all("span")
        page_number = int([page.text for page in pages][-1])

    # print("  pages: " + str(page_number))

    # Iterate over pages
    for page_id in range(1, page_number+1):
        page_url = "{film_url}/?page={page_num}".format(
            film_url=film_url,
            page_num=page_id)
        p_ratings, p_reviews, p_dates, p_helpfuls = parse_film_page(page_url)

        ratings.extend(p_ratings)
        reviews.extend(p_reviews)
        dates.extend(p_dates)
        helpfuls.extend(p_helpfuls)

        if max_reviews and len(ratings) > max_reviews:
            return (ratings[:max_reviews], reviews[:max_reviews],
                    dates[:max_reviews], helpfuls[:max_reviews])

    return (ratings, reviews, dates, helpfuls)


def get_film_reviews(root_url, urls, max_reviews_per_film=None):

    allocine_dic = defaultdict(list)
    bar = ProgressBar(len(urls), max_width=40)

    for i, url in enumerate(urls):
        # Log progress
        bar.numerator = i + 1
        print(bar, end='\r')
        sys.stdout.flush()

        film_id = re.findall(r'\d+', url)[0]
        film_url = "{root}/film/fichefilm-{film_id}/critiques/spectateurs".format(
            root=root_url,
            film_id=film_id
        )

        parse_output = parse_film(film_url, max_reviews_per_film)

        if parse_output:
            ratings, reviews, dates, helpfuls = parse_output

            # Rarely happens
            if not(len(ratings) == len(reviews) == len(dates) ==
                   len(helpfuls)):
                print("Error: film-url: " + film_url)
                continue

            allocine_dic['film-url'].extend(len(ratings)*[film_url])
            allocine_dic['rating'].extend(ratings)
            allocine_dic['review'].extend(reviews)
            allocine_dic['date'].extend(dates)
            allocine_dic['helpful'].extend([h[0] for h in helpfuls])
            allocine_dic['unhelpful'].extend([h[1] for h in helpfuls])

    return allocine_dic
