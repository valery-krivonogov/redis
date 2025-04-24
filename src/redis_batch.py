# -*- coding: utf-8 -*-
import redis
from itertools import izip_longest

# iterate a list in batches of size n
def batcher(iterable, n):
    args = [iter(iterable)] * n
    return izip_longest(*args)


client = redis.Redis( host='localhost', port=10001, password='admin@1234', db=0)



pipeline = client.pipeline()
for key in client.scan_iter("sample_bicycle:*"):
    pipeline.json().get(key)
results = pipeline.execute()
for r in results:
    print(r)


"""

# in batches of 500 delete keys matching user:*
for keybatch in batcher(r.scan_iter('user:*'),500):
    r.delete(*keybatch)
"""    