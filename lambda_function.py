import json
import pdb
import re
import time
import urllib
from bs4 import BeautifulSoup
import requests
import json
import validators
import urllib3
http = urllib3.PoolManager()
scrap_api={
    "api_key":"11adcc17388195658fe18d63a4cb715e",
    "url":"http://api.scraperapi.com?api_key=11adcc17388195658fe18d63a4cb715e&url="
}

def _fetch_html_structure_using_serive(url):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    response = http.request('GET', url,headers=header)
    return response.data
    # #
    # response = requests.get(scrap_api["url"]+url)
    # # print(response.status_code)
    # return response


message_global = {
    "success_scrap": "User data scrapped successfully",
    "url_validation_error": "Please provide a valid url starting with https://fiverr.com/",
    "url_not_exist":"This fiverr profile url doesn't exit"
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
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ur-PK;q=0.8,ur;q=0.7,zh-CN;q=0.6,zh;q=0.5,hi;q=0.4",
        "Dnt": "1",
        "Sec-Ch-Ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Linux\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    }
    response = http.request('GET', url,headers=header)
    return response.data
    #comment above lines i.e from 47 to 63 and use the below two lines if you want to use scrap api service for scrapping it will prevent scrapper from being blocked.
    # response = requests.get(scrap_api["url"] + url)   /
    # return response





def validate_profile_url(response,profile_url):
    # profile_title=profile_url.split("/")[1]
    profile_url_list=profile_url.split("/")
    profile_title=profile_url_list[-1]
    soup = BeautifulSoup(response, "html.parser")
    the_title = soup.find("title")
    the_title=the_title.text
    if profile_title in the_title:
        return True
    else:
        print("This was the page title="+the_title)
        print("This was the profile title="+profile_title)
        return False


def _get_reviews_as_buyer(response):
    reviews_list = []
    soup = BeautifulSoup(response, "html.parser")
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
    soup = BeautifulSoup(response, "html.parser")
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
        soup = BeautifulSoup(response, "html.parser")
        text_data = soup.find(class_=class_name).text
        return str(text_data)
    except Exception as e:
        return str(0)

def default_about_me_check(about_me):
    if "Just add your touch" in about_me:
        return ""
    else:
        return about_me

def validate_url(url):
    question_mark="?"
    if question_mark in url:
        url_list = url.split("?")
        url = url_list[0]
    target = "https://fiverr.com/"
    target_two = "https://www.fiverr.com/"
    if target in url or target_two in url:
        return True
    else:
        return False


def _fetch_starts_and_review(response):
    reviews_list = []
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        the_latest = soup.find(class_="review-list")

        if len(the_latest) < 1:
            return reviews_list
        else:
            for i in the_latest:
                single_list = i.find(class_="review-item")
                star_counts = single_list.find(class_="total-rating-out-five text-display-7")
                review_text = single_list.find(class_="text-body-2")
                reviews_list.append({"review_text": review_text.text, "review_rating": star_counts.text})
        return reviews_list
    except:
        return []


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
        time.sleep(0.0001*50)
        response = _fetch_html_structure(url)
        if not validate_profile_url(response,url):
            return _return_response({}, message_global.get("url_not_exist"), 0)
        else:
            pass
        reviews_with_ratings = _fetch_starts_and_review(response)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        about=default_about_me_check(about)
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
            "reviews_with_rating": reviews_with_ratings
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"), 1)

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)


def lambda_handler(event, context):
    url_body = json.loads(event['body'])
    get_url = url_body["url"]
    url = get_url
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
        time.sleep(0.0001 * 500)
        response = _fetch_html_structure(url)
        if not validate_profile_url(response, url):
            return _return_response({}, message_global.get("url_not_exist"), 0)
        else:
            pass
        reviews_with_ratings = _fetch_starts_and_review(response)
        average_review = _get_data_using_soup(response, classes.get("average_review"))
        total_reviews = _get_data_using_soup(response, classes.get("total_reviews"))
        if "k+" in total_reviews:
            print("Fetching exact reviews")
            total_reviews = _get_data_using_soup(response, classes.get("exact_review"))
        about = _get_data_using_soup(response, classes.get("about_me"))
        about = default_about_me_check(about)
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
            "reviews_with_rating": reviews_with_ratings
        }

        return _return_response(scrapped_data, message_global.get("success_scrap"), 1)

    except Exception as error:
        error_string = str(error)
        return _return_response({}, error_string, 0)




# response=_fetch_html_structure_using_serive("https://www.fiverr.com/")
# print(response)
if __name__ == '__main__':
    for i in range(1,10):
        response = fetch_profile("https://www.fiverr.com/webgirl80")
        print(response)
