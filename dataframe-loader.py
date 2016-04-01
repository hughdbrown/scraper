#!/usr/bin/env python3
from __future__ import print_function

import pandas as pd
import simplejson


def json_objects(filename):
    # Streams dictionaries from a file that has one JSON object per line
    with open(filename) as f:
        for line in f:
            yield simplejson.loads(line)


def main(filename):
    # Creates a DataFrame from a file that has a stream of JSON objects
    df = pd.DataFrame(list(json_objects(filename)))
    print(df.head())
    print(df.describe())


if __name__ == '__main__':
    main("results.txt")
