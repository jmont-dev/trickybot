import discord
from discord.ext import commands
import os
from datetime import datetime
import random

intents = discord.Intents().default()
intents.members = True
# create the instance

client = commands.Bot(command_prefix=".", intents=intents)
token = os.getenv("trickytoken")

@client.event
async def on_ready() :
    await client.change_presence(status = discord.Status.idle, activity = discord.Game("Listening to .help"))
    print("I am online")

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
                f"This gives me great happiness.",
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

    for team in range(numTeams):
        teamMembers = []
        player = random.choice(unpickedPlayers)
        teamMembers.append(player)
        unpickedPlayers.remove(player)
        await ctx.send(f"Team {team+1}: {teamMembers}")

@client.command()
async def clear(ctx, amount=3) :
    await ctx.channel.purge(limit=amount)


client.run(token)