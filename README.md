# Redis DB

Задание: <br/>
+ *сохранить большой json объект (~20МБ) в виде разных структур - строка, hset, zset, list;*
+ *протестировать скорость сохранения и чтения;*
+ *предоставить отчет.*


#  Выполнение домашнего задания:


## Развернуть сервер redis 

Развертывание на сервере с ОС Windows-10<br/>

![WS](/img/ws_params.jpg)

Версия redis: Redis server v=7.4.2 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64

docker-copmose
```
version: "3.8"

services:
  redis:
    image: redis/redis-stack:latest
    ports:
      - "10001:6379"
      - "13333:8001"
    volumes:
      - redis-data:/data
      - ./redis-stack.conf:/redis-stack.conf
volumes:
  redis-data:
 
networks:
  default:
    external: 
      name: stack
```

Конфигурация
```
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
always-show-logo no
set-proc-title yes
proc-title-template "{title} {listen-addr} {server-mode}"
locale-collate ""
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
rdb-del-sync-files no
dir ./
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-diskless-sync-max-replicas 0
repl-diskless-load disabled
repl-disable-tcp-nodelay no
replica-priority 100
acllog-max-len 128
requirepass admin@1234
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
lazyfree-lazy-user-del no
lazyfree-lazy-user-flush no
oom-score-adj no
oom-score-adj-values 0 200 800
disable-thp yes
appendonly no
appendfilename "appendonly.aof"
appenddirname "appendonlydir"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
aof-timestamp-enabled no
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-listpack-entries 512
hash-max-listpack-value 64
list-max-listpack-size -2
list-compress-depth 0
set-max-intset-entries 512
set-max-listpack-entries 128
set-max-listpack-value 64
zset-max-listpack-entries 128
zset-max-listpack-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
jemalloc-bg-thread yes
```

# Тестирование производительности 

На примере операций добавления (обновления) записей и чтение записей структур разного типа <br/>
Тестовые примеры  Python версия 3.12  <br/>
Python Redis library:
```
pip install redis
```
Проверка соединения с БД (предварительно загружены тестовые наборы данных в приложении RedisInsight)
```
import redis
import time

client = redis.Redis( host='localhost', port=10001, password='admin@1234', db=0)

ms = time.time_ns()
rec = client.json().get("sample_bicycle:1001")
delta =  time.time_ns() - ms
print(rec)
print(round(delta/1000), "micro sec")
```

Вывод (runfile('/src/test_redis_connect.py', wdir='/src'))
```
{'model': 'Racer', 
 'brand': 'Speedster', 
 'price': 320, 
 'type': 'Road', 
 'specs': {'material': 'carbon fiber', 'weight': 8}, 
 'description': 'The Racer is built for speed and performance on the road!', 
 'addons': ['water bottle holder', 'bike lock'], 
 'helmet_included': True, 
 'condition': 'new'}

 5739 microsec
```
Данные в базе Redis

![Data Redis](/img/test_data.jpg)

### Тест записи и чтения данных из БД
```
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
```
### Результаты выполнения тестов
```
myTestZlist set 32475 microsec
myTestZlist get  3214 microsec

myTestQuery set 374318 microsec

myTestHash set 65514 microsec
myTestHash get 31235 microsec

myTestDict set 7325 microsec
myTestDict get 1046 microsec

myTestList set 22461 microsec
myTestList get 15364 microsec

myTestJson set 56991 microsec
myTestJson get 29125 microsec
```
