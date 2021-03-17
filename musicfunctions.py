import discord
from discord.ext import commands

class SimpleCog(commands.Cog):
    """SimpleCog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, *, our_input: str):
        """A simple command which repeats our input.
        In rewrite Context is automatically passed to our commands as the first argument after self."""

        await ctx.send(our_input)

    @commands.command(name='add', aliases=['plus'])
    @commands.guild_only()
    async def do_addition(self, ctx, first: int, second: int):
        """A simple command which does addition on two integer values."""

        total = first + second
        await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

    @commands.command(name='oro')
    async def oro(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="oro.mp3"), after=lambda e: vc.disconnect())

    @commands.command(name='stop')
    async def stop(self, ctx):
        vc = await getVoiceChannel(ctx)
        vc.stop()

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
        vc.disconnect()

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
    bot.add_cog(SimpleCog(bot))



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
#        return

