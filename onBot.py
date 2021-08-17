import discord
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from imdb import IMDb
from pycliarr.api import RadarrCli, SonarrCli
import mariadb
from datetime import date, datetime
import json
import requests

load_dotenv()
ia = IMDb()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
radarr_cli = RadarrCli('http://192.168.4.63:7878', os.getenv('RADARR_API_KEY'))
sonarr_cli = SonarrCli('http://192.168.4.63:8989', os.getenv('SONARR_API_KEY'))

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you monkey brains"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if ('who' in message.clean_content.lower() and 'on' in message.clean_content.lower()):
        await whosOn(message)
    elif 'more like' in message.clean_content.lower():
        playlist = message.clean_content.replace('more like ', '')
        await message.channel.send('If you liked songs from %s, then you might also like these:' % (playlist))
        for el in moreLike(playlist):  # , name):
            await message.channel.send(el)
    elif 'request movie' in message.clean_content.lower():
        req = message.clean_content.replace('request movie ', '')
        await requestMovie(req, message)
    elif 'request series' in message.clean_content.lower():
        req = message.clean_content.replace('request series ', '')
        await requestSeries(req, message)
    elif 'geomap' in message.clean_content.lower():
        await message.channel.send('https://www.geoguessr.com/maps/5dec7ee144d2a4a0f4feb636/play')
        await message.delete()
    elif 'newdrops' in message.clean_content.lower():
        drops = getDrops()
        for artist, song in drops:
            print('%s most recent drop is %s' % (artist, song))
            await message.channel.send('%s most recent drop is %s' % (artist, song))
        await message.delete()
    elif 'whip' == message.clean_content.lower():
        await getCarETA(message)


async def whosOn(message):
    author = message.author.mention
    members = message.channel.members
    messageOut = (
        'Ok %s. Since it\'s so hard to look yourself i\'ll look for you' % (author))
    memids = []
    off = []
    for member in members:
        spot = False
        game = False
        stream = False
        song = ''
        songID = ''
        gName = ''
        if not member.bot and member != message.author:
            if member.status == discord.Status.online:
                memids.append(member.id)
                activities = member.activities
                for act in activities:
                    if isinstance(act, discord.activity.Spotify):
                        spot = True
                        song = act.title
                        songID = act.track_id
                    if isinstance(act, discord.activity.Activity):
                        game = True
                        gName = act.name
                    if isinstance(act, discord.activity.Game):
                        game = True
                        gName = act.name
                    if isinstance(act, discord.activity.Streaming):
                        stream = True
                        sName = act.twitch_name
                        sGame = act.game
                        sURL = act.url
                if game and spot:
                    if gName == 'Rocket League':
                        messageOut += ('\n%s is listening to %s while playing Rocket' %
                                       (member.name, song))

                    elif gName == 'Fortnite':
                        messageOut += ('\n%s is listening to %s while playing Fornite' %
                                       (member.name, song))
                    else:
                        messageOut += ('\n%s is listening to %s while playing %s' %
                                       (member.name, song, gName))
                    messageOut += (
                        '\nYou can listen here: https://open.spotify.com/track/%s' % (songID))
                elif stream and spot:
                    messageOut += ('\n%s is streaming %s at %s while listening to %s' %
                                   (sName, sGame, sURL, song))
                    messageOut += (
                        '\nYou can listen here: https://open.spotify.com/track/%s' % (songID))
                elif spot:
                    messageOut += ('\n%s is listening to %s' %
                                   (member.name, song))
                    messageOut += (
                        '\nYou can listen here: https://open.spotify.com/track/%s' % (songID))
                elif game:
                    messageOut += ('\n%s is playing %s' % (member.name, gName))
                elif stream:
                    messageOut += ('\n%s is streaming %s at %s' %
                                   (sName, sGame, sURL))
                else:
                    messageOut += ('\n%s is online but isn\'t doing anything' %
                                   (member.name))
            elif member.status == discord.Status.idle:
                messageOut += (
                    '\n%s is idle like a loser. Either get on or get off, jesus.' % (member.name))
            elif member.status == discord.Status.dnd:
                messageOut += ('\n%s doesn\'t want to be disturbed.' %
                               (member.name))
            elif member.status == discord.Status.invisible:
                messageOut += ('\n%s is invisible. They\'re probably watching TV' %
                               (member.name))
            else:
                off.append(member.name)
    if messageOut == 'Ok %s. Since it\'s so hard to look yourself i\'ll look for you' % (author):
        await message.channel.send(messageOut + '\nLooks like no one is on. You\'re going to have to play alone.')
        await message.delete()
        return
    await message.channel.send(messageOut)
    await message.delete()
    return


