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

import requests
from bs4 import BeautifulSoup

import wikipedia
from googlesearch import search

from wordcloud import WordCloud
import matplotlib.pyplot as plt

#from chatterbot import ChatBot
#from chatterbot.trainers import ChatterBotCorpusTrainer

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

#Chatbot
#chatbot = ChatBot('Ron Obvious')
#trainer = ChatterBotCorpusTrainer(chatbot)
#trainer.train("chatterbot.corpus.english")

#GPT-2
#model_name = "124M"
#if not os.path.isdir(os.path.join("models", model_name)):
#	print(f"Downloading {model_name} model...")
#	gpt2.download_gpt2(model_name=model_name)

#file_name = "shakespeare.txt"
#if not os.path.isfile(file_name):
#	url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
#	data = requests.get(url)
	
#	with open(file_name, 'w') as f:
#		f.write(data.text)

#sess = gpt2.start_tf_sess()
#gpt2.finetune(sess,
#              file_name,
#              model_name=model_name,
#              steps=1000)   # steps is max number of training steps

#gpt2.generate(sess)

import torch
#from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline, Conversation
from transformers import pipeline, Conversation, set_seed

# initialize tokenizer and model from pretrained GPT2 model
#tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
#model = GPT2LMHeadModel.from_pretrained('gpt2')

#sequence = "Our model, called GPT-2 (a successor to GPT), was trained simply to predict the next word in 40GB of Internet text. Due to our concerns about malicious applications of the technology, we are not releasing the trained model. As an experiment in responsible disclosure, we are instead releasing a much smaller model for researchers to experiment with, as well as a technical paper."

#inputs = tokenizer.encode(sequence, return_tensors='pt')

#outputs = model.generate(inputs, max_length=200, do_sample=True)

#text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#print(text)

conversational_pipeline = pipeline("conversational")
conversation = Conversation()

#GPT-2 Text generator
generator = pipeline('text-generation', model='gpt2')

#GPT-2 Question Answering Pipeline
question_answering = pipeline("question-answering")

qa_knowledge = "Machine learning (ML) is the study of computer algorithms that improve automatically through experience. It is seen as a part of artificial intelligence. Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so. Machine learning algorithms are used in a wide variety of applications, such as email filtering and computer vision, where it is difficult or unfeasible to develop conventional algorithms to perform the needed tasks."

#Simple Transformers library

from simpletransformers.conv_ai import ConvAIModel

train_args = {
    "overwrite_output_dir": True,
    "reprocess_input_data": True
}


#model = ConvAIModel("gpt", "gpt_personachat_cache", use_cuda=False, args=train_args)
#model.train_model()

history = [
    "Hello, what's your name?",
    "Geralt",
    "What do you do for a living?",
    "I hunt monsters",
]

personality=[
    "My name is Geralt.",
    "I hunt monsters.",
    "I say hmm a lot.",
]

import lyricsgenius
genius = lyricsgenius.Genius(token)

from aitextgen import aitextgen

# Without any parameters, aitextgen() will download, cache, and load the 124M GPT-2 "small" model
ai = aitextgen(model="gpt2")

