"""Personal discord bot."""
import logging
import os
import string
from datetime import datetime

import discord
from dotenv import load_dotenv

load_dotenv()

if not os.path.exists('logs'):
    os.makedirs('logs')
LOG_FILENAME = datetime.now().strftime('./logs/logfile_%H_%M_%S_%d_%m_%Y.log')
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

intents = discord.Intents.all()
activity = discord.Activity(
    type=discord.ActivityType.listening, name="you monkey brains")
client = discord.Client(intents=intents, activity=activity)


@client.event
async def on_ready():
    """Log when the bot is ready."""
    print(f'We have logged in as {client.user}')
    logging.info('We have logged in as %s', client.user)


@client.event
async def on_message(message):
    """Handle a message."""
    logging.info("%s sent '%s'", message.author, message.content)
    if message.author == client.user:
        return
    msg = message.clean_content.lower().translate(
        str.maketrans('', '', string.punctuation)).split()
    logging.info("Split message: %s", msg)
    if ((('who' in msg or 'whos' in msg) and 'on' in msg)
            or 'whoson' in msg or 'whose on' in message.clean_content.lower()):
        await whos_on(message)
    elif 'geomap' in message.clean_content.lower():
        await message.channel.send('https://www.geoguessr.com/maps/5dec7ee144d2a4a0f4feb636/play')
        await message.delete()


async def whos_on(message):
    """Send a message with the users that are on."""
    members = message.channel.members
    embed = discord.Embed(
        title="Who's on?",
        colour=discord.Colour.blue()
    )
    alone = True
    for member in members:
        if member.bot or member == message.author:
            continue
        resp = get_member_message(member)
        if resp:
            alone = False
            embed.add_field(
                name=resp['name'], value=resp['value'], inline=resp['inline'])
            continue
    if alone:
        embed.add_field(name='RIP',
                        value='Looks like no one is on. You\'re going to have to play alone.',
                        inline=False)
    await message.channel.send(embed=embed)
    await message.delete()
    return


def get_member_message(member):
    """Handle field for individual members."""
    member_name = member.nick if member.nick else member.name
    field = None
    if member.status == discord.Status.offline:
        return None
    activities = member.activities
    (spot, game, stream, song, song_id, game_name, game_state,
     stream_name, stream_game, stream_url) = handle_activities(activities)
    if game and spot and stream:
        field = {
            'name': member_name,
            'value': (f'Listening to [{song}](https://open.spotify.com/track/'
                      f'{song_id}?si=9e2a90467def41ae) while playing Rocket'
                      f'{game_state} and streaming [here]({stream_url})'),
            'inline': False
        }
    if game and spot:
        field = {
            'name': member_name,
            'value': (f'Listening to [{song}]'
                      f'(https://open.spotify.com/track/{song_id}'
                      f'?si=9e2a90467def41ae)'
                      f'while playing {game_name}{game_state}'),
            'inline': False
        }
    if stream and spot:
        field = {
            'name': stream_name,
            'value': (f'Streaming {stream_game} at {stream_url} while listening to [{song}]'
                      f'(https://open.spotify.com/track/{song_id}'
                      f'?si=9e2a90467def41ae)'),
            'inline': False
        }
    if spot:
        field = {
            'name': member_name,
            'value': (f'Listening to [{song}](https://open.spotify.com/track/'
                      f'{song_id}?si=9e2a90467def41ae)'),
            'inline': False
        }
    if game:
        field = {
            'name': member_name,
            'value': f'Playing {game_name}{game_state}',
            'inline': False
        }
    if stream:
        field = {
            'name': stream_name,
            'value': f'Streaming {stream_game}{game_state} at {stream_url}',
            'inline': False
        }
    if member.status == discord.Status.idle:
        field = {
            'name': member_name,
            'value': 'Idle like a loser. Either get on or get off, jesus.',
            'inline': False
        }
    if member.status == discord.Status.dnd:
        field = {
            'name': member_name,
            'value': 'Doesn\'t want to be disturbed.',
            'inline': False
        }
    if member.status == discord.Status.invisible:
        field = {
            'name': member_name,
            'value': 'Invisible. They\'re probably watching TV',
            'inline': False
        }
    if field:
        return field
    return {
        'name': member_name,
        'value': 'Online but not doing anything',
        'inline': False
    }


def handle_activities(activities):
    """Handle activities."""
    spot = False
    game = False
    stream = False
    song = ''
    song_id = ''
    game_name = ''
    game_state = ''
    for act in activities:
        if isinstance(act, discord.activity.Spotify):
            spot = True
            song = act.title
            song_id = act.track_id
        if isinstance(act, discord.activity.Activity):
            game = True
            game_name = act.name
            game_state = act.state
            game_state = f" ({game_state})" if game_state else ''
        if isinstance(act, discord.activity.Game):
            game = True
            game_name = act.name
            game_state = act.state
            game_state = f" ({game_state})" if game_state else ''
        if isinstance(act, discord.activity.Streaming):
            stream = True
            stream_name = act.twitch_name
            stream_game = act.game
            stream_url = act.url
        if isinstance(act, discord.activity.CustomActivity):
            print(act)
    return (spot, game, stream, song, song_id, game_name, game_state,
            stream_name, stream_game, stream_url)


client.run(os.getenv('TOKEN'))
