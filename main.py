import discord
from datetime import datetime, timezone
from discord.ext.commands.core import check
from discord_slash.context import ComponentContext, InteractionContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash import SlashCommand
from dotenv import load_dotenv
import os
import json
import asyncio
from discord.ext import commands
import time
from PIL import Image
from io import BytesIO

load_dotenv()

intents = discord.Intents().all()

DISCORD_TOKEN = os.getenv('discord_token')
BASED = ['based', 'baste']
CRINGE = ['cringe', 'soy']
LEADERBOARD_BASE_COUNT = 5

bot = commands.Bot(
    command_prefix='./',
    description='Based Bot, the most based bot on Discord.',
    intents=intents)

slash = SlashCommand(bot)

def readFile(fileName):
    fileObj = open(fileName, "r")  # opens the file in read mode
    words = fileObj.read()  # .splitlines() #puts the file into an array
    fileObj.close()
    return words

def blacklist_check(author_id, guild_id):
    blisted_users = readFile('./blacklisted/sortedblacklistedusers.txt')
    print(blisted_users)
    blisted_guilds = readFile('./blacklisted/sortedblacklistedguilds.txt')
    if str(author_id) in blisted_users or str(guild_id) in blisted_guilds:
        return True
    else:
        return False
   
def checkFileExists(file):
    return os.path.isfile(file)

def getBotChannel(ctx):
    if not checkFileExists(f'./data/server_data/{ctx.guild.id}.json'):
        return bot.get_channel(ctx.channel.id)
    elif checkFileExists(f'./data/server_data/{ctx.guild.id}.json'):
        f = open(f'./data/server_data/{ctx.guild.id}.json', 'r')
        json_object = json.load(f)
        f.close()
        return bot.get_channel(json_object['bot_channel'])
    

def getTicks():
    return int(time.time())

