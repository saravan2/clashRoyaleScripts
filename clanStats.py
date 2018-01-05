import os
import asyncio
import time
import datetime
import pytz
import math
from crapipy import AsyncClient

async def getClanStats():
    #Use current timestamp to deduct the day, month and year
    curr_utctimestamp = pytz.utc.localize(datetime.datetime.utcnow()).timestamp()
    today_date = datetime.datetime.fromtimestamp(curr_utctimestamp, pytz.utc).strftime("%Y-%m-%d")

    client = AsyncClient()
    # get clan 
    clan = await client.get_clan(os.environ.get('CLAN'))
    today = open('data/clanStats-{}'.format(today_date), 'w+')
    maxPvPWinsPercentMember = None
    maxPvPWinsPercent = 0
    minPvPWinsPercentMember = None
    minPvPWinsPercent = 1000
    maxClanChestCrownsMember = None
    maxClanChestCrowns = 0
    maxDonationsPercentMember = None
    maxDonationsPercent = 0
    maxDonationsDeltaMember = None
    maxDonationsDelta = -math.inf 
    minDonationsDeltaMember = None
    minDonationsDelta = math.inf
    for member in clan.members:
        if (int(member.clanChestCrowns) > maxClanChestCrowns):
            maxClanChestCrowns = int(member.clanChestCrowns) 
            maxClanChestCrownsMember = member
        if (int(math.fsum([float(member.donationsPercent)] * 100)) > maxDonationsPercent):
            maxDonationsPercent = int(math.fsum([float(member.donationsPercent)] * 100))
            maxDonationsPercentMember = member
        if (int(member.donationsDelta) > maxDonationsDelta):
            maxDonationsDelta = int(member.donationsDelta)
            maxDonationsDeltaMember = member
        if (int(member.donationsDelta) < minDonationsDelta):
            minDonationsDelta = int(member.donationsDelta)
            minDonationsDeltaMember = member
        player = await client.get_player(member.tag)
        wins = int(player.games.wins)
        losses = int(player.games.losses)
        totalPvP = wins + losses
        winsPercent = int(math.fsum([wins / totalPvP] * 1000))
        if (winsPercent > maxPvPWinsPercent):
            maxPvPWinsPercent = winsPercent
            maxPvPWinsPercentMember = member
        if (winsPercent < minPvPWinsPercent):
            minPvPWinsPercent = winsPercent
            minPvPWinsPercentMember = member
        print("{} {} Trophies {} Clan Rank {} Role {} ClanChestCrowns {} Donations {} Received {} Delta {}".format(member.name, member.tag, member.trophies, member.rank, member.role, member.clanChestCrowns, member.donations, member.donationsReceived, member.donationsDelta), file=today)

    print("****************************", file=today)
    print("maxClanChestCrowns {} {} {}".format(maxClanChestCrownsMember.name, maxClanChestCrownsMember.tag, maxClanChestCrowns), file=today)
    print("maxWinsPercent {} {} {}".format(maxPvPWinsPercentMember.name, maxPvPWinsPercentMember.tag, (maxPvPWinsPercent/10)), file=today)
    print("minWinsPercent {} {} {}".format(minPvPWinsPercentMember.name, minPvPWinsPercentMember.tag, (minPvPWinsPercent/10)), file=today)
    print("maxDonationsPercent {} {} {}".format(maxDonationsPercentMember.name, maxDonationsPercentMember.tag, (maxDonationsPercent/100)), file=today)
    print("maxDonationsDelta {} {} {}".format(maxDonationsDeltaMember.name, maxDonationsDeltaMember.tag, maxDonationsDelta), file=today)
    print("minDonationsDelta {} {} {}".format(minDonationsDeltaMember.name, minDonationsDeltaMember.tag, minDonationsDelta), file=today)
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
