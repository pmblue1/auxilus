import os
import datetime
import discord
from discord.ext import tasks
import random
import asyncio
import re
import sys
import json
import requests
import encrypt
import vaal
import strCheck
import sqliteObj
import traceback
from base64 import b64decode, b64encode
import eve

print("-----------------------\n\nStarting bot, loading keys...\n\n-----------------------")

keysF = open('keys.json')
keys = json.load(keysF)
TOKEN = keys["botToken"]
hourOffset=0

def strJsonTo(a):
    b = str(json.dumps(a))
    c = b.replace("<r_brac>","</r_brac>").replace("<l_brac>","</l_brac>").replace('<d_quote>',"</d_quote>").replace("<s_quote>","</s_quote>").replace("{","<r_brac>").replace("}","<l_brac>").replace('"',"<d_quote>").replace("'","<s_quote>")
    return c
def strJsonFrom(a):
    b = str(a)
    c = b.replace("<r_brac>","{").replace("<l_brac>","}").replace("<d_quote>",'"').replace("<s_quote>","'").replace("</r_brac>","<r_brac>").replace("</l_brac>","<l_brac>").replace('</d_quote>',"<d_quote>").replace("</s_quote>","<s_quote>")
    d = json.loads(c)
    return d
def numbFormat(number):
    try:
        return str("{:,}".format(number))
    except:
        return "numbFormat [01]: Unknown Error"

db = sqliteObj.sqliteObj("data.sqlite3","queue")

presDict = strJsonFrom(db.select({"name": "presence"},table="data")[0]["data"])
presDict["value"] = presDict["value"].replace("{servers}",f'0').replace("{users}",f'0')
if presDict["type"] == "playing":
    activity = discord.Game(presDict["value"])
elif presDict["type"] == "streaming":
    activity = discord.Streaming(name=presDict["value"]["title"],url=presDict["value"]["url"])
elif presDict["type"] == "listening":
    activity = discord.Activity(type=discord.ActivityType.listening, name=presDict["value"])
elif presDict["type"] == "watching":
    activity = discord.Activity(type=discord.ActivityType.watching, name=presDict["value"])
else:
    activity = None
    
client = discord.Client(activity=activity)

class BotPostKey:
    def __init__(self):
        keysF = open('keys.json')
        keys = json.load(keysF)
        self.key = keys["postKey"]
    def update(self):
        keysF = open('keys.json')
        keys = json.load(keysF)
        self.key = keys["postKey"]
        return self
botPostKey = BotPostKey()
def epoch():
    return int(round(datetime.datetime.now().timestamp(),0))
def epochMS():
    now = datetime.datetime.now()
    ms = round(now.microsecond/1000,1)
    return int(round(now.timestamp()*1000,0)) + ms
def msgAuthor(embed,user):
    embed.set_author(name=str(user),icon_url=user.avatar_url_as(format="png"))
    return embed
class StaffCheck:
    def __init__(self):
        staffF = open('staff.json')
        staffDict = json.load(staffF)
        self.dict = staffDict
        self.list = staffDict["staff"]
        self.updated = epoch()

    def refreshCheck(self):
        if self.updated + 15 <= epoch():
            staffF = open('staff.json')
            staffDict = json.load(staffF)
            self.dict = staffDict
            self.list = staffDict["staff"]
            self.updated = epoch()
        return self

staffCheckObj = StaffCheck()
def staffCheck(userId,staffCheckObj=staffCheckObj):
    staffList = staffCheckObj.refreshCheck().list
    if userId in staffList:
        return True
    return False
    
def userToMember(user,guild):
    try:
        memb = guild.get_member(user.id)
    except:
        memb = guild.get_member(int(user))
    return memb
def checkPresets(tier,filtered):
    tier = int(tier)
    if tier == 0:
        return strCheck.Settings(filtered)
    elif tier == 1:
        return strCheck.Settings(filtered).advanced()
    elif tier == 2:
        return strCheck.Settings(filtered).advanced(percent=.2,noSpace=True)
    elif tier == 3:
        return strCheck.Settings(filtered).advanced(percent=.3,noSpace=True,char=2,charMin=True)
    else:
        return None

def strBool(a):
    if a == "true":
        return True
    elif a == "false":
        return False
    else:
        return None


def linkCheck(string,returnBool=False):
    string = string
    def inS(check, string=string):
        string = string.lower()
        if check.lower() in string.lower():
            return True
        else:
            return False
    def inSL(period=False, string=string):
        string = string.lower()
        found = False
        dList = ['com', 'org', 'net', 'gov', 'edu']
        for x in dList:
            dom = x.lower()
            if period:
                dom = f'.{dom}'
            if dom in string.lower():
                found = True
                break
        return found
    if inS('https://') or inS('http://'):
        return True
    nStr = ''
    nList = []
    sList = []
    nList2 = []
    stringS = string+' '
    for x in stringS:
        if x != ' ':
            nStr = f'{nStr}{x}'
        else:
            if True:
                nList.append(nStr)
                sList.append(nStr)
                nStr = ''
    sListC = 0
    for x in sList:
        sListC += 1
    if sListC <= 3:
        str2 = ''
        for x in sList:
            str2 = f'{str2}{x}'
        nList2.append(str2)
    else:
        while sListC > 3:
            sListC = 0
            for x in sList:
                sListC += 1
            count = 0
            str2 = ''
            for x in sList:
                count += 1
                if count == 1:
                    dStr = x
                elif count >= 4:
                    nList2.append(x)
                    break
                else:
                    str2 = f'{str2}{x}'
            sList.remove(dStr)
        str2 = ''
        for x in sList:
            str2 = f'{str2}{x}'
        nList2.append(str2)
    for x in nList:
        char = len(x)
        if ((inS('http',string=x) or inS('https',string=x)) and char>12) or ((inSL(period=True,string=x) and char>12) or (inSL(string=x) and inS('www',string=x) and char>12)):
            if returnBool:
                return x
            return True
        if inSL(period=True,string=x) and char>=10 and (x[-1]=='/' or inSL(period=True,string=(x[-4:-1]+x[-1]))):
            if returnBool:
                return x
            return True
    for x in nList2:
        char = len(x)
        if ((inS('http',string=x) or inS('https',string=x) and (inS('www',string=x) or inSL(string=x))) and char>15) or ((inSL(period=True,string=x) and char>12) or (inSL(string=x) and inS('www',string=x) and char>12)):
            return True
    return False


