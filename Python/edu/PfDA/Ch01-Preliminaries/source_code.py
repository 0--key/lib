import json

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from collections import defaultdict, Counter


# sudo apt-get install python-numpy python-pandas

def get_counts2(sequence):
    counts = defaultdict(int)  # values will initialize to 0
    for x in sequence:
        counts[x] += 1
    return counts


def top_counts(count_dict, n=10):
    value_key_pairs = [(count, tz) for tz, count in count_dict.items()]
    value_key_pairs.sort()
    return value_key_pairs[-n:]

print('Hi there')

path = 'pydata-book/ch02/usagov_bitly_data2012-03-16-1331923249.txt'
records = [json.loads(line) for line in open(path)]
print(records[0])
time_zones = [rec['tz'] for rec in records if 'tz' in rec]
# print set(time_zones), len(set(time_zones))

counts = Counter(time_zones)
print(counts.most_common(10))
