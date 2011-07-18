#!/usr/bin/python

import sys
import web
import hashlib
import time
import pymongo
from pymongo import Connection
from pymongo import ASCENDING, DESCENDING

render = web.template.render('templates/')

urls = (
    '/home', 'home',
    '/encode', 'encode',
    '/(.*)', 'decode'
    )
conn = Connection()
db = conn.shorty
collection = db.hashes
collection.create_index([('hash', ASCENDING)
    , ('index', ASCENDING)
    , ('timestamp', DESCENDING)])
index = '9'
if (collection.count()):
    for rec in collection.find().sort('timestamp', DESCENDING):
        index = rec['index']
        break

app = web.application(urls, globals())
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
          'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
          'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
          'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
#
revIndex = {
	'a': 0
	, 'b': 1
	, 'c': 2
	, 'd': 3
	, 'e': 4
	, 'f': 5
	, 'g': 6
	, 'h': 7
	, 'i': 8
	, 'j': 9
	, 'k': 10
	, 'l': 11
	, 'm': 12
	, 'n': 13
	, 'o': 14
	, 'p': 15
	, 'q': 16
	, 'r': 17
	, 's': 18
	, 't': 19
	, 'u': 20
	, 'v': 21
	, 'w': 22
	, 'x': 23
	, 'y': 24
	, 'z': 25
	, 'A': 26
	, 'B': 27
	, 'C': 28
	, 'D': 29
	, 'E': 30
	, 'F': 31
	, 'G': 32
	, 'H': 33
	, 'I': 34
	, 'J': 35
	, 'K': 36
	, 'L': 37
	, 'M': 38
	, 'N': 39
	, 'O': 40
	, 'P': 41
	, 'Q': 42
	, 'R': 43
	, 'S': 44
	, 'T': 45
	, 'U': 46
	, 'V': 47
	, 'W': 48
	, 'X': 49
	, 'Y': 50
	, 'Z': 51
	, '0': 52
	, '1': 53
	, '2': 54
	, '3': 55
	, '4': 56
	, '5': 57
	, '6': 58
	, '7': 59
	, '8': 60
	, '9': 61
}
#
def nextIndex(s):
  start = [e for e in s]
  l = len(start)
  i = l - 1
  while i >= 0:
    if revIndex[start[i]] < len(alphabets) - 1:
      start[i] = alphabets[revIndex[start[i]] + 1]
      return "".join(start)
    else:
      start[i] = 'a'
    i = i - 1
  return "".join(['a'] * (l + 1))

class home:
  def GET(self):
    return render.index("")

#
class decode:
  def GET(self, inHash):
    try:
      record = collection.find_one({'index': inHash})
      record['url']
    except:
      return web.notfound("Unknown short URL")
    else:
      row = record
      row['accessCount'] = row['accessCount'] + 1
      collection.update({'index': row['index']}, row, upsert = False, multi =
          False)
      raise web.seeother(record['url'])
#
class encode:
  def shortenUrl(self, url):
    timestamp = int(time.time())
    reqIp = web.ctx['ip']
    m = hashlib.sha1()
    m.update(url)
    urlHash = m.hexdigest()
    try:
      record = collection.find_one({'hash': urlHash})
      record['index']
    except:
      global index
      index = nextIndex(index)
      collection.insert({
          'reqIp': reqIp
          , 'timestamp': timestamp
          , 'url': url
          , 'hash': urlHash
          , 'accessCount': 0
          , 'index': index
          })
      return render.index(index)
    else:
      return render.index(record['index'])

  def GET(self):
    i = web.input(q = None)
    url = i.q
    return self.shortenUrl(url)

  def POST(self):
    formIn = web.input()
    url = formIn.url
    return self.shortenUrl(url)

# Tell web.py explicitly that it has to act as a FastCGI server
web.wsgi.runwsgi = lambda func, addr = None: web.wsgi.runfcgi(func, addr)
#

if __name__ == "__main__": app.run()
#

