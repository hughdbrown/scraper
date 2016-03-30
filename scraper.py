#!/usr/bin/env python
from __future__ import print_function

from sys import stderr
from time import sleep

from bs4 import BeautifulSoup
import requests

from local import ROOT

PREFIXES = (
    "/Sativa",
    "/Indica",
    "/Hybrid",
)


def get_strains():
    with open("strains.txt") as f:
        soup = BeautifulSoup(f.read(), "lxml")
        href_iter = (a["href"] for a in soup.find_all("a", href=True))
        return [h for h in href_iter if h.startswith(PREFIXES)]


def get_review(data):
    sleep(1.5)
    soup = BeautifulSoup(data.encode('utf-8'), "lxml")

    # Find the name of the strain
    h1_iter = [h for h in soup.find_all("h1")]
    strain_name = h1_iter[0].text.strip()

    # Find the user names
    href_iter = (
        a["href"]
        for h3 in soup.find_all("h3", {"class": "copy--xl padding-rowItem no-margin"})
        for a in h3.find_all("a", href=True)
    )
    users = [href.replace("/profile/", "") for href in href_iter if href.startswith("/profile")]

    # Find the rating
    span_iter = (s for s in soup.find_all("span", {"class" : "squeeze"}))
    rating_iter = (s["star-rating"] for s in span_iter)
    ratings = [float(rating) for rating in rating_iter]
    print("Read {0} users and {1} ratings".format(len(users), len(ratings)), file=stderr)
    return strain_name, list(zip(users, ratings))


def get_pages(root):
    review_page = ROOT.format(root)
    print(review_page, file=stderr)
    r = requests.get(review_page)
    name, reviews = get_review(r.text)
    print(reviews, file=stderr)
    page = {
        "name": name,
        "reviews": reviews,
    }
    for i in range(1, 1000):
        url = "{0}?page={1}".format(review_page, i)
        print(url, file=stderr)
        r = requests.get(url)
        if not r.ok:
            print("Bad request for {0}".format(url), file=stderr)
            break
        _, reviews = get_review(r.text)
        if reviews:
            page["reviews"] += reviews
            print(reviews, file=stderr)
        else:
            print("{0} reviews for {1}".format(len(page["reviews"]), root), file=stderr)
            break
    return page


def main():
    pages = get_strains()
    for page in pages:
        results = get_pages(page)
        name, reviews = results["name"], results["reviews"]
        for user, rating in reviews:
            print('"{0}","{1}",{2}'.format(name, user, rating))


if __name__ == '__main__':
    main()
