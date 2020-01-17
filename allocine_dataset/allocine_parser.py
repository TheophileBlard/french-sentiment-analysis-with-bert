import argparse
from collections import defaultdict
import json
import os
import sys

from bs4 import BeautifulSoup
import dateparser
from etaprogress.progress import ProgressBar
import pandas as pd
import requests

ROOT_URL = "http://www.allocine.fr"
DEFAULT_OUTPUT_PATH = "pickle"


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

    assert(len(ratings) == len(reviews) == len(dates) == len(helpfuls))

    return ratings, reviews, dates, helpfuls


def parse_film(film_url):
    ratings, reviews, dates, helpfuls = [], [], [], []
    r = requests.get(film_url)
    if r.status_code == requests.codes.not_found:
        # if url is not foud : film does not exist
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
    for page_id in range(0, page_number):
        page_url = "{film_url}/?page={page_num}".format(
            film_url=film_url,
            page_num=page_id+1)
        p_ratings, p_reviews, p_dates, p_helpfuls = parse_page(page_url)

        ratings.extend(p_ratings)
        reviews.extend(p_reviews)
        dates.extend(p_dates)
        helpfuls.extend(p_helpfuls)

    return (ratings, reviews, dates, helpfuls)


def parse_allocine(root_url, start_id, max_id):
    allocine_dic = defaultdict(list)
    bar = ProgressBar(max_id-start_id+1, max_width=40)
    for film_id in range(start_id, max_id+1):

        bar.numerator = film_id - start_id
        print(bar, end='\r')
        sys.stdout.flush()

        film_url = "{root}/film/fichefilm-{id}/critiques/spectateurs".format(
            root=root_url,
            id=film_id
        )

        parse_output = parse_film(film_url)

        if parse_output:
            ratings, reviews, dates, helpfuls = parse_output
            allocine_dic['film-id'].extend(len(ratings)*[film_id])
            allocine_dic['rating'].extend(ratings)
            allocine_dic['review'].extend(reviews)
            allocine_dic['date'].extend(dates)
            allocine_dic['helpful'].extend([h[0] for h in helpfuls])
            allocine_dic['unhelpful'].extend([h[1] for h in helpfuls])

    return allocine_dic


parser = argparse.ArgumentParser()
parser.add_argument('--root-url', type=str, default=ROOT_URL)
parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_PATH)
parser.add_argument('--start-id', type=int, default=1)
parser.add_argument('--end-id', type=int, required=True)
args = parser.parse_args()

if __name__ == '__main__':
    out_file = "allocine_{}_{}.pickle".format(args.start_id, args.end_id)
    out_path = os.path.join(args.output, out_file)

    allocine_dic = parse_allocine(args.root_url, args.start_id, args.end_id)

    # Create a pandas DataFrame and save it to disk as a picle file
    df = pd.DataFrame.from_dict(allocine_dic)
    df.to_pickle(out_path)