@client.command(aliases=['ai'])
async def aitextgen(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global ai

    ai_response = ai.generate_one(prompt=text, max_length=100)

    await ctx.send(f"{ai_response}")

@client.command()
async def compute(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    await ctx.send(f"{eval(text)}")

@client.command(aliases=[])
async def lyrics(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global genius

    song = genius.search_song(text)
    print(song.lyrics)

    max_chars_per_message = 2000

    remaining_chars = len(song.lyrics)
    messages_sent = 0


    if len(song.lyrics)>2000:
        await ctx.send(f"{song.lyrics[:2000]}")
    else:
        await ctx.send(f"{song.lyrics}")

#    while remaining_chars>0:
#        if remaining_chars>2000:
#            await ctx.send(f"{song.lyrics[(messages_sent+1)*2000:2000*(messages_sent+1)]}")
#            remaining_chars-=2000
#        else:
#            await ctx.send(f"{song.lyrics[(messages_sent+1)*2000:(messages_sent+1)*2000+remaining_chars]}")
#            remaining_chars = 0    


@client.command(aliases=[])
async def interact(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global model, history, personality

    response, history = model.interact_single(
        text,
        history,
        personality=personality
    )

    await ctx.send(f"{response}")

@client.command(aliases=['u'])
async def untrain(ctx, *args) :

    global qa_knowledge
    qa_knowledge = ""

    await ctx.send(f"Removed all training data.")

@client.command(aliases=['e'])
async def educate(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global qa_knowledge
    qa_knowledge += text

    await ctx.send(f"Added data to knowledge base.")

@client.command(aliases=['a'])
async def ask(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global question_answering, qa_knowledge

    result = question_answering(question=text, context=qa_knowledge)

    await ctx.send(f"{result['answer']}")

@client.command(aliases=['gen, finish'])
async def gpt2gen(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global generator
    set_seed(42)

    responses = generator(text, max_length=100, num_return_sequences=5)

    await ctx.send(f"{random.choice(responses)['generated_text']}")


@client.command(aliases=['cr'])
async def chatreset(ctx) :

    global conversation
    conversation = Conversation()

    await ctx.send(f"Conversation was reset.")

@client.command(aliases=['c'])
async def chat(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global conversation, conversational_pipeline
    #conversation = Conversation()
    conversation.add_user_input(text)
    response = conversational_pipeline(conversation)

    await ctx.send(f"{response}")

@client.command()
async def gpt2train(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    global inputs
    inputs = tokenizer.encode(text, return_tensors='pt')

    await ctx.send(f"Trained GPT-2 using provided text.")

@client.command()
async def gpt2generate(ctx) :

    global inputs, model, tokenizer

    outputs = model.generate(inputs, max_length=10, do_sample=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    await ctx.send(f"{response}")


#@client.command()
#async def chat(ctx, *args) :
#    text = ""
#    for string in args:
#        text+=(string+" ")
#
#    response = chatbot.get_response(text)
#    await ctx.send(f"{response}")

@client.command(aliases=['wc'])
async def wordcloud(ctx, num_messages=10) :

    if num_messages<1: num_messages=1
    if num_messages>1000: num_messages=1000

    await ctx.send(f"Generating wordcloud for past {num_messages} messages.")

    messages = await ctx.channel.history(limit=num_messages+2).flatten()

    all_text=""
    for msg in messages[2:]:
        all_text += msg.content

    #print(all_text)

    wordcloud = WordCloud().generate(all_text)
    wordcloud.to_file('wordcloud.png')

    await ctx.send(file=discord.File('wordcloud.png'))


@client.command()
async def timeout(ctx, time) :
    await ctx.send(f"I am in timeout for {time} seconds")

@client.command(aliases=['g'])
async def lmgtfy(ctx, *args) :
    text = ""
    for string in args:
        text+=(string+" ")

    await ctx.send(f"{search(text, num_results=1)[0]}")

@client.command()
async def wiki(ctx, *args) :
    query = ""
    for string in args:
        query+=(string+" ")

    try:
        results = wikipedia.search(query)
        summary = wikipedia.summary(results[0], sentences=3)
    except wikipedia.DisambiguationError as e:

        await ctx.send("Disambiguation error. Please search for one of the following options.")
        await ctx.send(f"{e.options}")       
        return

    await ctx.send(f"{summary}")

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

    temp = client.get_command(name='playlocal')
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


@client.command(aliases=['answ'],brief='Listen for the next buzzer input.', description='Will identify the user who buzzes next with the .b command. Must be reset after a player buzzes in.')
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

#@client.command()
#async def dongs(ctx) :
#
#    memes = [f"We slangin {ctx.message.author.name}?",
#            f"{ctx.message.author.name} got domed.",
#            f"Super Fergie Paper Mario",
#            f"Mike Bloomberg has a strong affinity for dogs.",
#            f"Settle it in Smash {ctx.message.author.name}."]       
#
#    await ctx.send(f"{random.choice(memes)}")

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
            f"https://www.youtube.com/watch?v=_MWDJ278zo4",
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

    await ctx.send(message, tts=False)

@client.command()
async def goodbot(ctx) :

    messages = [f"I am pleased.",
                f"I am glad you approve of me {ctx.message.author.name}.",
                f"This gives me great happiness.",
                f"*Happy beep*"]

    message = random.choice(messages)      

    await ctx.send(message, tts=False)

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