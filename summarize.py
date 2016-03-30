#!/usr/bin/env python3.5
from __future__ import print_function

from glob import glob
from collections import defaultdict
import csv
from string import punctuation


def report():
    # Get expected strains
    with open("strains.txt") as f:
        strains = [s.strip().split('/')[2].replace('-', ' ') for s in f]

    # Summarize files
    s = defaultdict(list)
    u = defaultdict(list)
    su = defaultdict(list)
    for filename in glob("user*.txt"):
        print(filename)
        with open(filename) as f:
            c = csv.reader(f)
            try:
                for strain, user, rating in c:
                    s[strain].append((user, rating))
                    u[user].append((strain, rating))
                    su[(strain, user)].append(rating)
            except Exception as exc:
                print("Exception in {0}: {1}".format(filename, exc))
                pass

    # Report on results
    all_ratings = sum(len(v) for v in su.values())
    duplicated_ratings = sum(len(r) - 1 for r in su.values())
    print("All ratings: {0}".format(all_ratings))
    print("Duplicate ratings: {0}".format(duplicated_ratings))
    print("Unique ratings: {0}".format(all_ratings - duplicated_ratings))
    print("Unique strains: {0}".format(len(s)))
    print("Unique users: {0}".format(len(u)))

    # Print the missing strains
    #print("Missing strains:")
    #for s in sorted(set(s.strip(punctuation) for s in strains) - set(k.lower()  for k in s.keys())):
    #    print(s)

if __name__ == '__main__':
    report()
