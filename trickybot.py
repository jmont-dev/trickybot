import discord
from discord.ext import commands

import os
import random
import asyncio
import numbers
import threading

import time
from datetime import datetime
#import pytz
#from tzlocal import get_localzone

from webfunctions import *
from musicfunctions import *

intents = discord.Intents().default()
intents.members = True
# create the instance

client = commands.Bot(command_prefix=".", intents=intents)
token = os.getenv("trickytoken")

client.load_extension('musicfunctions')

scores={}

buzzerListening = False

@client.command()
async def game(ctx) :
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send(f"You are not connected to a voice channel {ctx.message.author.name}")
        return

    global scores  

    scores={}
    players = [] #(list)
    for member in channel.members:
        players.append(member.name)
        scores[member.name] = 0

    await ctx.send(f"Starting new jeopardy game with players {players}.")

@client.command()
async def scores(ctx) :
    global scores
    await ctx.send(f"Game scores: {scores}.")

@client.command()
async def add(ctx, inPoints, inPlayer) :
    
    print(f"inPlayer {inPlayer} ", flush=True)
    print(f"inPoints {inPoints}", flush=True)

    #If the player swapped the syntax, swap the two inputs
    if inPlayer.isnumeric():
        player = inPoints
        points = int(inPlayer)
    else:
        player = inPlayer
        points = int(inPoints)

    if player=="":
        await ctx.send(f"No player entered. Cannot add points.")
        return

    if points==0:
        await ctx.send(f"No points specified.")

    global scores
    scores[player] += points
    await ctx.send(f"Added {points} points to player {player}. Player {player} now has {scores[player]} points.")

async def timeout(ctx):
    global buzzerListening
    if buzzerListening==True:
        buzzerListening = False
        temp = client.get_command(name='play')
        await temp.callback(ctx, "sounds/timeout.mp3")
        await ctx.send(f"Buzzer timed out without response.")


@client.command(brief='Listen for the next buzzer input.', description='Will identify the user who buzzes next with the .b command. Must be reset after a player buzzes in.')
async def listen(ctx) :
    global buzzerListening
    buzzerListening = True
    #Do an asyncio to timeout if no buzz in a period of time and play sound effect
    #threading.Timer(3, await timeout(ctx), [ctx]).start()
    #threading.Timer(2, timeout, [ctx]).start()


    await ctx.send(f"Listening for buzzer.")

@client.command()
async def b(ctx) :
    currentTime = datetime.now().strftime("%H:%M:%S.%f")
    global buzzerListening
    if buzzerListening==True:
        buzzerListening = False
        temp = client.get_command(name='play')
        await temp.callback(ctx, "sounds/buzz.mp3")
        await ctx.send(f"Player {ctx.message.author.name} buzzed first! They buzzed at time {currentTime}.")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.idle, activity = discord.Game("Listening to .help"))
    print("I am online")

@client.command()
async def imout(ctx) :
    await ctx.send(f"https://www.youtube.com/watch?v=JzFo83UOZY8")

@client.command()
async def marco(ctx) :
    links = getLinks("https://en.wikipedia.org/wiki/Marco", "Marco_")
    link = random.choice(links)
    await ctx.send(f"https://en.wikipedia.org/{link}")

@client.command()
async def ping(ctx) :
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}")

@client.command(name="whoami")
async def whoami(ctx) :
    await ctx.send(f"You are {ctx.message.author.name}")

@client.command()
async def encourage(ctx, person="") :

    if person=="":
        person = ctx.message.author.name

    messages = [f"You are a good person with a wonderful future ahead of you {person}.",
                f"I believe in you {person}.",
                f"All of your dreams will come true {person}."]

    message = random.choice(messages)      

    await ctx.send(message)

@client.command()
async def badbot(ctx) :

    messages = [f"I just did what you told me to.",
                f"I didn't deserve that.",
                f"I'm sad now.",
                f"*Sad beep*"]

    message = random.choice(messages)      

    await ctx.send(message, tts=True)

@client.command()
async def goodbot(ctx) :

    messages = [f"I am pleased.",
                f"I am glad you approve of me {ctx.message.author.name}.",
                f"This gives me great happiness.",
                f"*Happy beep*"]

    message = random.choice(messages)      

    await ctx.send(message, tts=True)

@client.command()
async def videogamename(ctx) :

    messages = [f"Tales of Bloomberia",
                f"Happy dogs.",
                f"*Happy beep*"]

    message = random.choice(messages)      

    await ctx.send(message)

@client.command()
async def dick(ctx, dickSize=5, jizz="") :
    dickString="8"
    for x in range(dickSize):
        dickString+="="
    dickString += "D"
    if jizz=="jizz":
        dickString +="~~~"
    await ctx.send(f"{dickString} {ctx.message.author.name}")

@client.command()
async def time(ctx) :
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    await ctx.send(f"The time is "+current_time)

@client.command()
async def teams(ctx, numTeams=2) :

    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send(f"You are not connected to a voice channel {ctx.message.author.name}")
        return

    unpickedPlayers = [] #(list)
    for member in channel.members:
        unpickedPlayers.append(member.name)

    if len(unpickedPlayers)==1:
        await ctx.send(f"Only one person in voice channel {channel.name}. Cannot make teams.")
        return

    teamMembers = []
    for team in range(0,numTeams):
        teamMembers.append([])

    team = 0
    while len(unpickedPlayers)>0:
        player = random.choice(unpickedPlayers)
        teamMembers[team].append(player)
        unpickedPlayers.remove(player)
        if team < numTeams-1:
            team += 1
        else:
            team = 0

    for team in range(0,numTeams):
        await ctx.send(f"Team {team+1}: {teamMembers[team]}")


client.run(token)