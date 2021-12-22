import json
import pdb
import re
import unicodedata
import urllib

from bs4 import BeautifulSoup
import requests
import json

message_global = {
    "success_scrap": "User data scrapped successfully",
    "url_validation_error": "Please provide a valid url starting with https://www.fiverr.com/",
    "key_error": "Please send the the user profile url in 'url' key"
}


def _parse_html(get_response):
    soup = BeautifulSoup(get_response.content, "html.parser")
    return soup


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


def _get_reviews_as_buyer(soup):
    reviews_list = []
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i].text)
            # review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def _get_reviews_using_soup(soup):
    reviews_list = []
    p_tags_list = soup.find_all("p", {"class": "text-body-2"})
    if len(p_tags_list) < 1:
        return reviews_list
    for i in range(0, len(p_tags_list) - 1):
        if i % 2 == 0:  # showing every even p tag because p at odd tags contains information text
            review_text = str(p_tags_list[i].text)
            # review_text = _normalize_review(review_text)
            reviews_list.append(review_text)

    return reviews_list


def _get_data_using_soup(class_name, soup):
    try:
        text_data = soup.find(class_=class_name).text
        return str(text_data)
    except Exception as e:
        return "Not found"


def _get_langs(soup):
    langs_list = []
    try:
        p_tags_list = soup.find_all("div", {"class": "languages"})
        skills_html_list = p_tags_list[0].find_all("li")
        for skills in skills_html_list:
            langs_list.append(unicodedata.normalize("NFKD", skills.text).replace("  - Native/Bilingual", ""))
        return langs_list
    except Exception as e:
        empty_list = []
        return empty_list


# languages

def _get_skills(soup):
    skills_list = []
    p_tags_list = soup.find_all("div", {"class": "skills"})
    skills_html_list = p_tags_list[0].find_all("li")
    for skills in skills_html_list:
        skills_list.append(skills.text)
    return skills_list


def fetch_profile(url):
    if not validate_url(url):
        return _return_response({}, message_global.get("url_validation_error"), 0)
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)  # get response as html if calling an html page directly
        soup = _parse_html(response)
        langs_list = _get_langs(
            soup)  # call langs list and it returns a list of languages,pass the basic response object
        skills_list = _get_skills(soup)  # return list of skills
        average_review = _get_data_using_soup(classes.get("average_review"), soup)  # returns average average rating
        total_reviews = _get_data_using_soup(classes.get("total_reviews"), soup)  # returns total number of views
        if "k+" in total_reviews:  # if the reviews are like 1k+ look in div with below class
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(classes.get(
                "exact_review"), soup)  # look for exact number of reviews and return number of reviews
        about = _get_data_using_soup(classes.get("about_me"), soup)  # returns about me for the user profile
        reviews_list = _get_reviews_using_soup(soup)
        total_reviews = total_reviews.replace("(", "")  # normalize text
        total_reviews = total_reviews.replace(")", "")  # normalize text
        total_reviews = total_reviews.replace(" reviews", "")  # normalize text
        about = about[
                11:]  # remove the word description from the start of description, description is a 11 letter long word
        try:  # try to convert the string values i.e total number of reviews and average to int/float
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:  # if there is any exception keep data types to strings
            print(error)
        scrapped_data = {  # create the data object to be sent in response
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list,
            "skills": skills_list,
            "languages": langs_list
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"),
                                1)  # calling this method with return the response object with headers

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)  # if there is an exption return this object


def validate_url(url):
    target = "https://www.fiverr.com/"
    if target in url and target != url:
        return True
    else:
        return False


def lambda_handler(event, context):
    try:
        url_body = json.loads(event['body'])
        url = url_body["url"]
    except Exception as e:
        return _return_response({}, message_global.get("key_error"), 0)

    if not validate_url(url):
        return _return_response({}, message_global.get("url_validation_error"), 0)
    try:
        classes = {
            "average_review": 'rating-score rating-num',
            "total_reviews": 'ratings-count rating-count',
            "exact_review": "total-rating header-total-rating",
            "about_me": 'description',
        }
        response = _fetch_html_structure(url)  # get response as html if calling an html page directly
        soup = _parse_html(response)
        langs_list = _get_langs(soup)  # call langs list and it returns a list of languages,pass the basic response object
        skills_list = _get_skills(soup)  # return list of skills
        average_review = _get_data_using_soup(classes.get("average_review"),soup)  # returns average average rating
        total_reviews = _get_data_using_soup(classes.get("total_reviews"),soup)  # returns total number of views
        if "k+" in total_reviews:  # if the reviews are like 1k+ look in div with below class
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(classes.get(
                "exact_review"),soup)  # look for exact number of reviews and return number of reviews
        about = _get_data_using_soup(classes.get("about_me"),soup)  # returns about me for the user profile
        reviews_list = _get_reviews_using_soup(soup)
        total_reviews = total_reviews.replace("(", "")  # normalize text
        total_reviews = total_reviews.replace(")", "")  # normalize text
        total_reviews = total_reviews.replace(" reviews", "")  # normalize text
        about = about[
                11:]  # remove the word description from the start of description, description is a 11 letter long word
        try:  # try to convert the string values i.e total number of reviews and average to int/float
            total_reviews = total_reviews.replace(',', "")
            total_reviews = float(total_reviews)
            average_review = float(average_review)
        except Exception as error:  # if there is any exception keep data types to strings
            print(error)
        scrapped_data = {  # create the data object to be sent in response
            "total_projects_completed": total_reviews,
            "average_review": average_review,
            "total_reviews_count": total_reviews,
            "about_me": about,
            "reviews_list": reviews_list,
            "skills": skills_list,
            "languages": langs_list
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"),
                                1)  # calling this method with return the response object with headers

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)  # if there is an exption return this object


# print(fetch_profile("https://www.fiverr.com/rankterpriseuk"))