def epochConv(mode=None,info=None, hourOffset=hourOffset):
    try:
        if info != None:
            info = int(info)
        if mode == None:
            print(f'epochConv (ERROR[01]): No mode provided')
            return 'epochConv ERROR[01]'
        elif mode == 'currEpoch':
            return int(round(datetime.datetime.now().timestamp(),0))
        elif mode == 'dur':
            if info == None:
                print(f'epochConv (ERROR[02]): No information provided! (info= {info})')
                return 'epochConv ERROR[02]'
            strInfo = str(info)
            if charCountFunction(strInfo) > 10:
                info = int(round(info/1000,0))
            newCreated = int(round(info,0))
            nDay = int(round(newCreated,0))
            time = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(seconds=nDay)
            timeT = datetime.datetime.utcnow() - time
            sec = timeT.total_seconds()
            tMin = 0
            tHour = 0
            tDay = 0
            tYear = 0
            while sec > 59:
                sec -= 60
                tMin += 1
            while tMin > 59:
                tMin -= 60
                tHour += 1
            while tHour > 23:
                tHour -= 24
                tDay += 1
            totDay = tDay
            while tDay > 364:
                tDay -= 365
                tYear += 1
            jsinceDur = ''
            if tYear != 0:
                if tYear == 1:
                    jsinceDur = f'{tYear} Year ({totDay} days)'
                else:
                    jsinceDur = f'{tYear} Years ({totDay} days)'
            elif tDay != 0:
                jsinceDur = f'{totDay} days'
            else:
                jsinceDur = f'{tHour}:{twoDigFormat(tMin)}:{twoDigFormat(int(round(sec,0)))}'
            jsinceDate = f'{time.day}/{time.month}/{time.year} {twoDigFormat(time.hour)}:{twoDigFormat(time.minute)}'
            return jsinceDur
        elif mode == 'durUntil':
            if info == None:
                print(f'epochConv (ERROR[03]): No information provided! (info= {info})')
                return 'epochConv ERROR[03]'
            newCreated = int(round(info,0))
            nDay = int(round(newCreated,0))
            time = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(seconds=nDay)
            timeT = time - datetime.datetime.utcnow()
            sec = timeT.total_seconds()
            tMin = 0
            tHour = 0
            tDay = 0
            tYear = 0
            while sec > 59:
                sec -= 60
                tMin += 1
            while tMin > 59:
                tMin -= 60
                tHour += 1
            while tHour > 23:
                tHour -= 24
                tDay += 1
            totDay = tDay
            while tDay > 364:
                tDay -= 365
                tYear += 1
            jsinceDur = ''
            if tYear != 0:
                if tYear == 1:
                    jsinceDur = f'{tYear} Year ({totDay} days)'
                else:
                    jsinceDur = f'{tYear} Years ({totDay} days)'
            elif tDay != 0:
                jsinceDur = f'{totDay} days'
            else:
                jsinceDur = f'{twoDigFormat(tHour)}:{twoDigFormat(tMin)}:{twoDigFormat(int(round(sec,0)))}'
            jsinceDate = f'{time.day}/{time.month}/{time.year} {twoDigFormat(time.hour)}:{twoDigFormat(time.minute)}'
            return jsinceDur
        elif mode == 'dateTime':
            if info == None or info == '':
                print(f'epochConv (ERROR[04]): No information provided! (info= {info})')
                return 'epochConv ERROR[04]'
            newCreated = int(round(info,0))
            nDay = int(round(newCreated,0))
            time = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(seconds=nDay) - datetime.timedelta(hours=hourOffset)
            timeT = datetime.datetime.utcnow() - time
            sec = timeT.total_seconds()
            tMin = 0
            tHour = 0
            tDay = 0
            tYear = 0
            while sec > 59:
                sec -= 60
                tMin += 1
            while tMin > 59:
                tMin -= 60
                tHour += 1
            while tHour > 23:
                tHour -= 24
                tDay += 1
            totDay = tDay
            while tDay > 364:
                tDay -= 365
                tYear += 1
            jsinceDur = ''
            if tYear != 0:
                if tYear == 1:
                    jsinceDur = f'{tYear} Year ({totDay} days)'
                else:
                    jsinceDur = f'{tYear} Years ({totDay} days)'
            elif tDay != 0:
                jsinceDur = f'{totDay} days'
            else:
                jsinceDur = f'{tHour}:{tMin}:{int(round(sec,0))}'
            jsinceDate = f'{time.day}/{time.month}/{time.year} {twoDigFormat(time.hour)}:{twoDigFormat(time.minute)}'
            return jsinceDate
        elif mode == 'date':
            if info == None or info == '':
                print(f'epochConv (ERROR[05]): No information provided! (info= {info})')
                return 'epochConv ERROR[05]'
            newCreated = int(round(info,0))
            nDay = int(round(newCreated,0))
            time = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(seconds=nDay) - datetime.timedelta(hours=hourOffset)
            timeT = datetime.datetime.utcnow() - time
            sec = timeT.total_seconds()
            tMin = 0
            tHour = 0
            tDay = 0
            tYear = 0
            while sec > 59:
                sec -= 60
                tMin += 1
            while tMin > 59:
                tMin -= 60
                tHour += 1
            while tHour > 23:
                tHour -= 24
                tDay += 1
            totDay = tDay
            while tDay > 364:
                tDay -= 365
                tYear += 1
            jsinceDur = ''
            if tYear != 0:
                if tYear == 1:
                    jsinceDur = f'{tYear} Year ({totDay} days)'
                else:
                    jsinceDur = f'{tYear} Years ({totDay} days)'
            elif tDay != 0:
                jsinceDur = f'{totDay} days'
            else:
                jsinceDur = f'{tHour}:{tMin}:{int(round(sec,0))}'
            jsinceDate = f'{time.day}/{time.month}/{time.year}'
            return jsinceDate
        else:
            print(f'epochConv (ERROR[06]): Invalid mode provided!')
            return 'epochConv ERROR[06]'
    except:
        print(f'epochConv (ERROR[07]): Unknown Error\n{traceback.format_exc()}')
        return 'epochConv ERROR[07]'

def searchDiscord(value,guild):
    notFound = True
    found = None
    if '<@' in value:
        try:
            aSel = re.search("<@(.*)>", value.replace("!",""))
            nChoice = str(aSel.group(1))
            found = int(nChoice)
            found = guild.get_member(found)
            notFound = False
        except:
            notFound = True
    memberList = guild.members
    if notFound:
        for x in memberList:
            if value == x.display_name:
                found = x
                notFound = False
                break
            elif value == x.name:
                found = x
                notFound = False
                break
    if notFound:
        for x in memberList:
            if value.lower() == x.display_name.lower():
                found = x
                notFound = False
                break
            elif value.lower() == x.name.lower():
                found = x
                notFound = False
                break
    if notFound:
        charCount = 0
        for j in value:
            charCount += 1
        if charCount < 6:
            return found
        for x in memberList:
            if value.lower() in x.display_name.lower():
                found = x
                notFound = False
                break
            elif value.lower() in x.name.lower():
                found = x
                notFound = False
                break
    return found
def twoDigFormat(number):
    number = str(number)
    charCount = 0
    for x in number:
        charCount += 1
    if charCount == 1:
        number = f'0{number}'
    return number

