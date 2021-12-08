import discord
from dotenv import load_dotenv
import os
import pytest

load_dotenv()

target_id = "ID of bot to be tested"
channel_id = "ID of channel of where it will be tested"


async def test_ping():
    correct_response = 'Pong!'
    channel = await client.fetch_channel(channel_id)
    await channel.send("ping")

    def check(m):
        return m.content == correct_response and m.author.id == target_id

    response = await client.wait_for('message', check=check)
    assert (response.content == correct_response)

intents = discord.Intents.all()
client = discord.Client(intents=intents)
client.run(os.getenv('TOKEN'))
