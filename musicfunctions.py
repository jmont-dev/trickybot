import discord
from discord.ext import commands

class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='giorno')
    async def giorno(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="sounds/buzz.mp3")) #, after=lambda e: vc.disconnect())

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