class GuildSettings:
    def __init__(self,gId,prefix=None,log=None,disNameStatus=None,disNameTrackUsername=None,disNameImpStatus=None,disNameImpRoles=None,disNameWordStatus=None,disNameWordWords=None,disNameActNameBack=None,disNameActDM=None,disNameActChannelMsg=None,disNameWordSens=None):
        self.gId = int(gId)
        if prefix != None:
            self.prefix = prefix
            self.log = int(log)
            self.disNameStatus = strBool(disNameStatus)
            self.disNameTrackUsername = strBool(disNameTrackUsername)
            self.disNameImpStatus = strBool(disNameImpStatus)
            self.disNameImpRoles = [disNameImpRoles]
            self.disNameWordStatus = strBool(disNameWordStatus)
            self.disNameWordWords = disNameWordWords.split(",")
            self.disNameActNameBack = strBool(disNameActNameBack)
            self.disNameActDM = strBool(disNameActDM)
            self.disNameActChannelMsg = disNameActChannelMsg
            self.disNameWordSens = int(disNameWordSens)
        else:
            self.prefix = '!'
            self.log = 0
            self.disNameStatus = False
            self.disNameTrackUsername = None
            self.disNameImpStatus = None
            self.disNameImpRoles = None
            self.disNameWordStatus = None
            self.disNameWordWords = None
            self.disNameActNameBack = None
            self.disNameActDM = None
            self.disNameActChannelMsg = None
            self.disNameWordSens = None

    def update(self):
        r = requests.post("https://auxilus.ml/bot_request/guild_update",headers={"Auth": botPostKey.key,"guildId": str(self.gId)})
        givenDict = r.json()
        self.prefix = givenDict["prefix"]
        self.log = int(givenDict["log"])
        self.disNameStatus = strBool(givenDict["disNameStatus"])
        self.disNameTrackUsername = strBool(givenDict["disNameTrackUsername"])
        self.disNameImpStatus = strBool(givenDict["disNameImpStatus"])
        self.disNameImpRoles = [givenDict["disNameImpRoles"]]
        self.disNameWordStatus = strBool(givenDict["disNameWordStatus"])
        self.disNameWordWords = givenDict["disNameWordWords"].split(",")
        self.disNameActNameBack = strBool(givenDict["disNameActNameBack"])
        self.disNameActDM = strBool(givenDict["disNameActDM"])
        self.disNameActChannelMsg = givenDict["disNameActChannelMsg"]
        self.disNameWordSens = int(givenDict["disNameWordSens"])
        return

def guildInit():
    r = requests.post("https://auxilus.ml/bot_request/init",headers={"Auth": botPostKey.key})
    guildsDict = {}
    givenDict = r.json()
    for x in givenDict:
        guildsDict[x] = GuildSettings(x,givenDict[x]["prefix"],givenDict[x]["log"],givenDict[x]["disNameStatus"],givenDict[x]["disNameTrackUsername"],givenDict[x]["disNameImpStatus"],givenDict[x]["disNameImpRoles"],givenDict[x]["disNameWordStatus"],givenDict[x]["disNameWordWords"],givenDict[x]["disNameActNameBack"],givenDict[x]["disNameActDM"],givenDict[x]["disNameActChannelMsg"],givenDict[x]["disNameWordSens"])
    return guildsDict



def clientPost(staffCheckObj=staffCheckObj):
    iGuilds = []
    iUsers = []
    for x in client.guilds:
        memberIds = []
        for y in x.members:
            memberIds.append(y.id)
        channels = []
        for z in x.text_channels:
            channels.append({"name": z.name, "id": z.id})
        gRoles = []
        for a in x.roles:
            gRoles.append({"name": a.name, "id": a.id, "color": str(a.color), "position": a.position})
        iGuilds.append({"name": x.name, "id": x.id, "icon": str(x.icon_url_as(format="png")), "members": memberIds, "channels": channels, "roles": gRoles})
    for x in client.users:
        iUsers.append({"name": x.name, "id": x.id, "icon": str(x.avatar_url_as(format="png"))})
    presDict = strJsonFrom(db.select({"name": "presence"},table="data")[0]["data"])
    cUser = client.user
    clientDict = {"name": cUser.name, "id": cUser.id, "icon": str(cUser.avatar_url_as(format="png")),"presence": presDict}
    staffList = staffCheckObj.refreshCheck().list
    info = {"guilds": iGuilds,"users": iUsers,"staff": staffList,"client": clientDict}
    r = requests.post("https://auxilus.ml/client_post",headers={"Auth": botPostKey.key},data=f'{json.dumps(info)}')
    return r.text

def user_check(userId,db=db):
    found = db.select({"discord_id": int(userId)},table="users")
    if found == []:
        db.insert({"discord_id": int(userId), "def_system": "None"},table="users")
        db.commit()
        return True
    return False

global guildsInfo
guildsInfo = guildInit()

cRed = discord.Color.red()

pColor = discord.Color.blue()


class ActionQueue:
    def __init__(self,loop_interval=60,db=db):
        self.loop = 0
        self.db = db
        self.loop_interval = float(loop_interval)

actQueue = ActionQueue()
@tasks.loop(seconds=actQueue.loop_interval)
async def action_queue(actQueue,db=db):
    actQueue.loop += 1
    rows = db.select_all()
    commit = False
    def rowSort(e):
        return e["activate"]
    rows.sort(key=rowSort)
    for x in rows:
        if x["activate"] <= epoch()+actQueue.loop_interval+10:
            await asyncio.sleep(x["activate"]-epoch())
            commit = True
            data = strJsonFrom(x["data"])
            if x["action"] == "test":
                c = client.get_channel(748584891171733650)
                await c.send(f'{data} - {x["activate"]} - {epoch()}')
            db.delete({"id": x["id"]})
    if commit:
        db.commit()

class PresUpdate:
    def __init__(self,db=db):
        self.loop = 0
        self.db = db

presUpdate = PresUpdate()
@tasks.loop(minutes=30)
async def presence_update(presUpdate,db=db):
    presUpdate.loop += 1
    presDict = strJsonFrom(db.select({"name": "presence"},table="data")[0]["data"])
    presDict["value"] = presDict["value"].replace("{servers}",f'{numbFormat(len(client.guilds))}').replace("{users}",f'{numbFormat(len(client.users))}')
    if presDict["value"] != client.activity.name:
        if presDict["type"] == "playing":
            activity = discord.Game(presDict["value"])
        elif presDict["type"] == "streaming":
            activity = discord.Streaming(name=presDict["value"]["title"],url=presDict["value"]["url"])
        elif presDict["type"] == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=presDict["value"])
        elif presDict["type"] == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=presDict["value"])
        else:
            activity = None
        await client.change_presence(activity=activity)

@client.event
async def on_ready():
    if actQueue.loop != 0:
        action_queue.restart(actQueue)
    else:
        action_queue.start(actQueue)
    if presUpdate.loop != 0:
        presence_update.restart(presUpdate)
    else:
        presence_update.start(presUpdate)
    print('EVENT: On ready detected')
    clientPost()
    embed=discord.Embed(title="Bot is ready!", color=0x76bb40)
    embed.set_footer(text=str(datetime.datetime.now()))
    channel = client.get_channel(748584891171733650)
    await channel.send(embed=embed)

    for x in client.users:
        user_check(x.id)

@client.event
async def on_member_join(member):
    user_check(member.id)
    
