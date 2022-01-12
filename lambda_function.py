import json
import pdb
import re
import urllib
from bs4 import BeautifulSoup
import requests
import json
import validators

message_global = {
    "success_scrap": "User data scrapped successfully",
    "url_validation_error": "Please provide a valid url starting with https://www.fiverr.com/"
}


def _return_response(user_profile, msg, success):
    response_object = {"statusCode": 200,
                       "headers": {
                           "Content-Type": "application/json"
                       },
                       "body": json.dumps({
                           "data": {"success": success, "user_profile": user_profile, "message": msg}
                       }),
                       }
    return response_object


def _fetch_html_structure(url):
    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    return response


def _get_reviews_as_buyer(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, "html.parser")
    the_latest = soup.find(class_="reviews-package is-collapsed")
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i].text)
            # review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def _get_reviews_using_soup(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, "html.parser")
    the_latest = soup.find(class_="review-list")
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i].text)
            # review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def _get_data_using_soup(response, class_name):
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        text_data = soup.find(class_=class_name).text
        return str(text_data)
    except Exception as e:
        return "Not found"


def validate_url(url):
    target = "https://www.fiverr.com/"
    if target in url:
        return True
    else:
        return False


def _fetch_starts_and_review(response):
    reviews_list = []
    soup = BeautifulSoup(response.content, "html.parser")
    the_latest = soup.find(class_="review-list")

    if len(the_latest) < 1:
        return reviews_list
    else:
        for i in the_latest:
            single_list = i.find(class_="review-item")
            star_counts = single_list.find(class_="total-rating-out-five text-display-7")
            review_text = single_list.find(class_="text-body-2")
            reviews_list.append({"review_text":review_text.text,"review_rating":star_counts.text})
    return reviews_list


def fetch_profile(url):
    valid = validators.url(url)
    if not valid:
        url = "https://www." + url
    print("Recieved URL is" + " " + url)
    if not validate_url(url):
        return _return_response({}, message_global.get("url_validation_error"), 0)
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)
        reviews_with_ratings=_fetch_starts_and_review(response)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        reviews_list = _get_reviews_using_soup(response)
        total_reviews = total_reviews.replace("(", "")
        total_reviews = total_reviews.replace(")", "")
        total_reviews = total_reviews.replace(" reviews", "")
        about = about[11:]
        try:
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:
            print(error)
        scrapped_data = {
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list,
            "reviews_with_rating":reviews_with_ratings
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"), 1)

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)






def lambda_handler(event, context):
    url_body = json.loads(event['body'])
    get_url = url_body["url"]
    url = get_url
    valid=validators.url(url)
    if not valid:
        url="https://www."+url
    print("Recieved URL is"+" "+url)
    if not validate_url(url):
        return _return_response({}, message_global.get("url_validation_error"), 0)
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        reviews_list = _get_reviews_using_soup(response)
        total_reviews = total_reviews.replace("(", "")
        total_reviews = total_reviews.replace(")", "")
        total_reviews = total_reviews.replace(" reviews", "")
        about = about[11:]
        try:
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:
            print(error)
        scrapped_data = {
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"), 1)

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)


