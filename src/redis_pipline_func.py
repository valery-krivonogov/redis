# -*- coding: utf-8 -*-
import redis
from redis.commands.json.path import Path
import time

client = redis.Redis( host='localhost', port=10001, password='admin@1234', db=0)
show_read = False
pipeline = client.pipeline()


def exec_pipe (pl, mode, scn):
    ms = time.time_ns()
    res = pl.execute()
    delta =  time.time_ns() - ms
    print(scn, mode, round(delta/1000), "microsec")
    return res

# SORT LIST
part = "myTestZlist"
for m in range(1,2000):
    obj = {'member score is '+str(m) : m*5}
    pipeline.zadd(part+":scr", obj)

results = exec_pipe(pipeline, "set", part)

ms = time.time_ns()
res = client.zrange(part+":scr", 0, -1, withscores=True)
delta =  time.time_ns() - ms
if show_read:
    print(res)
print(part, "get", round(delta/1000), "microsec")

# POST
part = "myTestQuery"
for m in range(1,2000):
    for p in range(20):
        pipeline.rpush(part+":"+str(m)+":post", 'my message number '+str(p))

results = exec_pipe(pipeline, "set", part)

# HASH
part = "myTestHash"
for m in range(1,2000):
    pipeline.hset(part+ ":"+str(m),"name","Dmitry")
    pipeline.hset(part+ ":"+str(m),"age", m)
    pipeline.hset(part+ ":"+str(m),"sex", "Male")
results = exec_pipe(pipeline, "set", part)

for m in range(1,2000):
    pipeline.hvals(part+ ":"+str(m))

results = exec_pipe(pipeline, "get", part)
if show_read:
    for r in results:
        print(r[0].decode("utf-8"),r[1].decode("utf-8"),r[2].decode("utf-8"))

# DICT
part = "myTestDict"
dict_data = {
    part+":employee_name": "Adam Adams",
    part+":employee_age": 30,
    part+":position": "Software Engineer",
}

ms = time.time_ns()
client.mset(dict_data)
delta =  time.time_ns() - ms
print(part, "set", round(delta/1000), "microsec")

ms = time.time_ns()
client.mget(part+":employee_name", part+":employee_age", part+":position", part+":non_existing")
delta =  time.time_ns() - ms
print(part, "get", round(delta/1000), "microsec")

# STRING
part = "myTestList"
for m in range(1,2000):
    pipeline.set(part+ ":"+str(m), 'Тестовое значение для элемента myTestList:'+str(m))
results = exec_pipe(pipeline, "set", part)

for key in client.scan_iter(part+ ":*"):
    pipeline.get(key)
results = exec_pipe(pipeline, "get", part)
if show_read:
    for r in results:
        print(r.decode("utf-8"))

# JSON
part = "myTestJson"
dict_value = {'model': 'Freedom', 'brand': 'Liberty', 'price': 400, 'type': 'Electric', 
              'specs': {'material': 'aluminium', 'weight': 16}, 
              'description': 'The Freedom empowers you with effortless mobility and eco-friendly commuting!', 
              'addons': ['phone mount', 'rear light'], 'helmet_included': True, 'condition': 'new'}
for m in range(1,2000):
    pipeline.json().set(part+ ":"+str(m), Path.root_path(), dict_value)
results = exec_pipe(pipeline, "set", part)

for key in client.scan_iter(part+":*"):
    pipeline.json().get(key)
results = exec_pipe(pipeline, "get", part)
if show_read:
    for r in results:
        print(r)