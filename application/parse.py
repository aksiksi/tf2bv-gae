import json, os, re, urllib2
import xml.etree.ElementTree as etree
from collections import OrderedDict 
from time import time, ctime
from google.appengine.api import memcache

def from_normal_to_64(steamid):
    '''Convert Steam ID of format STEAM_X:Y:Z to 64-bit Steam Community ID. Refer to https://developer.valvesoftware.com/wiki/SteamID.'''
    Y, Z = re.findall(u':(\w+):(\w+)', steamid)[0]
    V = 0x0110000100000000
    steamid64 = int(Z) * 2 + V + int(Y)
    return steamid64

def from_profile_to_64(steamid):
    '''Get the username of a given Steam ID using XML option in Steam Profile.'''
    # In case input returns an invalid webpage
    try:
        doc = urllib2.urlopen('http://steamcommunity.com/id/{0}/?xml=1'.format(steamid)).read().decode('ISO-8859-1').encode('UTF-8')
        xml = etree.fromstring(doc)
        steamid64 = xml.findtext('steamID64')
    except:
        steamid64 = None
    finally:
        return steamid64

def get_player_response(steamid, API_KEY):
    '''Get player response from Steam API; no caching - data must be fresh.'''
    text = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?steamids={0}&key={1}'. \
                            format(steamid, API_KEY)).read().encode('UTF-8') # Make sure it's UTF-8
    response = json.loads(text)['response']

    # Return response only if it contains data
    if response['players']:
        return response

    return None

def get_item_response(steamid, API_KEY):
    '''Get item response from Steam API, if it doesn't already exist in cache.'''
    cache = memcache.get(steamid)

    # Return cached response if it is already in the cache
    if cache:
        return cache

    # Otherwise grab response using Steam API
    text = urllib2.urlopen('http://api.steampowered.com/ITFItems_440/GetPlayerItems/v0001/?steamID={0}&key={1}'. \
                         format(steamid, API_KEY)).read().encode('UTF-8') # Make sure it's UTF-8
    response = json.loads(text)['result']

    # Write response to cache if it exists and contains items
    status = response['status']
    if status == 1 and None not in response['items']['item']:
        response['time_written'] = time()
        memcache.add(key=steamid, value=response, time=86400)
        return response
    elif status == 8 or status == 18:
        return None
    elif status == 15:
        return -1
    elif None in response['items']['item']:
        return -2

def find_steamid(parameter, category):
    '''Find 64-bit Steam ID based on passed parameter.'''
    if ('765611980' in parameter and len(parameter) == 17) and category == 'steamid64':
        steamid64 = parameter
    elif 'STEAM_' in parameter and category == 'steamid':
        # Make sure it's not just a customURL
        try:
            steamid64 = from_normal_to_64(parameter)
        except: 
            steamid64 = from_profile_to_64(parameter)
    elif parameter and category == 'profile':
        steamid64 = from_profile_to_64(parameter)
    else:
        return False

    # Make sure steamid64 exists
    if steamid64:
        return steamid64
    
    return False

def parse_item_response(response):
    '''Extract what's needed from the JSON response and use the TF2 item schema to get new data.'''
    # Get item schema from cache
    tf2_item_schema = {
        'items': memcache.get('items'),
        'qualities': memcache.get('qualities'),
        'originNames': memcache.get('origins')
    }
    
    # Check variables and results
    if response <= 0:
        return response
    
    # Variables..
    ordered_response = OrderedDict(response)
    items_in_bp = ordered_response['items']['item']
    schema_items = tf2_item_schema['items']
    bp_slots = ordered_response['num_backpack_slots']
    time_written = ctime(ordered_response['time_written']) # Timestamp in ASCII form
    item_qualities = {v:k.title() for k, v in tf2_item_schema['qualities'].items()} # Reverse dict to make searching easier
    item_origins = {each['origin']:each['name'] for each in tf2_item_schema['originNames']} # Map origin number to name
    req = [
        ('image_url', 'Image'),
        ('name', 'Name'),
        ('level', 'Level'),
        ('defindex', 'Identifier'),
        ('flag_cannot_trade', 'Tradeable?'),
        ('flag_cannot_craft', 'Craftable?'),
        ('quantity', 'Quantity'),
        ('quality', 'Quality'),
        ('origin', 'Origin'),
        ('id', 'ID'),
        ('original_id', 'Original ID'),
        ('custom_name', 'Custom Name'),
        ('custom_desc', 'Custom Description'),
    ]

    # Make a dictionary mapping of item defindex to absolute index in list -> {defindex: index}
    mapping = {item['defindex']:schema_items.index(item) for item in schema_items}
    
    parsed_items = [] # Item dicts stored here
    
    # Get required info from each item; use mapping to find each item in JSON response
    for item in items_in_bp:
        current_item = OrderedDict() # Empty ordered dict for each item
        
        # Used to find item position in schema through mapping
        current_index = mapping[item['defindex']]
        
        # Check if each attribute is in either the schema or the item response, and add to current_item if it is
        for pair in req:
            attr = pair[0]
            new_attr = pair[1]
            if attr in item:
                if attr == 'quality':
                    quality = item_qualities[item[attr]]
                    current_item[new_attr] = quality
                elif attr == 'origin':
                    current_item[new_attr] = item_origins[item[attr]]
                elif attr == 'flag_cannot_trade' or attr == 'flag_cannot_craft':
                    current_item[new_attr] = 'No'
                else:
                    current_item[new_attr] = item[attr]
            elif attr in schema_items[current_index]:
                current_item[new_attr] = schema_items[current_index][attr]
            else:
                if attr == 'flag_cannot_trade' or attr == 'flag_cannot_craft':
                    current_item[new_attr] = 'Yes'
                elif attr == 'custom_name' or attr == 'custom_desc':
                    current_item[new_attr] = 'None'
        
        parsed_items.append(current_item) # Append each item to parsed_items
        
    return [parsed_items, bp_slots, time_written]

def parse_player_response(response):
    '''Convert player response into a dict containing required info.'''
    # Check if response exists
    if not response:
        return None

    # Variables..
    player_info = response['players'][0]
    ordered_response = OrderedDict()
    req = [
        ('personaname', 'Profile Name'),
        ('avatarmedium', 'Avatar'),
        ('steamid', 'Steam ID'),
        ('realname', 'Real Name'),
        ('personastate', 'Status'),
        ('lastlogoff', 'Last Logoff'),
        ('timecreated', 'Account Creation Date'),
        ('profileurl', 'Profile')
    ]
    status = ['Offline', 'Online', 'Busy', 'Away', 'Snooze', 'Looking to Trade', 'Looking to Play']

    # Populate ordered_response with player info; if entry is time-related, convert time to ASCII format
    for pair in req:
        key = pair[0]
        new_key = pair[1]
        if key in player_info:
            if key == 'lastlogoff' or key == 'timecreated':
                ordered_response[new_key] = ctime(player_info[key])
            elif key == 'personastate': # Get user status
                ordered_response[new_key] = status[player_info[key]]
            else:
                ordered_response[new_key] = player_info[key]
        else:
            if key == 'realname':
                ordered_response[new_key] = 'Not listed'

    return ordered_response

if __name__ == '__main__':
    pass