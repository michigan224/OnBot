import os
from discord import Webhook, RequestsWebhookAdapter
import discord
from dotenv import load_dotenv
import requests
from datetime import datetime
import json
import asyncio


async def getCarETA():
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
    webhook.send(embed=e)
    with open('data.json', 'w') as outfile:
        outfile.write(json.dumps(r, indent=4))
        outfile.close()


load_dotenv()
webhook = Webhook.from_url(
    os.getenv('WEBHOOK_URL'),
    adapter=RequestsWebhookAdapter())
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getCarETA())
