from re import T
import discord
from datetime import datetime, timezone
from discord.ext.commands.core import check
from discord.file import File
from dotenv import load_dotenv
import os
import requests
import json
import asyncio
from discord.ext import commands
import time
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

load_dotenv()

intents = discord.Intents().all()

DISCORD_TOKEN = os.getenv('discord_token')
BASED = ['based', 'baste']
CRINGE = ['cringe', 'soy']

bot = commands.Bot(
    command_prefix='.//',
    description='Based Bot, the most based bot on Discord.',
    intents=intents)

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

def getBotChannel(server_id):
    f = open(f'./data/server_data/{server_id}.json', 'r')
    json_object = json.load(f)
    f.close()
    return bot.get_channel(json_object['bot_channel'])
    
def checkFileExists(file):
    return os.path.isfile(file)

def getTicks():
    return int(time.time())

def generateBasedTitle(count):
    if (count // 10) == 1:
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
        return "Too Based"
    elif (count // 10) <= 20:
        return "ERROR- Too Based"

@bot.event
async def on_ready():
    global botUptime
    botUptime = datetime.utcnow()
    print(f'Logged in as:\n{bot.user.name}#{bot.user.discriminator} at {botUptime}.\n----------')


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if message.content.split()[0].lower() == 'based' and message.mentions:
        # Based stuff goes here
        
        for member in message.mentions:
            if not checkFileExists(f'./data/{member.id}.json'):
                with open(f'./data/{member.id}.json', 'w') as f:
                    data = {
                        "discord_id": member.id,
                        "server_id": message.guild.id,
                        "created_at": getTicks(),
                            "data": {
                                "based": {
                                    "based_count": 1,
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
                                "early_adopter": True,
                                "developer": False,
                                "owner": False,
                                "donator": False
                            }
                    }
                    json.dump(data, f, indent=4)
            
            elif checkFileExists(f'./data/{member.id}.json'):
                if member.id == message.author.id:
                    return
                f = open(f'./data/{member.id}.json', 'r')
                json_object = json.load(f)
                f.close()

                if json_object['data']['based']['last_based_at'] + 3 >= getTicks():
                    print(json_object['data']['based']['last_based_at'] + 3, getTicks())
                    return
                elif json_object['data']['based']['last_based_at'] + 100 >= getTicks() and json_object['data']['based']['last_based_by'] == message.author.id:
                    return
                json_object['data']['based']['based_count'] += 1
                json_object['data']['based']['based_title'] = generateBasedTitle(json_object['data']['based']['based_count'])
                json_object['data']['based']['last_based_at'] = getTicks()
                json_object['data']['based']['last_based_by'] = message.author.id

                f = open(f'./data/{member.id}.json', 'w')
                json.dump(json_object, f, indent=4)
                f.close()

            print(member.id)
        
        await message.add_reaction('👍')

    elif message.content.split()[0].lower() == 'cringe' and message.mentions:
        # cringe stuff goes here

        for member in message.mentions:
            if not checkFileExists(f'./data/{member.id}.json'):
                with open(f'./data/{member.id}.json', 'w') as f:
                    data = {
                        "discord_id": member.id,
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
                                    "cringe_count": 1,
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
                                "early_adopter": True,
                                "developer": False,
                                "owner": False,
                                "donator": False
                            }
                    }
                    json.dump(data, f, indent=4)
            
            elif checkFileExists(f'./data/{member.id}.json'):
                if member.id == message.author.id:
                    return
                f = open(f'./data/{member.id}.json', 'r')
                json_object = json.load(f)
                f.close()

                if json_object['data']['cringe']['last_cringed_at'] + 3 >= getTicks():
                    print(json_object['data']['cringe']['last_cringed_at'] + 3, getTicks())
                    return
                elif json_object['data']['cringe']['last_cringed_at'] + 120 >= getTicks() and json_object['data']['cringe']['last_cringed_by'] == message.author.id:
                    return
                json_object['data']['cringe']['cringe_count'] += 1
                json_object['data']['cringe']['last_cringed_at'] = getTicks()
                json_object['data']['cringe']['last_cringed_by'] = message.author.id

                f = open(f'./data/{member.id}.json', 'w')
                json.dump(json_object, f, indent=4)
                f.close()

            print(member.id)
        
        await message.add_reaction('👍')

    await bot.process_commands(message)



@bot.command()
async def whoami(ctx):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    embed = discord.Embed(title = 'Based Bot', description = '**The most based bot on Discord.**', color = 0xFFCC)
    embed.add_field(name='Command Help', value= 'For command help, [Click Here](https://5late.github.io/guides/HIDDEN-BASED-BOT.html#commands)')
    embed.add_field(name='Creator', value='My creator is ``Xurxx#7879``')

    channel = getBotChannel(ctx.guild.id)
    await channel.send(f'<@{ctx.author.id}>!')
    await channel.send(embed=embed)


@bot.command()
async def reset(ctx, boc, person):
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
            json_object['data'][boc][f'based_count'] = 0
            json_object['data'][boc][f'based_title'] = 'newb'
        elif boc.lower() == 'cringe':
            json_object['data'][boc][f'cringe_count'] = 0
            json_object['data'][boc][f'cringe_title'] = 'newb'

        f = open(f'./data/{person}.json', 'w')
        json.dump(json_object, f, indent=4)
        f.close()
        return await ctx.send(f'Reset <@{person}> {boc} score to 0.')
        

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
        based_count = json_object['data']['based']['based_count']
        based_title = json_object['data']['based']['based_title']
        last_based_at = json_object['data']['based']['last_based_at']
        cringe_count = json_object['data']['cringe']['cringe_count']
        cringe_title = json_object['data']['cringe']['cringe_title']
        last_cringed_at = json_object['data']['cringe']['last_cringed_at']
        
        if based_count > cringe_count:
            thumbnail = discord.File('./imgs/based.png', 'thumbnail.png')
            color = 0x42f551
        elif based_count == cringe_count:
            thumbnail = discord.File('./imgs/normie.png', 'thumbnail.png')
            color = 0x8e998f
        elif based_count < cringe_count:
            thumbnail = discord.File('./imgs/cringe.png', 'thumbnail.png')
            color = 0xad1313

        last_based_at = datetime.utcfromtimestamp(last_based_at).strftime("%a %b %d %Y | %H:%M")
        last_cringed_at = datetime.utcfromtimestamp(last_cringed_at).strftime("%a %b %d %Y | %H:%M")

        
        embed = discord.Embed(title=f'Based Count for {ctx.author.name}', description = 'Based and Based-Bot pilled.', color=color)
        embed.add_field(name='Badges', value=badges, inline=False)
        embed.add_field(name='Based Count', value=based_count)
        embed.add_field(name='Based Title', value=based_title)
        embed.add_field(name='Last Based Count', value=f'{last_based_at} **UTC**')
        embed.add_field(name='Cringe Count', value=cringe_count)
        embed.add_field(name='Cringe Title', value=cringe_title)
        embed.add_field(name='Last Cringed Count', value=f'{last_cringed_at} **UTC**')
        embed.set_thumbnail(url='attachment://thumbnail.png')
        
        channel = getBotChannel(ctx.guild.id)
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
        based_count = json_object['data']['based']['based_count']
        based_title = json_object['data']['based']['based_title']
        last_based_at = json_object['data']['based']['last_based_at']
        cringe_count = json_object['data']['cringe']['cringe_count']
        cringe_title = json_object['data']['cringe']['cringe_title']
        last_cringed_at = json_object['data']['cringe']['last_cringed_at']
        
        if based_count > cringe_count:
            thumbnail = discord.File('./imgs/based.png', 'thumbnail.png')
            color = 0x42f551
        elif based_count == cringe_count:
            thumbnail = discord.File('./imgs/normie.png', 'thumbnail.png')
            color = 0x8e998f
        elif based_count < cringe_count:
            thumbnail = discord.File('./imgs/cringe.png', 'thumbnail.png')
            color = 0xad1313

        last_based_at = datetime.utcfromtimestamp(last_based_at).strftime("%a %b %d %Y | %H:%M")
        last_cringed_at = datetime.utcfromtimestamp(last_cringed_at).strftime("%a %b %d %Y | %H:%M")

        
        embed = discord.Embed(title=f'Based Count for {person.name}', description = 'Based and Based-Bot pilled.', color=color)
        embed.add_field(name='Badges', value=badges, inline=False)
        embed.add_field(name='Based Count', value=based_count)
        embed.add_field(name='Based Title', value=based_title)
        embed.add_field(name='Last Based Count', value=f'{last_based_at} **UTC**')
        embed.add_field(name='Cringe Count', value=cringe_count)
        embed.add_field(name='Cringe Title', value=cringe_title)
        embed.add_field(name='Last Cringed Count', value=f'{last_cringed_at} **UTC**')
        embed.set_thumbnail(url='attachment://thumbnail.png')
        
        channel = getBotChannel(ctx.guild.id)
        await channel.send(f'<@{ctx.author.id}>!')
        await channel.send(embed = embed, file=thumbnail)
    

@bot.command()
async def ask(ctx, *, question):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    with open(f'./{ctx.message.guild.id}-questionlog.txt', 'a') as f:
        f.write(f'<@{ctx.author.id}> asked: {question}\n')
        f.close()
    
    channel = getBotChannel(ctx.guild.id)
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
        json_object = json.load(f)

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

    await ctx.send(f'Updated {file_count} files with new data.')

    
@bot.command()
async def settings(ctx, arg='', value=''):
    if blacklist_check(ctx.author.id, ctx.guild.id):
        return
    if not checkFileExists(f'./data/{ctx.author.id}.json'):
        return await ctx.send('Nothing to show. What a boring person.')
    elif checkFileExists(f'./data/{ctx.author.id}.json'):
        channel = getBotChannel(ctx.guild.id)
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
    
    channel = getBotChannel(ctx.guild.id)
    await channel.send(f'<@{ctx.author.id}>!')
    await channel.send(file=discord.File("fbi-edited.png"))
    
@bot.command()
async def test(ctx):
    print(blacklist_check(ctx.author.id, ctx.guild.id))

bot.run(DISCORD_TOKEN)