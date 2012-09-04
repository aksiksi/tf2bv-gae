import urllib2, json
from google.appengine.api import memcache

response = urllib2.urlopen('http://api.steampowered.com/IEconItems_440/GetSchema/v0001/?key=').read()
schema = json.loads(response)

qualities = schema['result']['qualities']
origins = schema['result']['originNames']
items = schema['result']['items']

memcache.set_multi(
		{
			'items': items,
			'qualities': qualities,
			'origins': origins
		},
	)