async def requestMovie(req, message):
    d = date.today()
    conn = mariadb.connect(
        user=os.getenv('MARIA_DB_USER'),
        password=os.getenv('MARIA_DB_PASS'),
        host="192.168.4.63",
        port=3306,
        database="tron_db"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Requests (Movies,Series,Requested,Date) VALUES (?, ?, ?, ?)", (req, "", message.author.name, d))
    conn.commit()
    conn.close()
    movie = ''
    movies = []
    if isinstance(req, int):
        movie = ia.get_movie(req)
        metadata = radarr_cli.lookup_movie(imdb_id=req)._data
        metadata = json.dumps(metadata, indent=4)
        d = date.today()
        auth = message.author.name

        try:
            radarr_cli.add_movie(imdb_id=req, quality=4)
            await message.channel.send(f'{movie} was successfully added. It should be downloaded and imported soon!')
            conn = mariadb.connect(
                user=os.getenv('MARIA_DB_USER'),
                password=os.getenv('MARIA_DB_PASS'),
                host="192.168.4.63",
                port=3306,
                database="tron_db"
            )
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Movies (metadata,requested,date) VALUES (?, ?, ?)",
                (metadata, auth, d))
            conn.commit()
            conn.close()
            return
        except Exception as e:
            print(e)
            await message.channel.send('Movie already on Plex. If not ask David idk gosh man')
            return
    else:
        movies = ia.search_movie(req)
        temp = []
        for el in movies:
            if(el.data['kind'] == 'movie'):
                temp.append(el)
        movies = temp[:6]
        movieTitles = [el.data['title'] for el in movies]
        movieIDs = [el.movieID for el in movies]

        if not movies and not movie:
            await message.channel.send('Could not find the given movie. Check [imdb](https://www.imdb.com/)')
            return

        embed = discord.Embed(title='Please react with the correct one')
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
                  '7️⃣', '8️⃣', '9️⃣', '🔟', '❌']
        for i in range(len(movies)):
            embed.add_field(
                name=emojis[i], value=f'[{movieTitles[i]}](https://www.imdb.com/title/tt{movieIDs[i]}/)')

        embed.add_field(name='If you can\'t find what you\'re looking for click the X and Try again with the ID from,',
                        value='[imdb](https://www.imdb.com/)', inline=False)
        embed.set_thumbnail(url=movies[0].data['cover url'])

        mess1 = await message.channel.send(embed=embed)
        for i in range(len(movies)):
            await mess1.add_reaction(emojis[i])

        await mess1.add_reaction('❌')

        def check(reaction, user):
            return reaction.message.id == mess1.id and (emojis.index(reaction.emoji) != -1) and user == message.author

        reaction = await client.wait_for('reaction_add', check=check)
        if reaction[0].emoji == '❌':
            await message.channel.send('Please be more descriptive or try with the IMDB ID')
            return
        movie = movies[emojis.index(reaction[0].emoji)]
        metadata = radarr_cli.lookup_movie(imdb_id=movie.movieID)._data
        metadata = json.dumps(metadata, indent=4)
        auth = message.author.name

        try:
            radarr_cli.add_movie(imdb_id=movie.movieID, quality=4)
            await message.channel.send(f'{movie} was successfully added. It should be downloaded and imported soon!')
            conn = mariadb.connect(
                user=os.getenv('MARIA_DB_USER'),
                password=os.getenv('MARIA_DB_PASS'),
                host="192.168.4.63",
                port=3306,
                database="tron_db"
            )
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Movies (metadata,requested,date) VALUES (?, ?, ?)",
                (metadata, auth, d))
            conn.commit()
            conn.close()
            return
        except Exception as e:
            print(e)
            await message.channel.send('Movie already on Plex. If not ask David idk gosh man')
            return


