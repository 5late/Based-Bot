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

load_dotenv()

intents = discord.Intents().all()

DISCORD_TOKEN = os.getenv('discord_token')
BASED = ['Based', 'based', 'Baste', 'baste']
CRINGE = ['Cringe', 'cringe', 'soy', 'Soy']

bot = commands.Bot(
    command_prefix='./',
    description='A VALORANT bot that breaks down stats.',
    intents=intents)

def readFile(fileName):
    fileObj = open(fileName, "r")  # opens the file in read mode
    words = fileObj.read()  # .splitlines() #puts the file into an array
    fileObj.close()
    return words

def blacklist_check(ctx):
    blisted_users = readFile('./blacklisted/sortedblacklistedusers.txt')
    print(blisted_users)
    blisted_guilds = readFile('./blacklisted/sortedblacklistedguilds.txt')
    return str(
        ctx.author.id) not in blisted_users and str(
        ctx.guild.id) not in blisted_guilds

def checkFileExists(file):
    return os.path.isfile(file)

def getTicks():
    #d = datetime.utcnow()
    #t0 = datetime(1, 1, 1)
    #return (d - t0).total_seconds()
    return int(time.time())

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
                        "created_at": getTicks(),
                        "data": {
                            "based_count": 1,
                            "based_title": "newb",
                            "last_based_at": getTicks(),
                            "cringe_count": 0,
                            "cringe_title": "newb",
                            "last_cringed_at": getTicks()
                        }
                    }
                    json.dump(data, f, indent=4)
            
            elif checkFileExists(f'./data/{member.id}.json'):
                f = open(f'./data/{member.id}.json', 'r')
                json_object = json.load(f)
                f.close()

                json_object['data']['based_count'] += 1
                json_object['data']['last_based_at'] = getTicks()

                f = open(f'./data/{member.id}.json', 'w')
                json.dump(json_object, f, indent=4)
                f.close()

            print(member.id)

    elif message.content.split()[0].lower() == 'cringe' and message.mentions:
        # cringe stuff goes here

        for member in message.mentions:
            if not checkFileExists(f'./data/{member.id}.json'):
                with open(f'./data/{member.id}.json', 'w') as f:
                    data = {
                        "discord_id": member.id,
                        "created_at": getTicks(),
                        "data": {
                            "based_count": 0,
                            "based_title": "newb",
                            "last_based_at": getTicks(),
                            "cringe_count": 1,
                            "cringe_title": "newb",
                            "last_cringed_at": getTicks()
                        }
                    }
                    json.dump(data, f, indent=4)
            
            elif checkFileExists(f'./data/{member.id}.json'):
                f = open(f'./data/{member.id}.json', 'r')
                json_object = json.load(f)
                f.close()

                json_object['data']['cringe_count'] += 1
                json_object['data']['last_cringed_at'] = getTicks()

                f = open(f'./data/{member.id}.json', 'w')
                json.dump(json_object, f, indent=4)
                f.close()

            print(member.id)

        print(message.mentions[0].id)
    await bot.process_commands(message)



@bot.command()
async def whoami(ctx):
    embed = discord.Embed(title = 'Based Bot', description = '**The most based bot on Discord.**', color = 0xFFCC)
    embed.add_field(name='Command Help', value= 'For command help, run command ``./commands``')
    embed.add_field(name='Creator', value='My creator is ``Xurxx#7879``')
    await ctx.send(embed=embed)


@bot.command()
async def blacklist(ctx, type, arg):
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
    if not checkFileExists:
        return await ctx.send('Nothing to show. What a boring person.')
    elif checkFileExists:
        f = open(f'./data/{ctx.author.id}.json', 'r')
        json_object = json.load(f)
        f.close()

        based_count = json_object['data']['based_count']
        based_title = json_object['data']['based_title']
        last_based_at = json_object['data']['last_based_at']
        cringe_count = json_object['data']['cringe_count']
        cringe_title = json_object['data']['cringe_title']
        last_cringed_at = json_object['data']['last_cringed_at']
        
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
        embed.add_field(name='Based Count', value=based_count)
        embed.add_field(name='Based Title', value=based_title)
        embed.add_field(name='Last Based Count', value=f'{last_based_at} **UTC**')
        embed.add_field(name='Cringe Count', value=cringe_count)
        embed.add_field(name='Cringe Title', value=cringe_title)
        embed.add_field(name='Last Cringed Count', value=f'{last_cringed_at} **UTC**')
        embed.set_thumbnail(url='attachment://thumbnail.png')

        await ctx.send(embed = embed, file=thumbnail)

bot.run(DISCORD_TOKEN)