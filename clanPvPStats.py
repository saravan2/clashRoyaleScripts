import os
import asyncio
import time
import datetime
import pytz
import math
from crapipy import AsyncClient
from collections import defaultdict
from collections import OrderedDict 
from operator import itemgetter

async def getClanStats():
    #Use current timestamp to deduct the day, month and year
    curr_utctimestamp = pytz.utc.localize(datetime.datetime.utcnow()).timestamp()
    today_date = datetime.datetime.fromtimestamp(curr_utctimestamp, pytz.utc).strftime("%Y-%m-%d")

    client = AsyncClient()
    # get clan 
    clan = await client.get_clan(os.environ.get('CLAN'))
    today = open('data/clanPvPStats-{}'.format(today_date), 'w+')
    d = {}
    sumWinsPercent = 0
    for member in clan.members:
        player = await client.get_player(member.tag)
        wins = int(player.games.wins)
        losses = int(player.games.losses)
        totalPvP = wins + losses
        winsPercent = int(math.fsum([wins / totalPvP] * 1000))
        sumWinsPercent += winsPercent
        values = [member.name, member.trophies, member.role, member.rank, totalPvP, (winsPercent/10)]
        for value in values:
            d.setdefault(member.tag, []).append(value)
    d = OrderedDict(sorted(d.items(), key = lambda v : (v[1][5], v[1][4]), reverse = True))
    for key in d:
        print("{} {}".format(key, d[key]), file = today)

    print("**********", file = today)
    print("Clan Average {}".format(sumWinsPercent/(len(d)*10)), file = today)
    today.close()

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
    loop.run_until_complete(getClanStats())
    loop.close()