def generateBasedTitle(count):
    if (count // 10) <= 1:
        return "newb"
    elif (count // 10) <= 3:
        return "a bit based"
    elif (count // 10) <= 5:
        return "distinguishably based"
    elif (count // 10) <= 7:
        return "Knight of the Based-ness"
    elif (count // 10) <= 9:
        return "Dangerously Based"
    elif (count // 10) <= 15:
        return "One of the Based-est"
    elif (count // 10) <= 20:
        return "ERROR- Too Based"
    else:
        return "The Most Based"

def generateCringeTitle(count):
    if (count // 10) <= 1:
        return "newb"
    elif (count // 10) <= 3:
        return "a bit cringe"
    elif (count // 10) <= 5:
        return "slightly soy"
    elif (count // 10) <= 7:
        return "extreme soy"
    elif (count // 10) <= 9:
        return "pure soy cringe"
    elif (count // 10) <= 15:
        return "Only Cringe Opinions"
    elif (count // 10) <= 20:
        return "ERROR- Too Cringe"
    else:
        return "The Most Cringe"

async def updateLeaderboard(id, count, boc):
    name = await bot.fetch_user(id)
    print(str(name).split('#')[0])
    data = {
        "discord_id": int(id),
        "discord_id_string": str(id),
        f"{boc}_count": count,
        "ranking": 0,
        "discord_name": str(name).split('#')[0]
    }

    f = open(f'./data/{boc}leaderboard.json', 'r')
    nested_json = json.load(f)
    f.close()

    for person in nested_json['data']:
        if person['discord_id_string'] == str(id):
            f = open(f'./data/{boc}leaderboard.json', 'w')    
            person[f'{boc}_count'] = count
            person['discord_name'] = str(name).split('#')[0]
            nested_json['data'] = sorted(nested_json['data'], key=lambda r: r[f'{boc}_count'], reverse=True)
            for count, value in enumerate(nested_json['data']):
                value['ranking'] = count
            json.dump(nested_json, f, indent=4)
            f.close()
            print('success')
            return
    

    f = open(f'./data/{boc}leaderboard.json', 'w')
    nested_json['data'] += [data]
    json.dump(nested_json, f, indent=4)
    f.close()
    
    f = open(f'./data/{boc}leaderboard.json', 'w')
    nested_json['data'] = sorted(nested_json['data'], key=lambda r: r[f'{boc}_count'], reverse=True)
    json.dump(nested_json, f, indent=4)
    f.close()

    for count, value in enumerate(nested_json['data']):
        value['ranking'] = count
    
    f = open(f'./data/{boc}leaderboard.json', 'w')
    json.dump(nested_json, f, indent=4)
    f.close()


async def updateLeaderboardWithID(id, boc):
    with open(f'./data/{id}.json', 'r') as f:
        json_object = json.load(f)

        if json_object['data'][boc][f'{boc}_count'] < int(LEADERBOARD_BASE_COUNT):
            return
        
        await updateLeaderboard(id, json_object['data'][boc][f'{boc}_count'], boc)


def updateServerCount(server_id):
    with open(f'./data/server_data/{server_id}.json', 'r') as f:
        json_object = json.load(f)

        json_object['command_count'] += 1

        with open(f'./data/server_data/{server_id}.json', 'w') as f:
            json.dump(json_object, f, indent=4)


@bot.event
async def on_ready():
    global botUptime
    botUptime = datetime.utcnow()
    print(f'Logged in as:\n{bot.user.name}#{bot.user.discriminator} at {botUptime}.\n----------')


async def createUser(message, member):
    with open(f'./data/{member.id}.json', 'w') as f:
        data = {
            "discord_id": member.id,
            "discord_name": member.name,
            "avatar_url": (await bot.fetch_user(member.id)).avatar,
            "server_id": message.guild.id,
            "created_at": getTicks(),
                "data": {
                    "based": {
                        "based_count": 0,
                        "based_title": "newb",
                        "last_based_at": getTicks(),
                        "last_based_by": message.author.id
                    },
                    "cringe": {
                        "cringe_count": 0,
                        "cringe_title": "newb",
                        "last_cringed_at": getTicks(),
                        "last_cringed_by": message.author.id
                    }
                },
                "settings": {
                    "public_profile": True,
                    "show_badges": True
                },
                "badges": {
                    "alpha_tester": False,
                    "early_adopter": False,
                    "developer": False,
                    "owner": False,
                    "donator": False,
                    "200_based_count": False,
                    "200_cringe_count": False,
                    "100_based_count" : False,
                    "100_cringe_count": False,
                    "50_based_count": False,
                    "50_cringe_count": False
                }
        }
        json.dump(data, f, indent=4)

async def AntiSpamBased(message, member):
    if member.id == message.author.id:
        return True
    f = open(f'./data/{member.id}.json', 'r')
    json_object = json.load(f)
    f.close()

    if json_object['data']['based']['last_based_at'] + 3 >= getTicks():
        print(json_object['data']['based']['last_based_at'] + 3, getTicks())
        return True
    elif json_object['data']['based']['last_based_at'] + 100 >= getTicks() and json_object['data']['based']['last_based_by'] == message.author.id:
        return True
    return False

async def AntiSpamCringed(message, member):
    if member.id == message.author.id:
        return True
    f = open(f'./data/{member.id}.json', 'r')
    json_object = json.load(f)
    f.close()

    if json_object['data']['cringe']['last_cringed_at'] + 3 >= getTicks():
        print(json_object['data']['cringe']['last_cringed_at'] + 3, getTicks())
        return True
    elif json_object['data']['cringe']['last_cringed_at'] + 100 >= getTicks() and json_object['data']['cringe']['last_cringed_by'] == message.author.id:
        return True
    return False

async def exceptions(message):
    rejected_words = ['not', 'arent', 'aren\'t']
    words = message.content.lower().split()
    if 'based' in words:
        if words[words.index('based')-1].lower() in rejected_words:
            return True
        elif message.content == './mybasedcount' or message.content[0] == './basedcount':
            return True
        return False

async def BasedTax(message):
    f_bot = open('./data/870487608105525298.json', 'r')
    json_object = json.load(f_bot)
    f_bot.close()

    json_object['data']['based']['based_count'] += 1
    json_object['data']['based']['based_title'] = generateBasedTitle(json_object['data']['based']['based_count'])
    json_object['data']['based']['last_based_by'] = message.author.id

    f_bot = open(f'./data/870487608105525298.json', 'w')
    json.dump(json_object, f_bot, indent=4)
    f_bot.close()
    #await updateLeaderboardWithID('870487608105525298', 'based')

async def addBased(message, member):
    f = open(f'./data/{member.id}.json', 'r')
    json_object = json.load(f)
    f.close()
    
    json_object['data']['based']['based_count'] += 1
    json_object['data']['based']['based_title'] = generateBasedTitle(json_object['data']['based']['based_count'])
    json_object['data']['based']['last_based_at'] = getTicks()
    json_object['data']['based']['last_based_by'] = message.author.id
    json_object['avatar_url'] = (await bot.fetch_user(member.id)).avatar
    json_object['discord_name'] = str((await bot.fetch_user(member.id)).name).split('#')[0]

    if json_object['data']['based']['based_count'] >= 50:
        json_object['badges']['50_based_count'] = True
    elif json_object['data']['based']['based_count'] >= 100:
        json_object['badges']['100_based_count'] = True
    elif json_object['data']['based']['based_count'] >= 200:
        json_object['badges']['200_based_count'] = True
    
    if message.guild.id == 853753017576587285 and json_object['data']['based']['based_count'] > 150:
        cringe_role = message.guild.get_role(899346066196017193)
        await member.add_roles(cringe_role)

    await message.add_reaction('👍')

    f = open(f'./data/{member.id}.json', 'w')
    json.dump(json_object, f, indent=4)
    f.close()
        
async def addCringe(message, member):
    f = open(f'./data/{member.id}.json', 'r')
    json_object = json.load(f)
    f.close()

    json_object['data']['cringe']['cringe_count'] += 1
    json_object['data']['cringe']['cringe_title'] = generateCringeTitle(json_object['data']['cringe']['cringe_count'])
    json_object['data']['cringe']['last_cringed_at'] = getTicks()
    json_object['data']['cringe']['last_cringed_by'] = message.author.id
    json_object['avatar_url'] = (await bot.fetch_user(member.id)).avatar
    json_object['discord_name'] = str((await bot.fetch_user(member.id)).name).split('#')[0]

    if json_object['data']['cringe']['cringe_count'] >= 50:
        json_object['badges']['50_cringe_count'] = True
    elif json_object['data']['cringe']['cringe_count'] >= 100:
        json_object['badges']['100_cringe_count'] = True
    elif json_object['data']['cringe']['cringe_count'] >= 200:
        json_object['badges']['200_cringe_count'] = True

    f = open(f'./data/{member.id}.json', 'w')
    json.dump(json_object, f, indent=4)
    f.close()

    await message.add_reaction('👍')
    
    if message.guild.id == 853753017576587285:
        if json_object['data']['cringe']['cringe_count'] > 150:
            cringe_role = message.guild.get_role(898636807250538526)
            await member.add_roles(cringe_role)

async def buttonCount(message, member, boc):
    def check(author: ComponentContext):
            return message.author.id == author.author_id
    buttons = [
        create_button(style=ButtonStyle.green, label='Yes!', custom_id='Yes'),
        create_button(style=ButtonStyle.green, label='No!', custom_id='No')
    ]
    action_row = create_actionrow(*buttons)
    origin = await message.channel.send(f"<@{message.author.id}>, would you like to grant **{member.name}** a {boc} point?",components=[action_row])
    button_ctx: ComponentContext = await wait_for_component(bot, components = action_row, check=check)
    await button_ctx.edit_origin(content="Got it!")
    if button_ctx.custom_id != "Yes":
        await origin.delete()
        return
    await origin.delete()
    if boc == "based":
        await addBased(message, member)
    elif boc == "cringe":
        await addCringe(message, member)

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    if message.content.split()[0].lower() == 'based' and message.mentions:
        # Based stuff goes here
        
        for member in message.mentions:
            updateServerCount(message.guild.id)

            if not checkFileExists(f'./data/{member.id}.json'):
                await createUser(message, member)
                #await updateLeaderboardWithID(member.id, 'based')
            
            elif checkFileExists(f'./data/{member.id}.json'):
                if await AntiSpamBased(message, member):
                    return
                #await updateLeaderboardWithID(member.id, 'based')
                await BasedTax(message)

        await message.add_reaction('👍')

    elif message.content.split()[0].lower() == 'cringe' and message.mentions:
        # cringe stuff goes here

        for member in message.mentions:
            updateServerCount(message.guild.id)
            
            if not checkFileExists(f'./data/{member.id}.json'):
                await createUser(message, member)
            
            elif checkFileExists(f'./data/{member.id}.json'):
                if await AntiSpamCringed(message, member):
                    return

                await addCringe(message, member)
                #await updateLeaderboardWithID(member.id, 'cringe')
        
        await message.add_reaction('👍')

    if message.content.split()[0].lower() != 'based' and "based" in message.content.lower() and message.mentions:
        for member in message.mentions:
            if not checkFileExists(f'./data/{member.id}.json'):
                await createUser(message, member)
                await buttonCount(message, member, 'based')
                await message.add_reaction('👍')
            if await AntiSpamBased(message, member) or await exceptions(message):
                return
            await buttonCount(message, member, 'based')
    
    elif message.content.split()[0].lower() != 'cringe' and "cringe" in message.content.lower() and message.mentions:
        for member in message.mentions:
            if not checkFileExists(f'./data/{member.id}.json'):
                await createUser(message, member)
                await buttonCount(message, member, 'cringe')
                await message.add_reaction('👍')
            if await AntiSpamCringed(message, member) or await exceptions(message):
                return
            await buttonCount(message, member, 'cringe')

    await bot.process_commands(message)



@bot.command()
async def whoami(ctx):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    embed = discord.Embed(title = 'Based Bot', description = '**The most based bot on Discord.**', color = 0xFFCC)
    embed.add_field(name='Command Help', value= 'For command help, [Click Here](https://5late.github.io/guides/HIDDEN-BASED-BOT.html#commands)')
    embed.add_field(name='Creator', value='My creator is ``Slate#7879``')

    channel = getBotChannel(ctx)
    await channel.send(f'<@{ctx.author.id}>!')
    await channel.send(embed=embed)


@bot.command()
async def reset(ctx, boc, person, new=''):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not ctx.author.id == 564466359107321856:
        return
    if not checkFileExists(f'./data/{person}.json'):
        return await ctx.send('File not found')
    elif checkFileExists(f'./data/{person}.json'):
        f = open(f'./data/{person}.json', 'r')
        json_object = json.load(f)
        f.close()

        if boc.lower() == 'based':
            if new == '':
                json_object['data'][boc][f'based_count'] = 0
            else:
                json_object['data'][boc]['based_count'] = int(new)
            json_object['data'][boc][f'based_title'] = 'newb'
        elif boc.lower() == 'cringe':
            if new == '':
                json_object['data'][boc][f'cringe_count'] = 0
            else:
                json_object['data'][boc]['cringe_count'] = int(new)
            json_object['data'][boc][f'cringe_title'] = 'newb'

        f = open(f'./data/{person}.json', 'w')
        json.dump(json_object, f, indent=4)
        f.close()
        return await ctx.send(f'Reset <@{person}> {boc} score to new value.')
        

@bot.command()
async def blacklist(ctx, type, arg):
    if blacklist_check(ctx):
        return
    if not ctx.author.id == 564466359107321856:
        return
    def readFile(fileName):
        fileObj = open(fileName, "r")  # opens the file in read mode
        words = fileObj.read().splitlines()  # puts the file into an array
        fileObj.close()
        return words

    if type.lower() == 'u':
        blisted = readFile('./blacklisted/blacklistedusers.txt')

        blisted.append(arg)

        with open('./blacklisted/blacklistedusers.txt', 'a') as f:
            f.write(f'{arg}\n')

        await ctx.send('Successfully blacklisted user with ID ||``{}``||'.format(arg))

    elif type.lower() == 'g':
        blisted_guilds = readFile('./blacklisted/blacklistedusers.txt')

        blisted_guilds.append(arg)

        with open('./blacklisted/blacklistedguilds.txt', 'a') as f:
            f.write(f'{arg}\n')

        await ctx.send('Successfully blacklisted server with ID ||``{}``||'.format(arg))

    start = await ctx.send(f'Hello <@{ctx.author.id}>, I will begin cleaning up blacklist files.')

    def countDuplicates(seq):
        return len(seq) - len(set(seq))

    blisted_users = readFile('./blacklisted/blacklistedusers.txt')
    report = await ctx.send(f'There are ``{countDuplicates(blisted_users)}`` in USER file. Clearing them up...')
    blisted_guilds = readFile('./blacklisted/blacklistedguilds.txt')
    await asyncio.sleep(2)
    await report.edit(content=f'There are ``{countDuplicates(blisted_guilds)}`` in GUILD file. Clearing them up...')

    seen_users = set()
    outfile_guild = open('./blacklisted/sortedblacklistedguilds.txt', 'w')
    for line in open('./blacklisted/blacklistedguilds.txt', 'r'):
        if line in seen_users:
            print(line)
        else:
            outfile_guild.write(line)
            seen_users.add(line)
    outfile_guild.close()

    seen = set()
    outfile_users = open('./blacklisted/sortedblacklistedusers.txt', 'w')
    for liner in open('./blacklisted/blacklistedusers.txt', 'r'):
        if liner not in seen:
            outfile_users.write(liner)
            seen.add(liner)
    outfile_users.close()

    await start.delete()
    await report.delete()
    await ctx.send(f'<@{ctx.author.id}> I have cleared up both blacklist files. Cheers 🍻')


@bot.command()
async def mybasedcount(ctx):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return print(blacklist_check(ctx.author.id, ctx.guild.id))
    if not checkFileExists(f'./data/{ctx.author.id}.json'):
        return await ctx.send('Nothing to show. What a boring person.')
    elif checkFileExists:
        f = open(f'./data/{ctx.author.id}.json', 'r')
        json_object = json.load(f)
        f.close()

        badges = ''

        if json_object['badges']['owner'] == True:
            badges += '<:owner:876856567880896602>'
        if json_object['badges']['early_adopter'] == True:
            badges += '<:early_adopter:876856567536947281>'
        if json_object['badges']['alpha_tester'] == True:
            badges += '<:alpha_tester:876856567717331004>'
        if json_object['badges']['developer'] == True:
            badges += '<:developer:876856568996560937>'
        if json_object['badges']['donator'] == True:
            badges += '<:donator:876856567859929188>'
        if not json_object['data']['based']['based_count'] < 50:
            json_object['badges']['50_based_count'] = True
            badges += '<:bronze_based:894270671482388530>'
        if not json_object['data']['based']['based_count'] < 100:
            json_object['badges']['100_based_count'] = True
            badges += '<:silver_based:894270672367419423>'
        if not json_object['data']['based']['based_count'] < 200:
            json_object['badges']['200_based_count'] = True
            badges += '<:gold_based:894270672073793618>'
        if not json_object['data']['cringe']['cringe_count'] < 50:
            json_object['badges']['50_cringe_count'] = True
            badges += '<:bronze_cringe:894270672543563816>'
        if not json_object['data']['cringe']['cringe_count'] < 100:
            json_object['badges']['100_cringe_count'] = True
            badges += '<:silver_cringe:894270672321253396>'
        if not json_object['data']['cringe']['cringe_count'] < 200:
            json_object['badges']['200_cringe_count'] = True
            badges += '<:gold_cringe:894270672333844510>'
        

        based_count = json_object['data']['based']['based_count']
        based_title = json_object['data']['based']['based_title']
        last_based_at = json_object['data']['based']['last_based_at']
        cringe_count = json_object['data']['cringe']['cringe_count']
        cringe_title = json_object['data']['cringe']['cringe_title']
        last_cringed_at = json_object['data']['cringe']['last_cringed_at']
        if cringe_count == 0:
            decimal = round(based_count / 1, 2)
        else:
            decimal = round(based_count / cringe_count, 2)
        
        if based_count > cringe_count:
            thumbnail = discord.File('./imgs/based.png', 'thumbnail.png')
            color = 0x42f551
        elif based_count == cringe_count:
            thumbnail = discord.File('./imgs/normie.png', 'thumbnail.png')
            color = 0x8e998f
        elif based_count < cringe_count:
            thumbnail = discord.File('./imgs/cringe.png', 'thumbnail.png')
            color = 0xad1313

        last_based_at = f'<t:{last_based_at}:R>'
        last_cringed_at = f'<t:{last_cringed_at}:R>'

        f = open(f'./data/{ctx.author.id}.json', 'w')
        json.dump(json_object, f, indent=4)
        f.close()

        
        embed = discord.Embed(title=f'Based Count for {ctx.author.name}', description = 'Based and Based-Bot pilled.', color=color)
        embed.add_field(name='Badges', value=badges, inline=False)
        embed.add_field(name='Based Count', value=based_count)
        embed.add_field(name='Based Title', value=based_title)
        embed.add_field(name='Last Based Count', value=f'{last_based_at}')
        embed.add_field(name='Cringe Count', value=cringe_count)
        embed.add_field(name='Cringe Title', value=cringe_title)
        embed.add_field(name='Last Cringed Count', value=f'{last_cringed_at}')
        embed.add_field(name='Based to Cringe Ratio', value=f'``{decimal}``')
        embed.set_thumbnail(url='attachment://thumbnail.png')
        
        channel = getBotChannel(ctx)
        await channel.send(f'<@{ctx.author.id}>!')
        await channel.send(embed = embed, file=thumbnail)

@bot.command()
async def basedcount(ctx, person:discord.Member=''):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not checkFileExists(f'./data/{person.id}.json'):
        return await ctx.send('Nothing to show. What a boring person.')
    elif checkFileExists(f'./data/{person.id}.json'):
        f = open(f'./data/{person.id}.json', 'r')
        json_object = json.load(f)
        f.close()

        if json_object['settings']['public_profile'] == False and not ctx.author.id == 564466359107321856:
            return await ctx.send('This profile is private!')

        badges = ''

        if json_object['badges']['owner'] == True:
            badges += '<:owner:876856567880896602>'
        if json_object['badges']['early_adopter'] == True:
            badges += '<:early_adopter:876856567536947281>'
        if json_object['badges']['alpha_tester'] == True:
            badges += '<:alpha_tester:876856567717331004>'
        if json_object['badges']['developer'] == True:
            badges += '<:developer:876856568996560937>'
        if json_object['badges']['donator'] == True:
            badges += '<:donator:876856567859929188>'
        if not json_object['data']['based']['based_count'] < 50:
            json_object['badges']['50_based_count'] = True
            badges += '<:bronze_based:894270671482388530>'
        if not json_object['data']['based']['based_count'] < 100:
            json_object['badges']['100_based_count'] = True
            badges += '<:silver_based:894270672367419423>'
        if not json_object['data']['based']['based_count'] < 200:
            json_object['badges']['200_based_count'] = True
            badges += '<:gold_based:894270672073793618>'
        if not json_object['data']['cringe']['cringe_count'] < 50:
            json_object['badges']['50_cringe_count'] = True
            badges += '<:bronze_cringe:894270672543563816>'
        if not json_object['data']['cringe']['cringe_count'] < 100:
            json_object['badges']['100_cringe_count'] = True
            badges += '<:silver_cringe:894270672321253396>'
        if not json_object['data']['cringe']['cringe_count'] < 200:
            json_object['badges']['200_cringe_count'] = True
            badges += '<:gold_cringe:894270672333844510>'

        based_count = json_object['data']['based']['based_count']
        based_title = json_object['data']['based']['based_title']
        last_based_at = json_object['data']['based']['last_based_at']
        cringe_count = json_object['data']['cringe']['cringe_count']
        cringe_title = json_object['data']['cringe']['cringe_title']
        last_cringed_at = json_object['data']['cringe']['last_cringed_at']
        if cringe_count == 0:
            decimal = round(based_count / 1, 2)
        else:
            decimal = round(based_count / cringe_count, 2)
        
        if based_count > cringe_count:
            thumbnail = discord.File('./imgs/based.png', 'thumbnail.png')
            color = 0x42f551
        elif based_count == cringe_count:
            thumbnail = discord.File('./imgs/normie.png', 'thumbnail.png')
            color = 0x8e998f
        elif based_count < cringe_count:
            thumbnail = discord.File('./imgs/cringe.png', 'thumbnail.png')
            color = 0xad1313

        last_based_at = f'<t:{last_based_at}:R>'
        last_cringed_at = f'<t:{last_cringed_at}:R>'

        f = open(f'./data/{person.id}.json', 'w')
        json.dump(json_object, f, indent=4)
        f.close()

        
        embed = discord.Embed(title=f'Based Count for {person.name}', description = 'Based and Based-Bot pilled.', color=color)
        embed.add_field(name='Badges', value=badges, inline=False)
        embed.add_field(name='Based Count', value=based_count)
        embed.add_field(name='Based Title', value=based_title)
        embed.add_field(name='Last Based Count', value=f'{last_based_at}')
        embed.add_field(name='Cringe Count', value=cringe_count)
        embed.add_field(name='Cringe Title', value=cringe_title)
        embed.add_field(name='Last Cringed Count', value=f'{last_cringed_at}')
        embed.add_field(name='Based to Cringe Ratio', value=f'``{decimal}``')
        embed.set_thumbnail(url='attachment://thumbnail.png')
        
        channel = getBotChannel(ctx)
        await channel.send(f'<@{ctx.author.id}>!')
        await channel.send(embed = embed, file=thumbnail)
    

@bot.command()
async def ask(ctx, *, question):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    with open(f'./{ctx.message.guild.id}-questionlog.txt', 'a') as f:
        f.write(f'<@{ctx.author.id}> asked: {question}\n')
        f.close()
    
    channel = getBotChannel(ctx)
    await channel.send(f'<@{ctx.author.id}>!')
    await channel.send('Added your question! Your question may be answered the next time my creator opens Q/A time. You will be pinged when your question is asked.')

@bot.command()
async def qa(ctx):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not ctx.author.id == 564466359107321856:
        return
    f = open(f'./{ctx.message.guild.id}-questionlog.txt', 'r')
    lines = f.readlines()

    for line in lines:
        await ctx.send(line)
        await asyncio.sleep(1)

    open(f'./{ctx.message.guild.id}-questionlog.txt', 'w')
    await ctx.send('End of questions.')
    

@bot.command()
async def update(ctx):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not ctx.author.id == 564466359107321856:
        return

    def write_json(new_data, filename):
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data.update(new_data)
            file.seek(0)
            
            json.dump(file_data, file, indent=4)

    path = './data/'
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    file_count = 0

    for file in files:
        f = open(f'./data/{file}', 'r')
        try:
            json_object = json.load(f)
        except BaseException:
            continue

        if not "settings" in json_object:
            file_count += 1
            settings = {
                "settings": {
                    "public_profile": True,
                    "show_badges": True
                }
            }
            write_json(settings, f'./data/{file}')

        elif not "badges" in json_object:
            file_count += 1
            badges = {
                "badges": {
                    "alpha_tester": False,
                    "early_adopter": True,
                    "developer": False,
                    "owner": False,
                    "donator": False
                }
            }
            write_json(badges, f'./data/{file}')
        
        elif not "server_id" in json_object:
            file_count += 1
            server_id = {
                "server_id": ctx.message.guild.id
            }
            write_json(server_id, f'./data/{file}')

        elif not "discord_name" in json_object:
            file_count += 1
            user = await bot.fetch_user(json_object['discord_id'])
            discord_name = {
                "discord_name": user.name
            }
            write_json(discord_name, f'./data/{file}')
        
        elif not "avatar_url" in json_object:
            file_count += 1
            user = await bot.fetch_user(json_object['discord_id'])
            discord_avatar = {
                "avatar_url": user.avatar
            }
            write_json(discord_avatar, f'./data/{file}')

    await ctx.send(f'Updated {file_count} files with new data.')

    
@bot.command()
async def settings(ctx, arg='', value=''):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not checkFileExists(f'./data/{ctx.author.id}.json'):
        return await ctx.send('Nothing to show. What a boring person.')
    elif checkFileExists(f'./data/{ctx.author.id}.json'):
        channel = getBotChannel(ctx)
        f = open(f'./data/{ctx.author.id}.json', 'r')
        json_object = json.load(f)
        f.close()
        
        falses = ['false', 'no', 'private', 'priv']
        trues = ['true', 'yes', 'public', 'pub']

        if not arg:
            embed = discord.Embed(title=f'Settings for {ctx.author.name}', description='To change a setting use ``./settings SETTING NEWVALUE``.', color=0x00ccff)
            embed.add_field(name='Public Profile', value=json_object['settings']['public_profile'])
            embed.add_field(name='Show Badges on Profile', value=json_object['settings']['show_badges'])
            embed.set_footer(text='Accepted SETTINGS are {public}, {badges}.')

            await channel.send(f'<@{ctx.author.id}>!')
            await channel.send(embed=embed)
        
        elif arg == 'public':
            if value.lower() in falses:
                json_object['settings']['public_profile'] = False
            elif value.lower() in trues:
                json_object['settings']['public_profile'] = True
            else:
                await channel.send(f'<@{ctx.author.id}>!')
                return await channel.send(f'Thats not an accepted NEWVALUE. Accepted NEWVALUES are: ``{trues}`` and ``{falses}``.')
            f = open(f'./data/{ctx.author.id}.json', 'w')
            json.dump(json_object, f, indent=4)
            f.close()
            
            await channel.send(f'<@{ctx.author.id}>!')
            return await channel.send(f'Successfully set ``{arg}`` to ``{value}``.')
        
        elif arg == 'badges':
            if value.lower() in falses:
                json_object['settings']['show_badges'] = False
            elif value.lower() in trues:
                json_object['settings']['show_badges'] = True
            else:
                await channel.send(f'<@{ctx.author.id}>!')
                return await channel.send(f'Thats not an accepted NEWVALUE. Accepted NEWVALUES are: ``{trues}`` and ``{falses}``.')
            f = open(f'./data/{ctx.author.id}.json', 'w')
            json.dump(json_object, f, indent=4)
            f.close()

            await channel.send(f'<@{ctx.author.id}>!')
            return await channel.send(f'Successfully set ``{arg}`` to ``{value}``.')
        
        else:
            await channel.send(f'<@{ctx.author.id}>!')
            return await channel.send('Thats not an accepted SETTING. Accepted SETTINGS are: ``public`` and ``badges``.')


@bot.command()
async def fed(ctx, person:discord.Member=None):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if person is None:
        person = ctx.author

    soyjak = Image.open("./imgs/fbi.png")

    asset = person.avatar_url_as(size=128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((300, 300))

    soyjak.paste(pfp, (550, 100))

    soyjak.save("fbi-edited.png")
    
    channel = getBotChannel(ctx)
    await channel.send(f'<@{ctx.author.id}>, <@{person.id}>!')
    await channel.send(file=discord.File("fbi-edited.png"))
    
@bot.command()
async def test(ctx):
    print(blacklist_check(ctx.author.id, ctx.guild.id))

@bot.command()
async def startLeaderboard(ctx):
    if not ctx.author.id == 564466359107321856:
        return
    
    onlyfiles = [f for f in os.listdir('./data/') if os.path.isfile(os.path.join('./data/', f))]

    for file in onlyfiles:
        print(file)
        if file == 'basedleaderboard.json' or file == 'cringeleaderboard.json':
            continue
        f = open(f'./data/{file}', 'r')
        try:
            json_object = json.load(f)
        except BaseException:
            continue
        f.close()

        try:
            discord_id = json_object['discord_id']
            discord_name = json_object['discord_name']
            based_count = json_object['data']['based']['based_count']
        except:
            continue

        if based_count < 5:
            continue

        data = {
            "discord_id": discord_id,
            "discord_id_string": str(discord_id),
            "discord_name": discord_name,
            "based_count": based_count,
            "ranking": 0
        }

        f = open('./data/basedleaderboard.json', 'r')
        nested_json = json.load(f)
        f.close()

        f = open('./data/basedleaderboard.json', 'w')
        nested_json['data'] += [data]
        json.dump(nested_json, f, indent=4)
        f.close()
    
    f = open('./data/basedleaderboard.json', 'w')
    nested_json['data'] = sorted(nested_json['data'], key=lambda r: r['based_count'], reverse=True)
    json.dump(nested_json, f, indent=4)
    f.close()

    for count, value in enumerate(nested_json['data']):
        value['ranking'] = count
    
    f = open('./data/basedleaderboard.json', 'w')
    json.dump(nested_json, f, indent=4)
    f.close()

@bot.command()
async def basedleaderboard(ctx):
    embed = discord.Embed(description='See the leaderboard [here!](https://slatedev.xyz/basedbot/basedleaderboard)')
    await ctx.send(embed=embed)

@bot.command()
async def cringeleaderboard(ctx):
    embed = discord.Embed(description='See the leaderboard [here!](https://slatedev.xyz/basedbot/cringeleaderboard)')
    await ctx.send(embed=embed)



bot.run(DISCORD_TOKEN)
