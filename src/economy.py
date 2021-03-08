import discord
import logging
import random
import json
import os
from discord import colour
from discord.embeds import Embed
from discord.ext import commands, tasks
from discord.utils import get

config = json.loads(open("./config/config.json", "r").read())
bot = commands.Bot(command_prefix=">")
bot.remove_command('help')
mainshop = config['shop']

# events
@bot.event
async def on_ready():
    change_staus.start()
    print('♦═════════════════════════════════════════════════♦')
    print(f'        • We have logged in as {bot.user}•')
    print('             • Polygon bot is online •')
    print('  • The log file is located at discord.log •')
    print('♦═════════════════════════════════════════════════♦')


@tasks.loop(seconds=config['config']['status']['delay'])
async def change_staus():
    status = config['config']['status']['text']
    await bot.change_presence(activity=discord.Game(random.choice(status)))

# commands
@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        title="Pong!",
        description=f"`The bot ping is {round(bot.latency * 1000)}ms!`",
        colour=ctx.author.colour
    )
    embed.set_footer(text="Polygon bot")
    await ctx.message.delete()
    await ctx.send(embed=embed)


@bot.command()
async def test(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(10, 100)

    await ctx.send(f"Someone gave you {earnings} polygons!")

    users[str(user.id)]["wallet"] += earnings

    with open("./data/mainbank.json", "w") as f:
        json.dump(users, f)


@bot.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(
        title=f"{ctx.author.name}'s balance", color=discord.Color.purple())
    em.add_field(name="Wallet balance", value=wallet_amt)
    em.add_field(name="Bank balance", value=bank_amt)
    await ctx.send(embed=em)


@bot.command()
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(1, 500)

    await ctx.send(f"Someone gave you {earnings} polygons!")

    users[str(user.id)]["wallet"] += earnings

    with open("./data/mainbank.json", "w") as f:
        json.dump(users, f)


@bot.command()
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[1]

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You dont have enough polygons!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")

    await ctx.send(f"You withdrew {amount} polygons!")


@bot.command()
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You dont have enough polygons!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author, amount, "bank")

    await ctx.send(f"You deposited {amount} polygons!")


@bot.command()
async def pay(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You dont have enough polygons!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive!")
        return

    await update_bank(ctx.author, -1*amount, "bank")
    await update_bank(member, amount, "bank")

    await ctx.send(f"You payed <@{member.id}> {amount} polygons!")


@bot.command()
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You dont have enough polygons!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive!")
        return

    final = []
    for i in range(3):
        a = random.choice(["X", "O", "Q"])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[0]:
        await update_bank(ctx.author, 2*amount)
        await ctx.send("You won!")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.send("You lost!")


@bot.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0] < 100:
        await ctx.send("It's not worth to rob this guy!")
        return

    earnings = random.randrange(0, bal[0])

    await update_bank(ctx.author, earnings)
    await update_bank(member, -1*earnings)

    await ctx.send(f"You robbed <@{member.id}> and got {earnings} polygons!")


@bot.command(aliases=["lb"])
async def leaderboard(ctx, x=1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} Richest People",
                       description="This is decided on the basis of raw money in the bank and wallet", color=discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = bot.get_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}",  inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)


@bot.command()
async def shop(ctx):
    em = discord.Embed(title="Shop", color=discord.Color.purple())

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name=name, value=f"${price} | {desc}")

    await ctx.send(embed=em)


@bot.command()
async def buy(ctx, item, amount=1):

    if amount < 1:
        await ctx.send(f"You cant buy {amount} items!")
        return

    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have enough polygons in your wallet to buy {amount} {item}")
            return

    await ctx.send(f"You just bought {amount} {item}")


@bot.command()
async def inventory(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        inv = users[str(user.id)]["inventory"]
    except:
        inv = []

    em = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.purple())
    for item in inv:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name=name, value=amount)

    await ctx.send(embed=em)


@bot.command()
async def sell(ctx, item, amount=1):

    if amount < 1:
        await ctx.send(f"You cant sell {amount} items!")
        return

    await open_account(ctx.author)
    res = await sell_this(ctx.author, item, amount)
    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your inventory.")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your inventory.")
            return
    await ctx.send(f"You just sold {amount} {item}.")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = 0.9 * item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["inventory"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["inventory"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open("./data/mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

        with open("./data/mainbank.json", "w") as f:
            json.dump(users, f)
        return True


async def get_bank_data():
    with open("./data/mainbank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("./data/mainbank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["inventory"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["inventory"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["inventory"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["inventory"] = [obj]

    with open("./data/mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, "wallet")

    return [True, "Worked"]

# token
if __name__ == '__main__':
    bot.run(config['config']['token'])
