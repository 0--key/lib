from pandas import DataFrame, Series
import pandas as pd

path = 'pydata-book/ch02/usagov_bitly_data2012-03-16-1331923249.txt'
records = [json.loads(line) for line in open(path)]
frame = DataFrame(records)

print frame['tz'][:10]  # unsorted
print frame['tz'].value_counts()
print '\n#   #\n'
clean_tz = frame['tz'].fillna('Missing')
clean_tz[clean_tz == ''] = 'Unknown'
tz_counts = clean_tz.value_counts()
print tz_counts[:10]
