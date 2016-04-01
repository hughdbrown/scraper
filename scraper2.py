#!/usr/bin/env python3
from __future__ import print_function

from sys import stderr, stdout, exit
from time import sleep
from datetime import datetime
import os.path
import glob

from bs4 import BeautifulSoup
import requests
import simplejson

from local import ROOT2


def extract_attrs(data):
    def key(div):
        return div.select("div.m-attr-label")[0].text
    def value(div):
        return float(div.select("div.m-attr-bar")[0]["style"].split(':')[1].replace('%', ''))
    soup = BeautifulSoup(data.encode("utf-8"))
    divs = soup.select("div.m-histogram-item-wrapper")
    return {key(div): value(div) for div in divs}


def strip_attributes(filename):
    s = datetime.now()
    strain = filename.split("/")[-1]
    with open(filename) as f:
        data = f.read()
        d = extract_attrs(data)
        d["strain"] = strain
    e = datetime.now()
    print("{0} {1} {2}".format('-' * 30, strain, (e - s)), file=stderr)
    return d


def main():
    path = os.path.join("data", "attrib", "*")
    results = [strip_attributes(filename) for filename in glob.glob(path)]
    with open("results.txt", "w") as f:
        for result in results:
            f.write(simplejson.dumps(result) + "\n")


def premain():
    with open("strains.txt") as f:
        strains = [line.strip() for line in f]
    print("{0} strains".format(len(strains)), file=stderr)

    for i, strain_path in enumerate(strains):
        s = datetime.now()
        try:
            url = ROOT2.format(strain_path)
            print(url, file=stderr)
            r = requests.get(url)
            data = r.text
            strain = strain_path.split("/")[2]
            try:
                path = os.path.join("data", "attrib", strain)
                with open(path, "w") as f:
                    f.write(data)
            except Exception as exc:
                print("You need a directory 'data/attrib'", file=stderr)
                print(exc, file=stderr)
                exit(1)
        except Exception as exc:
            print("{0}: {1}".format(strain, exc), file=stderr)
            break
        e = datetime.now()
        print("{0} {1} of {2}: {3} {4}".format('-' * 30, i, len(strains), strain, (e - s)), file=stderr)
        sleep(1.2)


if __name__ == '__main__':
    # premain()
    main()
