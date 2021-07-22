import discord
from discord import FFmpegPCMAudio
from discord import ChannelType
from discord.ext import commands
import spotipy
from PIL import Image
import requests
from io import BytesIO
from spotipy.oauth2 import SpotifyClientCredentials
import os
from keep_alive import keep_alive
from replit import db
import time

SPOTIPY_CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you monkey brains"))


@client.event
async def on_message(message):
  server = discord.utils.get(client.guilds, id=641507713733623829)  # your server's ID
  if message.author == client.user:
    return
  messageOut = ''
  if ('who' in message.clean_content.lower() and 'on' in message.clean_content.lower()):
  
    author = message.author.mention
    members = message.channel.members
    messageOut += ('Ok %s. Since it\'s so hard to look yourself i\'ll look for you'%(author))
    memids = []
    off = []
    for member in members:
      spot = False
      game = False
      stream = False
      song = ''
      songID = ''
      album = ''
      gName = ''
      if not member.bot and member != message.author:
        if member.status == discord.Status.online:
          memids.append(member.id)
          activities = member.activities
          for act in activities:
            if type(act) == discord.activity.Spotify:
              spot = True
              song = act.title
              songID = act.track_id
              album = act.album
            if type(act) == discord.activity.Activity:
              game = True
              gName = act.name
            if type(act) == discord.activity.Game:
              game = True
              gName = act.name
            if type(act) == discord.activity.Streaming:
              stream = True
              sName = act.twitch_name
              sGame = act.game
              sURL = act.url
          if game and spot:
            if gName == 'Rocket League':
              messageOut += ('\n%s is listening to %s while playing Rocket'%(member.name, song))

            elif gName == 'Fortnite':
              messageOut += ('\n%s is listening to %s while playing Fornite'%(member.name, song))
            else:
              messageOut += ('\n%s is listening to %s while playing %s'%(member.name, song, gName))
            messageOut += ('\nYou can listen here: https://open.spotify.com/track/%s'%(songID))
          elif stream and spot:
            messageOut += ('\n%s is streaming %s at %s while listening to %s'%(sName, sGame, sURL, song))
            messageOut += ('\nYou can listen here: https://open.spotify.com/track/%s'%(songID))
          elif spot:
            messageOut += ('\n%s is listening to %s'%(member.name, song))
            messageOut += ('\nYou can listen here: https://open.spotify.com/track/%s'%(songID))
          elif game:
            messageOut += ('\n%s is playing %s'%(member.name, gName))
          elif stream:
            messageOut += ('\n%s is streaming %s at %s'%(sName, sGame, sURL))
          else:
            messageOut += ('\n%s is online but isn\'t doing anything'%(member.name))
        elif member.status == discord.Status.idle:
          messageOut += ('\n%s is idle like a loser. Either get on or get off, jesus.'%(member.name))
        elif member.status == discord.Status.dnd:
          messageOut += ('\n%s doesn\'t want to be disturbed.'%(member.name))
        elif member.status == discord.Status.invisible:
          messageOut += ('\n%s is invisible. They\'re probably watching TV'%(member.name))
        else:
          off.append(member.name)
    await message.channel.send(messageOut)
    await message.delete()
    return
  if 'more like' in message.clean_content.lower():
    playlist = message.clean_content.replace('more like ', '')
    await message.channel.send('If you liked songs from %s, then you might also like these:'%(playlist))
    for el in moreLike(playlist):#, name):
      await message.channel.send(el)
  if 'delete request' in message.clean_content.lower():
    req = message.clean_content.replace('delete request ', '')
    req = req.replace('Delete request ', '')
    req = req.replace('delete Request ', '')
    req = req.replace('Delete Request ', '')
    delRequest(req)
    await message.channel.send("%s was removed from requests. I guess David decided to add it."%(req))
    await message.delete()
  elif 'get requests' in message.clean_content.lower():
    if "requests" in db.keys() and len(db["requests"]) > 0:
      requests = db["requests"]
      count = 1
      for req in requests:
        await message.channel.send('%i. %s'%(count, req))
        count += 1

    else:
      await message.channel.send('There are currently no requests.')
    await message.delete()
  elif 'request' in message.clean_content.lower():
    req = message.clean_content.replace('request ', '')
    req = req.replace('Request ', '')
    addRequest(req)
    await message.channel.send("%s was added to the requests by %s. Im sure David will get on that ASAP."%(req, message.author.mention))
    await message.delete()
  if 'geomap' in message.clean_content.lower():
    await message.channel.send('https://www.geoguessr.com/maps/5dec7ee144d2a4a0f4feb636/play')
    await message.delete()
  if 'newdrops' in message.clean_content.lower():
    drops = getDrops()
    for artist, song in drops:
      print('%s most recent drop is %s'%(artist, song))
      await message.channel.send('%s most recent drop is %s'%(artist, song))
    await message.delete()

# @client.event
# async def on_voice_state_update(member, before, after):
  # voice_channels = client.guilds[0].voice_channels;
  # if after.channel in voice_channels:
  #   members_in = len(after.channel.members)
  #   if members_in == 1:
  #     vc = await after.channel.connect()
  #     source = FFmpegPCMAudio('crickets.mp3')
  #     vc.play(source)
  #     time.sleep(10)
  #     await vc.disconnect()

def addRequest(req):
  if "requests" in db.keys():
    requests = db["requests"]
    requests.append(req)
    db["requests"] = requests
  else:
    db["requests"] = [req]

def delRequest(reqe):
  requests = db["requests"]
  ind = 0
  for req in requests:
    if req == reqe:
      del requests[ind]
      db["requests"] = requests
      return
    ind += 1



def moreLike(playlistID):
  client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
  sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
  songs = []
  playlist = sp.playlist(playlistID)
  for el in playlist['tracks']['items']:
    songs.append(el['track']['uri'][14:])
  print(songs)
  recc = sp.recommendations(seed_tracks=songs, limit=5)
  recs = []
  for track in recc['tracks']:
    recs.append(track['external_urls']['spotify'])
  return recs

def getLink(album, songID):
  client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
  sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
  sp.trace = False

  # find album by name
  results = sp.search(q = "album:" + album, type = "album")

  # get the first album uri
  albumID = results['albums']['items'][0]['uri']
  albumID = albumID[14:]
  format = 'https://open.spotify.com/album/%s?highlight=spotify:track:%s'%(albumID, songID)
  print(format)
  return format


def getDrops():
  client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
  sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
  sp.trace = False
  drops = []
  travID = 'spotify:artist:0Y5tJX1MQlPlqiwlOH1tJY'
  thugID = 'spotify:artist:50co4Is1HCEo8bhOyUWKpn'

  travSongs = sp.artist_albums(travID, album_type=None, country=None, limit=1)['items'][0]['external_urls']['spotify']
  print(travSongs)
  drops.append([sp.artist(travID)['name'], travSongs])
  thugSongs = sp.artist_albums(thugID, album_type=None, country=None, limit=1)['items'][0]['external_urls']['spotify']
  print(thugSongs)
  drops.append([sp.artist(thugID)['name'], thugSongs])

  return drops
  

keep_alive()
client.run(os.getenv('TOKEN'))
