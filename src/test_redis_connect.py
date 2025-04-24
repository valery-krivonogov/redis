# -*- coding: utf-8 -*-
import redis
import time

client = redis.Redis( host='localhost', port=10001, password='admin@1234', db=0)

ms = time.time_ns()
rec = client.json().get("sample_bicycle:1001")
delta =  time.time_ns() - ms
print(rec)
print(round(delta/1000), "micro sec")