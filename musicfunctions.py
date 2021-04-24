import discord
from discord.ext import commands

import youtube_dl
import os


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='giorno')
    async def giorno(self, ctx):
        vc = await getVoiceChannel(ctx)
        await ctx.send(f"I, trickybot, have a dream.")
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="sounds/oro.mp3")) #, after=lambda e: vc.disconnect())

    @commands.command(name='muda')
    async def muda(self, ctx):
        vc = await getVoiceChannel(ctx)
       # await ctx.send(f"I, trickybot, have a dream.")
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="sounds/muda.mp3")) #, after=lambda e: vc.disconnect())

    @commands.command(name='play')
    async def play(ctx, filename=""):
        vc = await getVoiceChannel(ctx)
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename)) #, after=lambda e: vc.disconnect())

    @commands.command(name='stop')
    async def stop(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.stop()
        await vc.disconnect()

    @commands.command(name='pause')
    async def pause(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.pause()

    @commands.command(name='resume')
    async def resume(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.resume()

    @commands.command(name='disconnect')
    async def disconnect(self, ctx):
        vc = await getVoiceChannel(ctx)
        await vc.disconnect()

    @commands.command(name='youtube')
    async def youtube(self, ctx, url : str):
        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
        except PermissionError:
            await ctx.send("Wait for the current playing music to end or use the 'stop' command")
            return

        vc = await getVoiceChannel(ctx)

        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        vc.play(discord.FFmpegPCMAudio("song.mp3"))

#Get the voice channel of the author
async def getVoiceChannel(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
        return vc
    else:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
        return vc

def setup(bot):
    bot.add_cog(MusicPlayer(bot))
