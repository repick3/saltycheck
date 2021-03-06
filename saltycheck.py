import requests
import re
import discord
import asyncio
import itertools
from enum import Enum

import scheduling
import settings

class TournamentStatus(Enum):
    '''
    All possible states of saltybet handled
    '''
    SOON = 1
    IN_PROGRESS = 2
    NOT_EVEN_CLOSE = 3
    UH_OH =  4

class SaltyStatus(object):
    '''
    Simple object for passing status, text, and match count around.
    '''

    def __init__(self, status, text=None, matches_left=None):
        self.status = status
        self.text = text
        self.matches_left = matches_left


async def get_salty_status():
    '''
    Queries saltybet for the current status.jsonm
    '''

    r = requests.get("http://www.saltybet.com/state.json")

    if r.ok:
        return r.json()
    else:
        return None


async def get_matches_until(input_string, mode="tournament"):
    '''
    Simple regex to return the amount of matches left in the string. The pattern
    seems to always have integers starting the string unless it is the LAST
    match before a tournament or the final round of a tournament.
    '''

    if mode == "tournament":
        m = re.search("\d+", input_string)
        if m:
            return int(m.group(0))
        else:
            return 0


async def check_for_tournament(input_string):
    '''
    Builds the SaltyStatus based on the "remaining" key retrieved from saltybet.
    Uses naive string searching to determine status.
    '''
    if not input_string:
        salty_status = SaltyStatus(
            TournamentStatus.UH_OH,
            text="Couldn't get the status of salty bet dot com."
        )
        return salty_status

    if 'remaining' in input_string:
        remaining_string = input_string["remaining"].lower()
    else:
        salty_status = SaltyStatus(
            TournamentStatus.UH_OH,
            text="Couldn't get the status of salty bet dot com."
        )
        return salty_status

    if "tournament" in remaining_string:
        matches_left = await get_matches_until(remaining_string)
        salty_status = SaltyStatus(
            TournamentStatus.SOON,
            text=await format_tourney_string(matches_left),
            matches_left=matches_left
        )

    elif "bracket" in remaining_string:
        matches_left = await get_matches_until(remaining_string)
        salty_status = SaltyStatus(
            TournamentStatus.IN_PROGRESS,
            text="Tournament currently ongoing!",
            matches_left=matches_left
        )
    else:
        salty_status = SaltyStatus(
            TournamentStatus.NOT_EVEN_CLOSE,
            text="No tournament on the horizon."
        )
    
    return(salty_status)


async def format_tourney_string(matches):
    '''
    Handles the output of the alert messages depending on matches left
    '''
    if matches <= 10:
        return(f"Tournament INCOMING! Matches left: {matches}")
        
    elif matches <= 30:
        return(f"Tournament soon! Matches left: {matches}")
        
    elif matches <= 100:
        return(f"Tournament is on the radar. Matches left: {matches}")
    else:
        return("The tournament either just began or just ended.")


async def get_mode():
    '''
    Does a simple check on the fly if someone requests it.
    '''
    salty_status = await get_salty_status()

    if "remaining" in salty_status:
        return(salty_status["remaining"])
    else:
        return("Couldn't get the status of salty bet dot com.")


async def update_presence(client, status):
    '''
    Updates the Discord presence based on status.
    TODO: display current mode for matchmaking/exbo/waifuwarz
    '''

    if status == TournamentStatus.SOON:
        await client.change_presence(game=discord.Game(name='Tournament Spotted!'))
    elif status == TournamentStatus.IN_PROGRESS:
        await client.change_presence(game=discord.Game(name='Tournament In Progress'))
    else:
        await client.change_presence()


async def salty_checker(client):
    '''
    Main task loop.
    Handles periodically checking saltybet and alerting channels defined in settings.py
    '''

    await client.wait_until_ready()
    next_alert_pattern = itertools.cycle(scheduling.ALERT_MILESTONES)
    next_alert = next(next_alert_pattern)
    wait_for_next_tournament = False
    has_alerted_tournament_start = False

    while not client.is_closed:
        salty_status = await get_salty_status()
        current_status = await check_for_tournament(salty_status)

        await update_presence(client, current_status.status)

        if current_status.status == TournamentStatus.SOON:
            if not wait_for_next_tournament:
                if current_status.matches_left <= min(scheduling.ALERT_MILESTONES):
                    wait_for_next_tournament = True
                if current_status.matches_left <= next_alert:
                    for channel in client.get_all_channels():
                        if channel.name in settings.ENABLED_CHANNELS:
                            await client.send_message(channel, current_status.text)

                    next_alert = next(next_alert_pattern)


        elif current_status.status == TournamentStatus.IN_PROGRESS:
            if not has_alerted_tournament_start:

                for channel in client.get_all_channels():
                    if channel.name in settings.ENABLED_CHANNELS:
                        await client.send_message(channel, current_status.text)
                has_alerted_tournament_start = True
                    

        else:
            wait_for_next_tournament = False
            has_alerted_tournament_start = False
        

        if current_status.status == TournamentStatus.NOT_EVEN_CLOSE:
            await asyncio.sleep(scheduling.NOT_EVEN_CLOSE_TIMER)
        
        elif current_status.status == TournamentStatus.SOON:
            await asyncio.sleep(scheduling.SOON_TIMER)
            
        elif current_status.status == TournamentStatus.IN_PROGRESS:
            await asyncio.sleep(scheduling.IN_PROGRESS_TIMER)

        else:
            await asyncio.sleep(scheduling.UH_OH_TIMER)

