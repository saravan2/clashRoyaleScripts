import os
import asyncio
import time
import datetime
import pytz
from crapipy import AsyncClient

# Gets PvP results of clan members for the last 3 days.
async def getPvPResults():
    #Use current timestamp to deduct the day, month and year
    curr_utctimestamp = pytz.utc.localize(datetime.datetime.utcnow()).timestamp()
    year = int(datetime.datetime.fromtimestamp(curr_utctimestamp).strftime("%Y"))
    month = int(datetime.datetime.fromtimestamp(curr_utctimestamp).strftime("%m"))
    day = int(datetime.datetime.fromtimestamp(curr_utctimestamp).strftime("%d"))
    # Lets get 12:00 am UTC timestamp for today
    today_utcts = int(pytz.utc.localize(datetime.datetime(year, month, day)).timestamp())
    yesterday_utcts = today_utcts - 86400
    daybeforeyesterday_utcts = yesterday_utcts - 86400
    today_date = datetime.datetime.fromtimestamp(today_utcts, pytz.utc).strftime("%Y-%m-%d")
    yest_date = datetime.datetime.fromtimestamp(yesterday_utcts, pytz.utc).strftime("%Y-%m-%d")
    dbyest_date = datetime.datetime.fromtimestamp(daybeforeyesterday_utcts, pytz.utc).strftime("%Y-%m-%d")

    client = AsyncClient()
    # get clan 
    clan = await client.get_clan(os.environ.get('CLAN'))
    today = open('data/{}'.format(today_date), 'w+')
    yest = open('data/{}'.format(yest_date), 'w+')
    dbyest = open('data/{}'.format(dbyest_date), 'w+')
    for member in clan.members:
        player = await client.get_player(member['tag'])
        for battle in player.battles:
            if (battle['type'] == 'PvP'):
                bt_date = time.strftime("%Y-%m-%d", time.gmtime(battle['utcTime']))
                ofile = None
                if (bt_date == today_date):
                    ofile = today
                if (bt_date == yest_date):
                    ofile = yest
                if (bt_date == dbyest_date):
                    ofile = dbyest
                if ofile is not None:
                    print("{} {} UTC Date {} Outcome {}".format(member.name, member.tag, time.strftime("%Y-%m-%d", time.gmtime(battle['utcTime'])), battle['winner']), file=ofile)
    today.close()
    yest.close()
    dbyest.close()

if __name__ == "__main__":
    with open('env_script.env') as f:
        for line in f:
            if 'export' not in line:
                continue
            # Remove leading `export `
            # then, split name / value pair
            key, value = line.replace('export ', '', 1).strip().split('=', 1)
            os.environ[key] = value
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getPvPResults())
    loop.close()
