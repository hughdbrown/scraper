#!/usr/bin/env python3.5
from __future__ import print_function

from sys import stderr, stdout
from time import sleep
from datetime import datetime
import re

from bs4 import BeautifulSoup
import requests

from local import ROOT, PREFIXES


USER_REGEX = re.compile(r'.*profile/(.*)$')

def get_strains():
    with open("strains.html") as f:
        soup = BeautifulSoup(f.read(), "lxml")
        href_iter = (a["href"] for a in soup.find_all("a", href=True))
        return [h for h in href_iter if h.startswith(PREFIXES)]


def get_review(data):
    soup = BeautifulSoup(data.encode('utf-8'), "lxml")

    # Find the name of the strain
    h1_iter = [h for h in soup.find_all("h1")]
    strain_name = h1_iter[0].text.strip().replace(" Reviews", "")

    # Find the user names
    users = [USER_REGEX.match(a["href"]).group(1) for a in soup.select('a.no-color')]

    # Find the rating
    ratings = [float(s["star-rating"]) for s in soup.select('.squeeze')]

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
        if not reviews or len(reviews) < 8:
            print("{0} reviews for {1}".format(len(page["reviews"]), root), file=stderr)
            break
        else:
            sleep(1.5)
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

    return page


def save_pages(pages):
    print("Number of strains: {0}".format(len(pages)), file=stderr)
    with open("strains.txt", "w") as f:
        f.write("\n".join(pages) + "\n")


def read_pages():
    with open("strains.txt") as f:
        return [page.strip() for page in f]


def main():
    # pages = get_strains()
    # save_pages(pages)
    pages = read_pages()
    empty, redo = [], []
    for i, page in enumerate(pages):
        print("{0}: {1} of {2}".format(page, i, len(pages)), file=stderr)
        s = datetime.now()
        results = get_pages(page)
        e = datetime.now()
        name, reviews = results["name"], results["reviews"]
        if reviews:
            try:
                for user, rating in reviews:
                    print('"{0}","{1}",{2}'.format(name, user, rating))
                stdout.flush()
            except Exception as exc:
                print("*** Exception on {0}: {1}".format(page, exc), file=stderr)
                redo.append(page)
        else:
            empty.append(page)
        print("Elapsed time: {0}".format(e - s), file=stderr)
        print("-" * 30, file=stderr)

    if redo:
        print("Rerun these pages:", file=stderr)
        for page in sorted(redo):
            print(page, file=stderr)

    if empty:
        print("Empty pages:", file=stderr)
        for page in sorted(empty):
            print(page, file=stderr)

if __name__ == '__main__':
    main()
