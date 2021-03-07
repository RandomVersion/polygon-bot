import discord
import logging
import asyncio
import random
from discord import colour
from discord.ext import commands, tasks
from discord.utils import get

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=">")

bot.remove_command('help')

#events

@bot.event
async def on_ready():
    change_staus.start()
    print('♦═════════════════════════════════════════════════♦')
    print('        • We have logged in as {0.user}•'.format(bot))
    print('             • Polygon bot is online •')
    print('  • The log file is located at discord.log •')
    print('♦═════════════════════════════════════════════════♦')

@tasks.loop(seconds=60)
async def change_staus():
  status = ['Polygon stock market','Poly-gone','hi polugo n donute','Super Polygon 64']
  await bot.change_presence(activity=discord.Game(random.choice(status)))

#commands
@bot.command()
async def test(ctx):
    await ctx.send("Test")

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send('{0} joined on `{0.joined_at}`'.format(member))
    await ctx.message.delete()

@bot.command()
async def help(ctx):
    embed = discord.Embed(
          title = "Help menu",
          description = "```>test\n>help```",
          colour = ctx.author.colour
        )
    embed.set_footer(text="Polygon bot")
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed = discord.Embed(
          title = "Pong!",
          description = f"`The bot ping is {round(bot.latency * 1000)}ms!`",
          colour = ctx.author.colour
        )
    embed.set_footer(text="Polygon bot")
    await ctx.message.delete()
    await ctx.send(embed=embed)



#token
bot.run("")
