'''Cron task that grabs the TF2 item schema every hour and makes some item name and quality replacements.
   Schema is then stored in cache.'''

import urllib2, simplejson
from google.appengine.api import memcache

API_KEY = ''

def replace_names(items):
	item_names = {
        'Upgradeable TF_WEAPON_BAT': 'Bat',
        'Upgradeable TF_WEAPON_BOTTLE': 'Bottle',
        'Upgradeable TF_WEAPON_FIREAXE': 'Fireaxe',
        'Upgradeable TF_WEAPON_CLUB': 'Club',
        'Upgradeable TF_WEAPON_KNIFE': 'Knife',
        'Upgradeable TF_WEAPON_FISTS': 'Fists',
        'Upgradeable TF_WEAPON_SHOVEL': 'Shovel',
        'Upgradeable TF_WEAPON_WRENCH': 'Wrench',
        'Upgradeable TF_WEAPON_BONESAW': 'Bonesaw',
        'Upgradeable TF_WEAPON_SHOTGUN_PRIMARY': 'Shotgun',
        'Upgradeable TF_WEAPON_SCATTERGUN': 'Scattergun',
        'Upgradeable TF_WEAPON_SNIPERRIFLE': 'Sniper Rifle',
        'Upgradeable TF_WEAPON_MINIGUN': 'Minigun',
        'Upgradeable TF_WEAPON_SMG': 'Submachinegun',
        'Upgradeable TF_WEAPON_SYRINGEGUN_MEDIC': 'Syringe Gun',
        'Upgradeable TF_WEAPON_ROCKETLAUNCHER': 'Rocket Launcher',
        'Upgradeable TF_WEAPON_GRENADELAUNCHER': 'Grenade Launcher',
        'Upgradeable TF_WEAPON_PIPEBOMBLAUNCHER': 'Stickybomb Launcher',
        'Upgradeable TF_WEAPON_FLAMETHROWER': 'Flamethrower',
        'Upgradeable TF_WEAPON_PISTOL': 'Pistol',
        'Upgradeable TF_WEAPON_REVOLVER': 'Revolver',
        'Upgradeable TF_WEAPON_MEDIGUN': 'Medigun',
        'Upgradeable TF_WEAPON_INVIS': 'Inviswatch',
        'Upgradeable TF_WEAPON_BUILDER_SPY': 'Sapper',
        'Upgradeable TF_WEAPON_PDA_ENGINEER_BUILD': 'PDA',
        'Craft Bar Level 1': 'Scrap Metal',
        'Craft Bar Level 2': 'Reclaimed Metal',
        'Craft Bar Level 3': 'Refined Metal',
        'TTG Max Pistol - Poker Night': 'Lugermorph',
        'OSX Item': 'Earbuds',
        'Treasure Hat 1': 'Bounty Hat',
        'Treasure Hat 2': 'Treasure Hat'
        }

	for item in items:
		if item['name'] in item_names:
			item['name'] = item_names[item['name']]

def replace_qualities(qualities):
	item_qualities = {
        	'rarity1': 'genuine',
        	'rarity4': 'unusual',
        	'selfmade': 'self-made'
	}

	for quality in qualities:
		if quality in item_qualities:
			qualities[item_qualities[quality]] = qualities[quality]
			del qualities[quality]

def main():
	response = urllib2.urlopen('http://api.steampowered.com/IEconItems_440/GetSchema/v0001/?key={0}'.format(API_KEY)).read()
	schema = simplejson.loads(response)

	qualities = schema['result']['qualities']
	origins = schema['result']['originNames']
	items = schema['result']['items']

	replace_names(items)
	replace_qualities(qualities)

	memcache.set_multi(
		{
			'items': items,
			'qualities': qualities,
			'origins': origins
		},
	)

if __name__ == '__main__':
	main()