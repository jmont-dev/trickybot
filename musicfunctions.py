import discord
from discord.ext import commands

class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play')
    async def play(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="oro.mp3")) #, after=lambda e: vc.disconnect())

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


#@client.command(
#    name='oro',
#    description='Plays an awful vuvuzela in the voice channel',
#    pass_context=True,
#)

#async def oro(ctx):
    # grab the user who sent the command
#    user = ctx.message.author
#    voice_channel = ctx.author.voice.channel
#    channel = None
#    if voice_channel != None:
#        channel = voice_channel.name
#        await ctx.send('User is in channel: ' + channel)
        
#        vc = await voice_channel.connect()
#        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="oro.mp3"), after=lambda e: vc.disconnect())

        #vc.is_playing()
        #vc.pause()
        #vc.resume()
        #vc.stop()        
        #vc.disconnect()

#        vc = await ctx.join_voice_channel(voice_channel)
#        player = vc.create_ffmpeg_player('oro.mp3', after=lambda: print('done'))
#        player.start()
#        while not player.is_done():
#            await asyncio.sleep(1)
#        player.stop()
#        await vc.disconnect()
#    else:
#        await ctx.send('User is not in a channel.')