@client.event
async def on_raw_reaction_add(payload):
    try:
        guild = client.get_guild(payload.guild_id)
        channel = client.get_channel(payload.channel_id)
        if channel != None:
            message = await channel.fetch_message(payload.message_id)
        else:
            channel = user.dm_channel
            message = await channel.fetch_message(payload.message_id)
        try:
            reamemb = guild.get_member(payload.user_id)
        except:
            reamemb = client.get_user(payload.user_id)
        if guild != None:
            member = guild.get_member(message.author.id)
        else:
            member = client.get_user(message.author.id)


        if reamemb.id == client.user.id:
            return
        
        await vaal.pageCheck(message, payload.emoji, reactor=reamemb)



        
    except:
        embed = discord.Embed(title="Error",description=f'There was an unknown error caused by your reaction! We would like your permission to send this error to the developers, so that they can fix it. React with a :white_check_mark: to send.\n\n*Why do we ask?*\n||```\nWe are committed to protecting your right to privacy. We understand you may not be comfortable sending us the details we ask for when logging the error, and we respect that. This is why we give you the option.\n```||',color=discord.Color.red())
        embed = msgAuthor(embed,reamemb)
        embed.add_field(name="What Is Sent",value=f'- Your username\n- Your reaction\n- Message you reacted to\n- The exception (error)\n- Your permissions in the server')
        embed.add_field(name="Who Will See This",value=f'Only the bot developers and administrators will see the errors, and no information from them will be shared.')
        embed.set_footer(text='Status: Waiting for response...')
        msg = await message.author.send(embed=embed)
        await msg.add_reaction(u"\U00002705")
        def check(payload):
            return (payload.user_id == reamemb.id) and (msg.id == payload.message_id) and (str(payload.emoji) == u"\U00002705") and (payload.user_id != 748586188885065768)
        try:
            await client.wait_for('raw_reaction_add', check=check, timeout=120.0)
            errLogChan = client.get_channel(755229664511000676)

            error = traceback.format_exc()

            embed1 = discord.Embed(title=f'on_raw_reaction_add', description=f'{message.content}', color=discord.Color.red(),timestamp=message.created_at)
            gPerms = reamemb.guild_permissions
            def emojiBool(boolean):
                if boolean:
                    return ':white_check_mark:'
                else:
                    return ':x:'
            admin = emojiBool(gPerms.administrator)
            manGuild = emojiBool(gPerms.manage_guild)
            manChan = emojiBool(gPerms.manage_channels)
            manNick = emojiBool(gPerms.manage_nicknames)
            manRoles = emojiBool(gPerms.manage_roles)
            manMsg = emojiBool(gPerms.manage_messages)
            changeNick = emojiBool(gPerms.change_nickname)
            invite = emojiBool(gPerms.create_instant_invite)
            embed1.add_field(name="Reaction",value=f'**Name** {payload.emoji.name}\n**Custom?** {payload.emoji.is_custom_emoji()}\n\n{payload.emoji}',inline=False)
            embed1.add_field(name=f'__**PERMISSIONS**__',value=f'**ADMINISTRATOR** {admin}\n**MANAGE GUILD** {manGuild}\n**MANAGE CHANNELS** {manChan}\n**MANAGE ROLES** {manRoles}\n**MANAGE NICKNAMES** {manNick}\n**MANAGE MESSAGES** {manMsg}\n**CHANGE NICKNAME** {changeNick}\n**CREATE INVITE** {invite}')

            embed1 = msgAuthor(embed1,reamemb)
            embed1.set_footer(text=f'{member} | Message Author',icon_url=membere.avatar_url_as(format="png"))

            if len(error) < 900:
                embed1.add_field(name="Error", value=f"||```\n{error}\n```||",inline=False)
                await errLogChan.send(embed=embed1)
            else:
                fileF = open(f'error.txt', 'w+')
                fileF.write(str(error))
                fileF.close()
                await errLogChan.send(embed=embed1,file=discord.File(f'error.txt'))
            embed.set_footer(text='Status: Error Sent! Thank you.')
            await msg.edit(embed=embed)
        except:
            embed.set_footer(text='Status: Timed Out')
            await msg.edit(embed=embed)
            return None

@client.event
async def on_guild_join(guild):
    clientPost()
    GuildSettings(int(guild.id), "!")
    for x in guild.members:
        user_check(x.id)
    #guildsInfo = guildInit()

@client.event
async def on_guild_remove(guild):
    clientPost()
    guildsInfo = guildInit()

@client.event
async def on_member_update(before,after):
    if after.guild_permissions.manage_nicknames:
        return
    if str(before.guild.id) in guildsInfo:
        gSettings = guildsInfo[str(before.guild.id)]
    else:
        gSettings = GuildSettings(before.guild.id)
    guild = before.guild


    if after.nick == None or before.display_name == after.display_name:
        return

    def oldNameCheck(before=before,after=after,gSettings=gSettings):
        if gSettings.disNameWordStatus:
            settings = checkPresets(int(gSettings.disNameWordSens),gSettings.disNameWordWords)
            found = strCheck.checkText(before.display_name,settings)
            if found.found:
                return True
        if gSettings.disNameImpStatus:
            if int(gSettings.disNameImpRoles[0]) == 0:
                checkMemb = []
                for x in guild.members:
                    if x.id != after.id and (x.bot == False):
                        checkMemb.append(x.display_name)
            else:
                checkMemb = []
                for x in gSettings.disNameImpRoles:
                    r = guild.get_role(int(x))
                    if r != None:
                        for y in r.members:
                            if y.id != after.id and (y.bot == False):
                                checkMemb.append(y.display_name)
                                checkMemb.append(y.name)
            settings = checkPresets(1,checkMemb)
            found = strCheck.checkText(before.display_name,settings)
            if found.found:
                return True
        return False



        
    if gSettings.disNameStatus:
        if gSettings.disNameImpStatus:
            validRole = False
            if int(gSettings.disNameImpRoles[0]) == 0:
                checkMemb = []
                for x in guild.members:
                    if x.id != after.id and (x.bot == False):
                        checkMemb.append(x)
            else:
                checkMemb = []
                for x in gSettings.disNameImpRoles:
                    r = guild.get_role(int(x))
                    if r != None:
                        validRole = True
                        for y in r.members:
                            if y.id != after.id and (y.bot == False):
                                checkMemb.append(y)
            for x in checkMemb:
                if validRole:
                    settings = checkPresets(1,[x.display_name,x.name])
                else:
                    settings = checkPresets(1,[x.display_name])
                found = strCheck.checkText(after.display_name,settings)
                if found.found:
                    if gSettings.log != 0:
                        logChan = client.get_channel(gSettings.log)
                        if logChan != None:
                            embed = discord.Embed(title="Display Name Flag",description=f'**Infraction** Impersonation\n**Flagged Name** `{after.display_name}`\n**Impersonated User** {x.mention} ({x})')
                            embed.set_author(name=str(after),icon_url=after.avatar_url_as(format='png'))
                            await logChan.send(embed=embed)
                    if gSettings.disNameActChannelMsg != 0:
                        selChan = client.get_channel(int(gSettings.disNameActChannelMsg))
                        if selChan != None:
                            embed = discord.Embed(title="Impersonation",description=f'{after.mention} ({after}) set their display name to `{after.display_name}`. This name could be used to impersonate `{after.display_name}` {x.mention} ({x})')
                            embed.set_author(name=str(after),icon_url=after.avatar_url_as(format='png'))
                            await selChan.send(embed=embed)
                    if gSettings.disNameActDM:
                        embed = discord.Embed(title="Impersonation Notice",description=f'The display name you just set, `{after.display_name}`, was flagged as a possible impersonation of {x.mention} ({x})')
                        await after.send(embed=embed)
                    if gSettings.disNameActNameBack:
                        if oldNameCheck():
                            await after.edit(nick=None)
                        else:
                            await after.edit(nick=before.display_name)
                    break
                    
        if gSettings.disNameWordStatus:
            settings = checkPresets(int(gSettings.disNameWordSens),gSettings.disNameWordWords)
            found = strCheck.checkText(after.display_name,settings)
            if found.found:
                if gSettings.log != 0:
                    logChan = client.get_channel(gSettings.log)
                    if logChan != None:
                        embed = discord.Embed(title="Display Name Flag",description=f'**Infraction** Blacklisted Word\n**Flagged Name** `{after.display_name}`\n**Flagged Part** {found.flaggedStr}\n**Filter Matched** {found.filterMatch}')
                        embed.set_author(name=str(after),icon_url=after.avatar_url_as(format='png'))
                        await logChan.send(embed=embed)
                if gSettings.disNameActChannelMsg != 0:
                    selChan = client.get_channel(int(gSettings.disNameActChannelMsg))
                    if selChan != None:
                        embed = discord.Embed(title="Blacklisted Word",description=f'{after.mention} ({after}) set their display name to `{after.display_name}`. This name was matched to the following filter: `{found.filterMatch}`')
                        embed.set_author(name=str(after),icon_url=after.avatar_url_as(format='png'))
                        await selChan.send(embed=embed)
                if gSettings.disNameActDM:
                    embed = discord.Embed(title="Blacklisted Name Notice",description=f'The display name you just set, `{after.display_name}`, was flagged for blacklisted language. This name was matched to the following filter: `{found.filterMatch}`')
                    await after.send(embed=embed)
                if gSettings.disNameActNameBack:
                    if oldNameCheck():
                        await after.edit(nick=None)
                    else:
                        await after.edit(nick=before.display_name)

                            
