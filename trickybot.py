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

from playsound import playsound
from gtts import gTTS
import pyttsx3

from webfunctions import *
from musicfunctions import *

#Must load intents in the new Discord API
intents = discord.Intents().default()
intents.members = True

# Create the instance. Make sure "trickytoken" is set in the environment to your bot token beforehand.
client = commands.Bot(command_prefix=".", intents=intents)
token = os.getenv("trickytoken")

#Load external cogs
client.load_extension('musicfunctions')

#Jeopary Globals
scores={}
wagers={}
lastDMs={}
buzzerListening = False
userAnswering = ""
lastQuestionValue = 0

#Text to speech engine
engine = pyttsx3.init()

@client.command(aliases=['s'])
async def speech(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")
    
    language = 'en'  
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save("sounds/text.mp3")

    #global engine
    #voices = engine.getProperty("voices")
    #print(voices)
    #engine.save_to_file(mytext, "sounds/text.mp3")
    #engine.runAndWait()

    temp = client.get_command(name='play')
    await temp.callback(ctx, "sounds/text.mp3")

    # Playing the converted file
    #os.system("mpg321 sounds/text.mp3")

@client.command()
async def game(ctx) :
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send(f"You are not connected to a voice channel {ctx.message.author.name}")
        return

    global scores, lastDMs, wagers  

    scores={}
    lastDMs={}
    wagers={}

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

    await ctx.send(f"Final Jeopardy Answers: \n{allAnswers}")

@client.command()
async def wagers(ctx) :
    global wagers

    allWagers=""

    for player, wager in wagers.items(): 
        allWagers+=f"{player} : {wager} \n" 

    await ctx.send(f"Wagers: \n{allWagers}")

@client.command()
async def repeat(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    await ctx.send(f"{text}")

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

    global buzzerListening, lastQuestionValue
    buzzerListening = True
    global timertask
    timertask = asyncio.create_task(timeout(ctx))
    lastQuestionValue = points
    msg = await ctx.send(f"Question is for ${lastQuestionValue}.") 
    await msg.add_reaction('⏺️')


@client.command(aliases=['a'],brief='Listen for the next buzzer input.', description='Will identify the user who buzzes next with the .b command. Must be reset after a player buzzes in.')
async def answer(ctx) :   

    await msg.add_reaction('⏺️')

@client.event
async def on_reaction_add(reaction, user):

    global lastQuestionValue, buzzerListening, timertask, userAnswering
    ctx = await client.get_context(reaction.message)

    #Check if the user pressed the record button
    if buzzerListening and reaction.emoji =='⏺️' and reaction.message.content.startswith("Question") and user.name!="trickybot":
        #get(reaction.message.ctx.server.emojis, name="record_button"):
         
        userAnswering = user.name

        await client.get_command('b').callback(ctx, userAnswering)
        await reaction.message.add_reaction("✅")
        await reaction.message.add_reaction("❌")
        timertask.cancel()

    #If the user said the right answer, award them points
    if reaction.emoji =='✅' and reaction.message.content.startswith("Question") and user.name!="trickybot":
        

        ctx = await client.get_context(reaction.message)
        await client.get_command(name='add').callback(ctx, lastQuestionValue, userAnswering)        
        await reaction.message.delete()

        await client.get_command(name='play').callback(ctx, "sounds/ding.mp3")
        await client.get_command('scores').callback(ctx)

    #If the user said the wrong answer, dock them points
    if reaction.emoji =='❌' and reaction.message.content.startswith("Question") and user.name!="trickybot":
        

        ctx = await client.get_context(reaction.message)
        await client.get_command(name='add').callback(ctx, -lastQuestionValue, userAnswering)
        await client.get_command('scores').callback(ctx)
        await reaction.message.delete()

        await client.get_command(name='play').callback(ctx, "sounds/wrong.mp3")

        #Pose the question to the players again
        await client.get_command(name='question').callback(ctx, lastQuestionValue)


@client.command()
async def wager(ctx, points=0) :
    if points==0:
        await ctx.send(f'You must specify the amount to wager.')
        return

    global wagers
    wagers[ctx.message.author.name]=points
    await ctx.send(f'{ctx.message.author.name} wagered ${points}')

@client.command()
async def b(ctx, player="") :
    currentTime = datetime.now().strftime("%H:%M:%S.%f")
    global buzzerListening
    if buzzerListening==True:
        buzzerListening = False

        temp = client.get_command(name='play')
        await temp.callback(ctx, "sounds/buzz.mp3")
        if player=="":
            player = ctx.message.author.name
        await ctx.send(f"Player {player} buzzed first! They buzzed at time {currentTime}.")

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
async def goodshit(ctx) :     

    text = "👌👀👌👀👌👀👌👀👌👀 good shit go౦ԁ sHit👌 thats ✔ some good👌👌shit right👌👌there👌👌👌 right✔there ✔✔if i do ƽaү so my self 💯 i say so 💯 thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ💯 👌👌 👌НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ👌 👌👌 👌 💯 👌 👀 👀 👀 👌👌Good shit"

    await ctx.send(f"{text}")

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