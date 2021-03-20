import discord
from discord.ext import commands
from discord.utils import get

import os
import random
import asyncio
import numbers
import threading

import time
from datetime import datetime

from webfunctions import *
from musicfunctions import *

intents = discord.Intents().default()
intents.members = True

# create the instance
client = commands.Bot(command_prefix=".", intents=intents)
token = os.getenv("trickytoken")

#Load external cogs
client.load_extension('musicfunctions')

#Jeopary Globals
scores={}
lastDMs={}
buzzerListening = False

@client.command()
async def game(ctx) :
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send(f"You are not connected to a voice channel {ctx.message.author.name}")
        return

    global scores, lastDMs  

    scores={}
    lastDMs={}

    players = []
    for member in channel.members:
        players.append(member.name)
        scores[member.name] = 0

    await ctx.send(f"Starting new jeopardy game with players {players}.")

@client.command()
async def addplayer(ctx, playerName="") :
    if playerName=="":
        return
    
    global scores
    scores[playerName] = 0
    await ctx.send(f"Player {playerName} has been added.")


@client.command()
async def scores(ctx) :
    global scores
    await ctx.send(f"Game scores: {scores}.")

@client.command()
async def final(ctx) :
    global lastDMs

    allAnswers=""

    for player, answer in lastDMs.items(): 
        allAnswers+=f"{player} : {answer} \n" 

    await ctx.send(f"Final Jeopardy Answers: \n {allAnswers}")

@client.command()
async def add(ctx, inPoints, inPlayer) :
    #If the player swapped the syntax, swap the two inputs
    try:
        int(inPlayer)
        player = inPoints
        points = int(inPlayer)
    except ValueError:
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
    #Quick solution since Threading.timer isn't working
    await asyncio.sleep(10)
    global buzzerListening
    if buzzerListening==True:
        buzzerListening = False
        temp = client.get_command(name='play')
        await temp.callback(ctx, "sounds/timeout.mp3")
        await ctx.send(f"Buzzer timed out without response.")


#Add function to create music-player like UI after a question. Have the value of the question in the command.
#.listen 400
#When the user clicks on a reaction, calculate who clicked first and then write whether or not they answered correctly with a new command
#.answer write wrong neutral
#This will add/subtract the number of points specified in the last listen command to the user who clicked automatically. If wrong, the listen is restarted automatically and the UI is reposted.

@client.command(aliases=['l'],brief='Listen for the next buzzer input.', description='Will identify the user who buzzes next with the .b command. Must be reset after a player buzzes in.')
async def listen(ctx) :
    global buzzerListening
    buzzerListening = True
    mytask = asyncio.create_task(timeout(ctx))
    #Do an asyncio to timeout if no buzz in a period of time and play sound effect
    #threading.Timer(3, await timeout(ctx), [ctx]).start()
    #threading.Timer(2, (await timeout(ctx)), [ctx]).start()
    await ctx.send(f"Listening for buzzer.")

@client.command(aliases=['q'],brief='Listen for the next buzzer input.', description='Will identify the user who buzzes next with the .b command. Must be reset after a player buzzes in.')
async def question(ctx, points=0) :
    
    if points==0:
        await ctx.send(f"Must specify a points value for the question.")
        return

    global buzzerListening
    buzzerListening = True
    mytask = asyncio.create_task(timeout(ctx))
    #Do an asyncio to timeout if no buzz in a period of time and play sound effect
    #threading.Timer(3, await timeout(ctx), [ctx]).start()
    #threading.Timer(2, (await timeout(ctx)), [ctx]).start()
    
    msg = await ctx.send(f"Question is for ${points}.") 
    await msg.add_reaction('⏺️')


@client.event
async def on_reaction_add(reaction, user):
    #Check for the record button on questions
    if reaction.emoji ==  '⏺️' and reaction.message.content.startswith("Question") and user.name!="trickybot":
        #get(reaction.message.ctx.server.emojis, name="record_button"):
        #'\N{Black Circle for Record}':

        #'Congratulations!' in reaction.message.content and
        #add reaction to message
        print(f"Got reaction from {user.name}")
        emoji = '\N{THUMBS UP SIGN}'
        await reaction.message.add_reaction(emoji)
        await client.b(ctx)

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
async def on_message(message):
    if isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user:
        global lastDMs
        lastDMs[message.author.name]=message.content
        await message.channel.send(f'You relayed this to me: {message.content}')
    
    await client.process_commands(message)

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.idle, activity = discord.Game("Listening to .help"))
    print("I am online")

@client.command()
async def imout(ctx) :
    await ctx.send(f"https://www.youtube.com/watch?v=JzFo83UOZY8")

@client.command(aliases=['gme','stonk'])
async def melvin(ctx) :
    melvins = [f"https://www.youtube.com/watch?v=y5YOCPzAX8M",
            f"https://twitter.com/i/status/1354809325412225026"]

    melvin = random.choice(melvins)   

    await ctx.send(f"{melvin}")  

@client.command()
async def dongs(ctx) :

    memes = [f"We slangin {ctx.message.author.name}?",
            f"{ctx.message.author.name} got domed.",
            f"Super Fergie Paper Mario",
            f"Mike Bloomberg has a strong afinity for dogs.",
            f"Settle it in Smash {ctx.message.author.name}."]       

    await ctx.send(f"{random.choice(memes)}")

@client.command()
async def vibe(ctx) :

    cats = [f"https://www.youtube.com/watch?v=eZTS4cL4Euo",
            f"https://www.youtube.com/watch?v=bFzrB-lo9k8",
            f"https://www.youtube.com/watch?v=krlaWEIx4XY",
            f"https://www.youtube.com/watch?v=2hpoLCpcWF4",
            f"https://www.youtube.com/watch?v=dsODRfCMRoM"]

    cat = random.choice(cats)   

    await ctx.send(f"{cat}")

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