async def requestSeries(req, message):
    d = date.today()
    conn = mariadb.connect(
        user=os.getenv('MARIA_DB_USER'),
        password=os.getenv('MARIA_DB_PASS'),
        host="192.168.4.63",
        port=3306,
        database="tron_db"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Requests (Movies,Series,Requested,Date) VALUES (?, ?, ?, ?)", ("", req, message.author.name, d))
    conn.commit()
    conn.close()
    res = sonarr_cli.lookup_serie(req)[:10]
    found = []
    titles = []
    for el in res:
        if el._data['tvdbId'] and el._data['tvdbId'] not in found:
            found.append(el._data['tvdbId'])
            titles.append(el._data['title'])
    found = found[:6]
    titles = titles[:6]

    embed = discord.Embed(title='Please react with the correct one')
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
              '7️⃣', '8️⃣', '9️⃣', '🔟', '❌']
    thumbnail = ''
    for i in range(len(titles)):
        url = 'https://api.tvmaze.com/lookup/shows?thetvdb=' + str(found[i])
        r = requests.get(url)
        if r.status_code == 200:
            r = r.json()
            if r['image'] and thumbnail == '':
                for el in r['image']:
                    if thumbnail == '':
                        thumbnail = r['image'][el]
            link = r['url']
            embed.add_field(
                name=emojis[i], value=f'[{titles[i]}]({link})')
        else:
            embed.add_field(
                name=emojis[i], value=f'{titles[i]}')
    embed.add_field(name='If you can\'t find what you\'re looking for click the X and Try again with the ID from,',
                    value='[tvdb](https://thetvdb.com/)', inline=False)
    if thumbnail != '':
        embed.set_thumbnail(url=thumbnail)
    mess1 = await message.channel.send(embed=embed)
    for i in range(len(titles)):
        await mess1.add_reaction(emojis[i])

    await mess1.add_reaction('❌')

    def check(reaction, user):
        return reaction.message.id == mess1.id and (emojis.index(reaction.emoji) != -1) and user == message.author

    reaction = await client.wait_for('reaction_add', check=check)
    if reaction[0].emoji == '❌':
        await message.channel.send('Please be more descriptive or try with the IMDB ID')
        return
    series = found[emojis.index(reaction[0].emoji)]
    title = titles[emojis.index(reaction[0].emoji)]
    metadata = sonarr_cli.lookup_serie(tvdb_id=series)._data
    metadata = json.dumps(metadata, indent=4)
    auth = message.author.name

    try:
        sonarr_cli.add_serie(tvdb_id=series, quality=6)
        await message.channel.send(f'{title} was successfully added. It should be downloaded and imported soon!')
        conn = mariadb.connect(
            user=os.getenv('MARIA_DB_USER'),
            password=os.getenv('MARIA_DB_PASS'),
            host="192.168.4.63",
            port=3306,
            database="tron_db"
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Series (metadata,requested,date) VALUES (?, ?, ?)",
            (metadata, auth, d))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        print(e)
        await message.channel.send('Series already on Plex. If not ask David idk gosh man')
        return


async def getCarETA(message):
    vin = os.getenv('VIN')
    orderNum = os.getenv('ORDER_NUMBER')
    url = 'https://shop.ford.com/aemservices/shop/vot/api/customerorder/?orderNumber=' + \
        orderNum + '&partAttributes=BP2_.*&vin=' + vin
    r = requests.get(url)
    r = r.json()[0]
    etaStartDate = r['etaStartDate']
    y, m, d = etaStartDate.split('-')
    etaStartDate = datetime(int(y), int(m), int(d))
    etaEndDate = r['etaEndDate']
    y, m, d = etaEndDate.split('-')
    etaEndDate = datetime(int(y), int(m), int(d))
    currDate = datetime.today().strftime('%Y-%m-%d')
    y, m, d = currDate.split('-')
    currDate = datetime(int(y), int(m), int(d))

    if etaStartDate > currDate and etaEndDate > currDate:
        e = discord.Embed(title="2021 Ranger XLT",
                          description="Estimated delivery date: **" + r['etaStartDate'] + ' - ' + r['etaEndDate'] + "**")
    else:
        e = discord.Embed(title="2021 Ranger XLT",
                          description="Estimated delivery date not available.\nVehicle Status: **" + r['primaryStatus'] + "**")
    e.set_image(url=os.getenv('IMAGE_URL'))
    await message.channel.send(embed=e)


def moreLike(playlistID):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
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
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False

    # find album by name
    results = sp.search(q="album:" + album, type="album")

    # get the first album uri
    albumID = results['albums']['items'][0]['uri']
    albumID = albumID[14:]
    form = 'https://open.spotify.com/album/%s?highlight=spotify:track:%s' % (
        albumID, songID)
    print(form)
    return form


def getDrops():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False
    drops = []
    travID = 'spotify:artist:0Y5tJX1MQlPlqiwlOH1tJY'
    thugID = 'spotify:artist:50co4Is1HCEo8bhOyUWKpn'

    travSongs = sp.artist_albums(travID, album_type=None, country=None, limit=1)[
        'items'][0]['external_urls']['spotify']
    print(travSongs)
    drops.append([sp.artist(travID)['name'], travSongs])
    thugSongs = sp.artist_albums(thugID, album_type=None, country=None, limit=1)[
        'items'][0]['external_urls']['spotify']
    print(thugSongs)
    drops.append([sp.artist(thugID)['name'], thugSongs])

    return drops


client.run(os.getenv('TOKEN'))