@client.event
async def on_message(message):
    try:
        msgCnt = message.content.lower()

        staffBool = staffCheck(message.author.id)
                  

        if msgCnt.startswith(f'!disconnect') and staffBool:
            await message.channel.send(embed=discord.Embed(title='Disconnecting...',timestamp=datetime.datetime.utcnow()))
            await asyncio.sleep(.5)
            await client.logout()
            return
        
        if message.guild == None:
            return
        if str(message.guild.id) in guildsInfo:
            prefix = guildsInfo[str(message.guild.id)].prefix
            msgGuildSettings = guildsInfo[str(message.guild.id)]
        else:
            prefix = '!'
            msgGuildSettings = GuildSettings(message.guild.id)

        preLen = len(prefix)-1


        if msgCnt.startswith(f'{prefix}clear'):
               if msgCnt != f'{prefix}clear':
                     if message.author.guild_permissions.manage_messages:
                         number = message.content[7+preLen:]
                         try:
                            int(number)
                         except:
                            embed=discord.Embed(title=f'{number} is not a valid number! Please use an integer below 100.',color=discord.Color.red())
                            await message.channel.send(embed=embed)
                            return
                         if int(number) < 100:
                            messages = await message.channel.history(limit=(int(number)+1)).flatten()
                            messages.reverse()
                            msgLogging = await message.channel.send(embed=discord.Embed(title='LOGGING..',description=f'Storing all messages being cleared and preparing to clear them'))
                            creator = str(message.author)
                            createdDate = epochConv(mode='currEpoch')
                            msgLog = f'=================================\nSTART:\nCREATED BY: {creator}\nCREATED DATE: {createdDate}\nCHANNEL: {message.channel} ({message.channel.id})\n=================================\n\n\n'
                            for y in messages:
                                infoMsg = ''
                                infoMsg = f'{infoMsg}{y.author}  |  {y.created_at}:\n{y.content}'
                                if y.attachments != []:
                                    attachUrls = ''
                                    aCount = 0
                                    for j in y.attachments:
                                        aCount += 1
                                    nCount = 0
                                    for z in y.attachments:
                                        nCount += 1
                                        if aCount == nCount:
                                            attachUrls = f'    -{attachUrls}{z.url}'
                                        else:
                                            attachUrls = f'    -{attachUrls}{z.url}\n'
                                    infoMsg = f'{infoMsg}  ATTACHMENTS:\n{attachUrls}\n---------------------------------------------\n'
                                else:
                                    infoMsg = f'{infoMsg}\n---------------------------------------------\n'
                                msgLog = f'{msgLog}{infoMsg}'
                            msgLog = f'{msgLog}\n\n\n=================================\nEND\n================================='
                            fileF = open(f'cleared.txt', 'w')
                            fileF.write(msgLog)
                            fileF.close()
                            os.remove("cleared.txt")

                            await message.channel.delete_messages(messages)
                            embed=discord.Embed(title='Cleared ' + str(number) + ' message(s)!',color=pColor)
                            await msgLogging.edit(embed=embed)
                            embed = discord.Embed(title=f'CLEARED {number} MESSAGES',description=f'**Channel** #{message.channel.name} ({message.channel.id})')
                            embed.set_author(name=str(message.author),icon_url=message.author.avatar_url_as(format='png'))
                            logChannel = client.get_channel(msgGuildSettings.log)
                            if logChannel != None:
                                await logChannel.send(embed=embed,file=discord.File(f'cleared.txt'))
                            await asyncio.sleep(4)
                            try:
                                await msgLogging.delete()
                            except:
                                None
                            return
                         else:
                            embed=discord.Embed(title=f'{number} is too high! Please use a number below 100.',color=discord.Color.red())
                            await message.channel.send(embed=embed)
                            return
                     else:
                        embed=discord.Embed(title='This command is only available to those with manage message perms!',color=discord.Color.red())
                        await message.channel.send(embed=embed)
                        return
               else:
                     embed=discord.Embed(title=f'**{prefix}Clear** *(# to clear)*',description=f'Clear up to 99 messages that are less than 14 days old within a channel. Can only be used by those with manage message permissions in a server.\n\nEXAMPLE: {prefix}clear 23',color=discord.Color.red())
                     await message.channel.send(embed=embed)
                     return

        
        if message.channel.id == 750934765032702032 and message.webhook_id != None:
            try:
                givenDict = json.loads(f'{message.content[2:-1]}')
                if "guild_update" in givenDict:
                    guildUpdatedId = givenDict["guild_update"]
                    guildsInfo[guildUpdatedId].update()
                elif "client_post" in givenDict:
                    clientPost()
                elif "pfp_change" in givenDict:
                    clientUser = client.user
                    response = requests.get("https://auxilus.ml/resources/new_pfp",headers={"Auth": botPostKey.key})
                    await clientUser.edit(avatar=response.content)
                elif "important_staff_msg" in givenDict:
                    staffChan = client.get_channel(753455199053676614)
                    await staffChan.send(givenDict["important_staff_msg"])
                elif "ping_test" in givenDict:
                    receivedTime = epochMS()
                    sendTime = givenDict["ping_test"]["send"]
                    siteToBotDur = receivedTime - sendTime#site to bot communication time
                    testChan = client.get_channel(748584891171733650)
                    sendMsgTime = epochMS()
                    testMsg = await testChan.send('Ping test..')
                    sentMsgTime = epochMS()
                    await testMsg.edit(content='Ping test.. edit')
                    editMsgTime = epochMS()
                    msgSendDur = sentMsgTime - sendMsgTime#time to send msg
                    editMsgDur = editMsgTime - sentMsgTime#time to edit msg
                    msLatency = round(client.latency * 1000, 1)#bot ping
                    info = {"site": round(siteToBotDur,1),"msgSend": round(msgSendDur,1),"msgEdit": round(editMsgDur,1),"latency": msLatency, "updated": epoch()}
                    r = requests.post("https://auxilus.ml/ping_data",headers={"Auth": botPostKey.key},data=f'{json.dumps(info)}')
                    if r.json()["success"] == True:
                        return
                elif "new_post_key" in givenDict:
                    await asyncio.sleep(1)
                    r = requests.post("https://auxilus.ml/get_new_key")
                    newPostKey = r.text
                    keysF = open('keys.json')
                    keys = json.load(keysF)
                    keys["postKey"] = newPostKey
                    with open('keys.json','w') as f:
                        json.dump(keys, f, indent=4)
                    botPostKey.update()
                elif "change_presence" in givenDict:
                    presDict = givenDict["change_presence"]
                    db.update({"data": strJsonTo(presDict)},{"name": "presence"},table="data")
                    db.commit()
                    clientPost()
                    presDict["value"] = presDict["value"].replace("{servers}",f'{numbFormat(len(client.guilds))}').replace("{users}",f'{numbFormat(len(client.users))}')
                    if presDict["type"] == "playing":
                        activity = discord.Game(presDict["value"])
                    elif presDict["type"] == "streaming":
                        activity = discord.Streaming(name=presDict["value"]["title"],url=presDict["value"]["url"])
                    elif presDict["type"] == "listening":
                        activity = discord.Activity(type=discord.ActivityType.listening, name=presDict["value"])
                    elif presDict["type"] == "watching":
                        activity = discord.Activity(type=discord.ActivityType.watching, name=presDict["value"])
                    else:
                        activity = None
                    await client.change_presence(activity=activity)
            except:
                print(message.content)
                print(traceback.format_exc())
            return


        if msgCnt.startswith(f'{prefix}staff') and message.author.id == 312049173895839746:
            if msgCnt == f'{prefix}staff':
                await message.channel.send("No input found.")
                return
            choice = message.content[7+preLen:]
            cMemb = searchDiscord(choice,message.guild)
            if cMemb == None:
                embed = discord.Embed(title="Invalid User",description="The user you provided was not found.")
                await message.channel.send(embed=embed)
                return
            else:
                staffDict = staffCheckObj.refreshCheck().dict
                staffList = staffDict["staff"]
                if cMemb.id in staffList:
                    staffList.remove(cMemb.id)
                    embed = discord.Embed(title="User Removed",description=f'{cMemb.mention} was removed from the staff list!')
                    await message.channel.send(embed=embed)
                else:
                    staffList.append(cMemb.id)
                    embed = discord.Embed(title="User Added",description=f'{cMemb.mention} was added to the staff list!')
                    await message.channel.send(embed=embed)
                staffDict["staff"] = staffList
                with open('staff.json','w') as f:
                    json.dump(staffDict, f, indent=4)
                return
                
                
        msgChan = message.channel
        async def send(content=None,embed=None,channel=None,msgChan=msgChan,author=message.author):
            try:
                if channel == None:
                    channel = msgChan
                elif isinstance(channel, int) == False:
                    channel = channel
                else:
                    channel = client.get_channel(channel)
            except:
                print(f'ERROR[01] WITH CHANNEL ({channel})')
                await msgChan.send('ERROR WITH CHANNEL SELECTION')
                return
            try:
                msgRet = await channel.send(content=content,embed=embed)
                return msgRet
            except:
                print(f'ERROR[02] WITH Sending ({channel})')
                await author.send('ERROR WITH SENDING MESSAGE') 
                return


        if msgCnt.startswith(f'!botprefix'):
            await message.channel.send(prefix)
            return

        if msgCnt.startswith(f'{prefix}hello'):
            await message.channel.send("hello!")
            return


        if msgCnt == f'{prefix}help':
            embed = discord.Embed(title=f'Information (Help)',description=f'This bot is quite new, and is in development. That means that there are few features so far, but it will be growing a lot. Display Name moderation is only available using the online dashboard. Message `Pmblue#1085` w/ questions, suggestions, or feedback!\n\n__Cmd Arguments Legend__\n<required>\n(optional)',url="https://auxilus.ml")
            embed.set_author(name='Support Server',url='https://discord.gg/aXSZzpm')
            embed.add_field(name="Commands",value=f'**{prefix}twitchstats <username>** Returns information on a Twitch streamer. If they are live, it also has a second page with information about their stream.\n**{prefix}prefix <new prefix>** Command used for setting new prefix (manage server required)\n**{prefix}dashboard** Get a link to your servers dashboard page.\n**{prefix}sysdefault <system name>** (Eve) Set your default system for Eve. Do `{prefix}sysdefault` for more info.\n**{prefix}res find <location> <resources>** (Eve) Search for planets within an area that have certain resources. Do `{prefix}res find` for more info.')
            await send(embed=embed)
            return
        
    ##    if msgCnt.startswith(f'{prefix}clientpost'):
    ##        await message.channel.send(clientPost())
    ##        return
    ##
    ##    if msgCnt.startswith(f'{prefix}guildspost'):
    ##        r = requests.post("https://auxilus.ml/bot_request/init",headers={"Auth": botPostKey.key})
    ##        await message.channel.send(str(r.json()))
    ##        return

        if msgCnt.startswith(f'{prefix}twitchstats'):
            choice = message.content[13+preLen:]
            twitch = vaal.Twitch()
            found = twitch.userSearch(choice)
            if found == []:
                embed = discord.Embed(title=f'Twitch Stats',description=f'None found!')
                await send(embed=embed)
                return
            user = found[0]
            stream = user.stream()
            if stream != None:
                channel = stream.channel
                streamStr = 'LIVE'
            else:
                channel = user.channel()
                streamStr = 'Offline'
            url = channel.url
            display = channel.display
            logo = channel.logo
            views = channel.views
            followers = channel.followers
            partner = channel.partner
            mature = channel.mature
            cId = channel.id
            bio = user.bio
            lang = channel.language
            embed = discord.Embed(title=f'{display}',description=f'**Views** {numbFormat(views)}\n**Followers** {numbFormat(followers)}\n**Mature?** {mature}\n**Partner?** {partner}\n**Language** {lang}\n**Status** {streamStr}',url=url,color=pColor)
            embed.set_author(name=f'Twitch Stats', icon_url='https://assets.help.twitch.tv/Glitch_Purple_RGB.png')
            embed.add_field(name='Bio',value=bio)
            embed.set_thumbnail(url=logo)
            if stream != None:
                sId = stream.id
                status = channel.status
                description = channel.description
                preview = stream.preview
                viewers = stream.viewers
                game = stream.game
                fps = stream.fps
                embed2 = discord.Embed(title=f'{status}',description=f'{description}\n\n**Game** {game}\n**Viewers** {numbFormat(viewers)}\n**Avg. FPS** {fps}\n\n||*Not live values*||\n__Preview__',url=url,color=pColor)
                embed2.set_author(name=f'Twitch Stats (Current Stream)', icon_url='https://assets.help.twitch.tv/Glitch_Purple_RGB.png')
                embed2.set_image(url=preview)
                msg = await send(embed=embed)
                await vaal.pageMessage(msg,[embed,embed2])
            else:
                await send(embed=embed)
            return


        if msgCnt.startswith(f'{prefix}prefix'):
            perms = message.author.guild_permissions.manage_guild
            if msgCnt == f'{prefix}prefix':
                if perms:
                    embed = discord.Embed(title=f'Set Prefix',description=f'Use this command to set the command prefix for this bot on this server. Can be a maximum of 8 characters, and the last character cannot be alphanumeric.\n\nYou must have manage server permissions to use this command.')
                    await send(embed=embed)
                    return
                else:
                    embed = discord.Embed(title='Insufficient Permissions',description='You must have manage server permissions to use this command.',color=cRed)
                    await send(embed=embed)
                    return
            else:
                if perms:
                    choice = message.content[8+preLen:].lower()
                    if prefix != choice:
                        if len(choice) > 8:
                            embed = discord.Embed(title='Too Many Characters',description=f'Your new prefix can only be up to 8 characters long, the prefix you provided was *{len(choice)}* long.',color=cRed)
                            await send(embed=embed)
                            return
                        if choice[-1] in ["!","?",")","*","&","^","%","$","#","@",":",";",".",",","<",">","~"]:
                            r = requests.post("https://auxilus.ml/bot_request/guild_prefix_update",headers={"Auth": botPostKey.key,"guildId": str(message.guild.id),"prefix": choice})
                            guildsInfo[str(message.guild.id)].prefix = choice
                            embed = discord.Embed(title='Prefix Set',description=f'Prefix has been changed!\n\n`{prefix}` --> `{choice}`')
                            await send(embed=embed)
                            return
                        else:
                            embed = discord.Embed(title='Invalid Prefix',description=f'The last character of the prefix was invalid. Remember, the final character in prefix must not be alphanumeric.',color=cRed)
                            await send(embed=embed)
                            return
                    else:
                        embed = discord.Embed(title='No Change',description='Prefix choice provided is same as the current prefix.')
                        await send(embed=embed)
                        return
                else:
                    embed = discord.Embed(title='Insufficient Permissions',description='You must have manage server permissions to use this command.',color=cRed)
                    await send(embed=embed)
                    return

        if msgCnt.startswith(f"{prefix}sysdefault"):
            if msgCnt == f"{prefix}sysdefault":
                embed = discord.Embed(title='Set Default System',description=f'Sets your default Eve system, to allow distance in jumps to be displayed when using `{prefix}res find`')
                embed.add_field(name="Command Usage",value=f'**{prefix}sysdefault** <system name>')
                currDef  = db.select({"discord_id": message.author.id},table="users")[0]["def_system"]
                if currDef != "None":
                    currDef = eve.System(int(currDef)).name
                embed.add_field(name="Current Default System", value=currDef,inline=False)
                await send(embed=embed)
                return
            choice = message.content[12+preLen:]
            found = eve.find_system(choice)
            if found == None:
                embed = discord.Embed(title='System Not Found',color=discord.Color.red())
                await send(embed=embed)
                return
            db.update({"def_system": str(found.id)},{"discord_id": message.author.id},table="users")
            db.commit()
            embed = discord.Embed(title='Default System Set',description=f'Your default/home system has been to `{found.name}`')
            await send(embed=embed)
            return

        if msgCnt.startswith(f"{prefix}res find"):
            if msgCnt == f"{prefix}res find":
                embed = discord.Embed(title='Resource Search',description='This command is used to find resources at certain output levels at planets.')
                embed.add_field(name='Command Usage',value=f'**{prefix}res find** <location> <resources>\n-----------------\n**Location** - This is either `All`, to search all of New Eden, `Near`, to check constellations nearby your default system, or the name of a region or constellation with no spaces. not capitalization or dash sensitive.\n**Resources** - A comma seperated list of the resources you want to be in the planets. If you want to search for certain amounts of output for each material, you can add `:<amt>`, such as `Base Metals:9`, to find planets with base metal outputs of 9 or more.',inline=False)
                embed.add_field(name='Examples',value=f'**{prefix}res find Impass Base Metals,LusteringAlloy:30**\nThis would find all planets in the Impass region that have BaseMetals, and output 30+ Lustering Alloy.\n\n**OTHERS**\n**{prefix}res find Impass BaseMetals:6,LA:30**\n**{prefix}res find All LA:24**\n**{prefix}res find near MC:30**')
                await send(embed=embed)
                return
            args = message.content[10+preLen:].split(" ",1)
            if len(args) != 2:
                embed = discord.Embed(title='Not Enough Arguments',description=f'You did not provide enough arguments! Do `{prefix}res find` for information on proper usage of this command.',color=discord.Color.red())
                await send(embed=embed)
                return                
            locType = "Region"
            location = eve.find_region(args[0])
            async def res_find_dict(args=args):
                while ", " in args[1]:
                    args[1] = args[1].replace(", ",",")
                while ": " in args[1]:
                    args[1] = args[1].replace(": ",":")
                if ",:" in args[1]:
                    embed = discord.Embed(title='Blank Resource Given',description=f'Found instance where no resource was provided! Do `{prefix}res find` for information on proper usage of this command.',color=discord.Color.red())
                    await send(embed=embed)
                    return None
                if ":," in args[1]:
                    args[1] = args[1].replace(":,",":0,")
                resRaw = args[1].split(",")
                resSel = {}
                for x in resRaw:
                    if ":" in x:
                        res0 = x.split(":")
                        res1 = res0[0]
                        res2 = float(res0[1])
                    else:
                        res1 = x
                        res2 = 0
                    foundRes = eve.find_resource(res1)
                    if foundRes == None:
                        embed = discord.Embed(title='Resource Not Found',description=f'Did not find a resource called `{res1}`',color=discord.Color.red())
                        await send(embed=embed)
                        return None
                    resSel[foundRes] = res2
                return resSel
            userLate = True
            if location == None:
                location = eve.find_constellation(args[0])
                locType = "Constellation"
                if args[0].lower() == "all":
                    locType = "All"
                    location = eve.AllPlanets()
                if args[0].lower() in ["near","nearby"]:
                    locType = "Near"
                    user = db.select({"discord_id": message.author.id},table="users")[0]
                    if user["def_system"] == "None":
                        embed = discord.Embed(title='Invalid Location',description=f'You cannot use Near as location unless you have a default system set. Do `{prefix}sysdefault` to see how to set one!',color=discord.Color.red())
                        await send(embed=embed)
                        return
                    else:
                        location = eve.Constellation(eve.System(int(user["def_system"])).constellation)
                    userLate = False
                elif location == None:
                    embed = discord.Embed(title='Location Not Found',description=f'Did not find a region or constellation with that name!',color=discord.Color.red())
                    await send(embed=embed)
                    return
            resSel = await res_find_dict()
            if resSel == None:
                return
            resList = []
            for x in resSel:
                resList.append(x)
            if locType == "Near":
                foundList = location.resource_find_output(resSel)
                for x in location.neighbors():
                    foundList = foundList + x.resource_find_output(resSel)
            else:
                foundList = location.resource_find_output(resSel)
            if foundList == []:
                embed = discord.Embed(title='No Planets Found',description=f'Did not find any planets with those specified resources.',color=discord.Color.red())
                await send(embed=embed)
                return
            foundList = eve.score_sort(foundList,resList)
            if userLate:
                user = db.select({"discord_id": message.author.id},table="users")[0]
            def planet_field(embed,planet,home=user["def_system"],resList=resList,locType=locType):
                if home == "None" or locType == "All":
                    name = f'**{planet.name}**'
                else:
                    distance = eve.jump_dist(eve.System(int(home)),planet.system())
                    if distance == None:
                        name = f'**{planet.name}** | 15+ Jumps'
                    else:
                        name = f'**{planet.name}** | {len(distance)} Jumps'
                value = f'**Region** {planet.region}\n**Constellation** {planet.constellation}\n**System** {planet.system_name}\n-----------------'
                for x in resList:
                    resObj = eve.ext_res(planet,x)
                    value = f'{value}\n{resObj.name} - {resObj.output} ({resObj.richness})'
                embed.add_field(name=name,value=value,inline=False)
                return embed
            pages = []
            displayed = 0
            disTotal = 0
            if locType == "Near":
                searchedIn = "Current and nearby constellations"
            else:
                searchedIn = location.name
            embed = discord.Embed(title=f'Planets Found',description=f'**Searched In** {searchedIn} ({locType})\n\nDisplayed in order of best mix in production for the requested resources. Max of 200 results.')
            embed.set_author(name=f'Found {len(foundList)} results!')
            for x in foundList:
                disTotal += 1
                if displayed > 9:
                    pages.append(embed)
                    embed = discord.Embed(title="Planets Found")
                    embed.set_author(name=f'Found {len(foundList)} results!')
                    displayed = -1
                embed = planet_field(embed,x)
                displayed += 1
                if disTotal > 200:
                    break
            pages.append(embed)
            msg = await send(embed=pages[0])
            await vaal.pageMessage(msg,pages)
            return
            
            

                
        if msgCnt == f'{prefix}ping':
            msLatency = round(client.latency * 1000, 1)
            await send(embed=discord.Embed(title=str(msLatency) + 'ms'))
            return

        if msgCnt == f'{prefix}settings':
            embed = discord.Embed(title="Settings",description=f'**Display Status** {msgGuildSettings.disNameStatus}\n**Log Channel** {msgGuildSettings.log}\n**Change Nick Back** {msgGuildSettings.disNameActNameBack}')
            await send(embed=embed)
            return

        if msgCnt == f'{prefix}dashboard':
            embed = discord.Embed(title="Dashboard",description=f'Go to your servers\'s web dashboard [**here**](https://auxilus.ml/guild/{message.guild.id}/main).\n\n Only people who have Manage Server perms will be able to successfully use this dashboard. You must log in to the site to gain access.')
            await send(embed=embed)
            return

        if msgCnt == f'{prefix}error' and staffBool:
            raise Exception("This is a test.")

        if msgCnt == f'!siteadmintoggle' and message.author.id == 312049173895839746:
            r = requests.post("https://auxilus.ml/admin_status_update",headers={"Auth": botPostKey.key,"Status": "toggle"})
            print(r.text)
            status = r.json()["admin_status"]
            embed = discord.Embed(title=f'Admin Features Toggled',description=f'Availability of admin features on the website have been set to `{status}`.')
            await send(embed=embed)
            return

        if msgCnt == f'!adminlockdowntest' and message.author.id == 312049173895839746:
            r = requests.post("https://auxilus.ml/admin_status_update",headers={"Auth": botPostKey.key,"Status": "false","lockdown": "this is a test."})
            print(r.text)
            status = r.json()["admin_status"]
            embed = discord.Embed(title=f'Admin Lockdown Test Run',description=f'Test on the lockdown of admin features has been run.')
            await send(embed=embed)
            return

        if msgCnt == f'{prefix}serverinfo':
            msgGuild = message.guild
            memCount = message.guild.member_count   
            ownMention = message.guild.owner.mention
            gIcon = msgGuild.icon_url_as(static_format='png')
            gPerms = msgGuild.me.guild_permissions
            def emojiBool(boolean):
                if boolean:
                    return ':white_check_mark:'
                else:
                    return ':x:'
            admin = emojiBool(gPerms.administrator)
            manGuild = emojiBool(gPerms.manage_guild)
            manChan = emojiBool(gPerms.manage_channels)
            manNick = emojiBool(gPerms.manage_nicknames)
            manRoles = emojiBool(gPerms.manage_roles)
            manMsg = emojiBool(gPerms.manage_messages)
            changeNick = emojiBool(gPerms.change_nickname)
            invite = emojiBool(gPerms.create_instant_invite)
            embed=discord.Embed(description=f'**Owner** {ownMention}\n**Member Count** {memCount}\n**Booster # (tier)** {msgGuild.premium_subscription_count} ({msgGuild.premium_tier})\n**Created (UTC)** {msgGuild.created_at}\n**Bot Joined (UTC)** {msgGuild.me.joined_at}',color=pColor)
            embed.set_author(name=msgGuild.name,icon_url=gIcon)
            embed.add_field(name=f'__**BOT PERMISSIONS**__',value=f'**ADMINISTRATOR** {admin}\n**MANAGE GUILD** {manGuild}\n**MANAGE CHANNELS** {manChan}\n**MANAGE ROLES** {manRoles}\n**MANAGE NICKNAMES** {manNick}\n**MANAGE MESSAGES** {manMsg}\n**CHANGE NICKNAME** {changeNick}\n**CREATE INVITE** {invite}')
            await message.channel.send(embed=embed)
            await msgLog('serverinfo')
            return

    except:
        embed = discord.Embed(title="Error",description=f'There was an unknown error caused by your message/command! We would like your permission to send this error to the developers, so that they can fix it. React with a :white_check_mark: to send.\n\n*Why do we ask?*\n||```\nWe are committed to protecting your right to privacy. We understand you may not be comfortable sending us the details we ask for when logging the error, and we respect that. This is why we give you the option.\n```||',color=discord.Color.red())
        embed = msgAuthor(embed,message.author)
        embed.add_field(name="What Is Sent",value=f'- Your username\n- Your message\n- The exception (error)\n- Your permissions in this server')
        embed.add_field(name="Who Will See This",value=f'Only the bot developers and administrators will see the errors, and no information from them will be shared.')
        embed.set_footer(text='Status: Waiting for response...')
        if message.guild == None:
            msg = await message.author.send(embed=embed)
        else:
            msg = await message.channel.send(embed=embed)
        await msg.add_reaction(u"\U00002705")
        def check(payload):
            return (payload.user_id == message.author.id) and (msg.id == payload.message_id) and (str(payload.emoji) == u"\U00002705") and (payload.user_id != 748586188885065768)
        try:
            await client.wait_for('raw_reaction_add', check=check, timeout=120.0)
            errLogChan = client.get_channel(755229664511000676)

            error = traceback.format_exc()

            embed1 = discord.Embed(title=f'on_message', description=f'{message.content}', color=discord.Color.red(),timestamp=message.created_at)
            gPerms = message.author.guild_permissions
            def emojiBool(boolean):
                if boolean:
                    return ':white_check_mark:'
                else:
                    return ':x:'
            admin = emojiBool(gPerms.administrator)
            manGuild = emojiBool(gPerms.manage_guild)
            manChan = emojiBool(gPerms.manage_channels)
            manNick = emojiBool(gPerms.manage_nicknames)
            manRoles = emojiBool(gPerms.manage_roles)
            manMsg = emojiBool(gPerms.manage_messages)
            changeNick = emojiBool(gPerms.change_nickname)
            invite = emojiBool(gPerms.create_instant_invite)
            embed1.add_field(name=f'__**PERMISSIONS**__',value=f'**ADMINISTRATOR** {admin}\n**MANAGE GUILD** {manGuild}\n**MANAGE CHANNELS** {manChan}\n**MANAGE ROLES** {manRoles}\n**MANAGE NICKNAMES** {manNick}\n**MANAGE MESSAGES** {manMsg}\n**CHANGE NICKNAME** {changeNick}\n**CREATE INVITE** {invite}')

            embed1 = msgAuthor(embed1,message.author)
            embed1.set_footer(text=str(datetime.datetime.utcnow()))

            if len(error) < 900:
                embed1.add_field(name="Error", value=f"||```\n{error}\n```||",inline=False)
                await errLogChan.send(embed=embed1)
            else:
                fileF = open(f'error.txt', 'w+')
                fileF.write(str(error))
                fileF.close()
                await errLogChan.send(embed=embed1,file=discord.File(f'error.txt'))
            embed.set_footer(text='Status: Error Sent! Thank you.')
            await msg.edit(embed=embed)
        except:
            embed.set_footer(text='Status: Timed Out')
            await msg.edit(embed=embed)
            return None




            

client.run(TOKEN)
