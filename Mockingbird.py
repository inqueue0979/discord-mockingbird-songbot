from types import NoneType
import discord
from discord import Intents
from discord.utils import get
from discord.ext import tasks
import youtube_dl
import traceback
import pafy
import asyncio
import re
from discord.ext import commands
from discord_buttons_plugin import  *
from youtubesearchpython import VideosSearch
#from discord_slash import SlashCommand

client = commands.Bot(command_prefix=";", intents=Intents.default())
buttons = ButtonsClient(client)
intents = discord.Intents.all()
#slash = SlashCommand(client)

#서버 설정~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

token = open("token", "r").readline()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

client.code = str()
client.ownid = 0
client.ids = list() #노래옹재 채널들
client.channels = list() #노래옹재가 활동하는 채널들 리스트
client.voice_num = list()

client.playlistEmbed = list() #대기열 임베드
client.topbanner =list() #노래옹재 배너 임베드
client.svembed = list() #주 임베드

playerlist = list() #신청인 리스트
playlist = list() #재생목록 리스트
channellist = list() #신청채널 리스트

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#링크 가져오기

profilePng = "https://media.discordapp.net/attachments/978242366873927741/995262978515533894/new.png?width=585&height=585"
bigBannerPng = "https://media.discordapp.net/attachments/978242366873927741/1007939098973048913/-001.png?width=960&height=540"
defaultBannerPng = "https://media.discordapp.net/attachments/978242366873927741/995286116108349551/-001.png?width=959&height=250"
playBannerPng = "https://media.discordapp.net/attachments/978242366873927741/995265214490619974/-001_2.png?width=959&height=250"
pauseBannerPng = "https://media.discordapp.net/attachments/978242366873927741/995266331538632784/-001_3.png?width=959&height=250"

client.version = "1.0"
client.headColor = 0x62c1cc
client.webPage = "https://wjcomingsoon.netlify.app/"
client.developerPage = "https://github.com/inqueue0979"
client.howtoPage = "https://wjcomingsoon.netlify.app/"
client.donationPage = "https://wjcomingsoon.netlify.app/"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.event
async def on_ready():
    print("로그인 | " + client.user.name)

    if client.user.name == "노래옹재":
        client.code = "WJSB"
        client.ownid = 1023447708679274507
    elif client.user.name == "노래옹재 β":
        client.code = "WJSB_B"
        client.ownid = 934446134460579850


    await client.change_presence(status=discord.Status.online, activity=discord.Game(str(len(client.guilds)) + "곳에서 노래 재생"))
    print("서버 로딩중..")
    
    for guild in client.guilds:
        client.ids.append(guild.id)
        print(guild.name + " | " + str(guild.id) + " | " + str(client.ids.index(guild.id)))

        for channel in guild.channels:
            if type(channel) == discord.channel.TextChannel: #채널이 텍스트 채널인지 확인
                if channel.topic is not None and "[" + client.code + "]" in channel.topic: #노래옹재 채널 찾기
                    
                    default_noti = False

                    if(guild.default_notifications == discord.NotificationLevel.all_messages):
                        await guild.edit(default_notifications=discord.NotificationLevel.only_mentions)
                        default_noti = True

                    #찾은 노래옹재 채널 초기 설정
                    await channel.purge()
                    client.channels.append(channel)

                    pembed = discord.Embed(color=0x62c1cc)
                    pembed.add_field(name="대기열 | QUEUE", value= "여긴 아직 아무것도 없어요.. 노래를 신청해봐요!", inline=True)
                    pEmbed = await channel.send(embed=pembed)
                    client.playlistEmbed.append(pEmbed)

                    banner = discord.Embed(color=0x62c1cc)
                    banner.set_image(url= defaultBannerPng)
                    tbanner = await channel.send(embed=banner)
                    client.topbanner.append(tbanner)

                    embed = discord.Embed(color=0x62c1cc)
                    embed.add_field(name=client.user.name + " (●'◡'●)", value= "[홈페이지](<%s>) | [개발자 페이지](<%s>) | [노래옹재 사용법](<%s>) | [후원](<%s>)" % (client.webPage, client.developerPage, client.howtoPage, client.donationPage), inline=False)
                    embed.set_image(url= bigBannerPng)
                    sembed = await channel.send(embed=embed)
                    client.svembed.append(sembed)

                    await Buttons(channel)

                    playlist.append([])
                    playerlist.append([])
                    channellist.append([])

                    if default_noti == True:
                        await guild.edit(default_notifications=discord.NotificationLevel.all_messages)

                    break
    
    print("로딩 완료.")

@tasks.loop(minutes = 5)
async def change_status():
    try:
        count = str(len(client.guilds))
        await client.change_presence(status=discord.Status.online, activity=discord.Game(count + "곳에서 노래 재생"))
    except Exception as e:
        print("Change Status")

change_status.start() #루프 시작

@client.event
async def on_guild_join(guild):

    await asyncio.sleep(1)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            iembed = discord.Embed(color=0x62c1cc)
            iembed.add_field(name="🕊️ 노래옹재 24/7 🕊️", value= "[홈페이지](<%s>) | [개발자 페이지](<%s>) | [노래옹재 사용법](<%s>) | [후원](<%s>)" % (client.webPage, client.developerPage, client.howtoPage, client.donationPage), inline=True)
            iembed.add_field(name="_", value= "초기 설정을 하시려면 아래의 설정 버튼을 눌러주세요.", inline=False)
            #또는 /setup 을 사용하셔도 됩니다. << 셋업명령어 추가하기
            iembed.set_image(url=bigBannerPng)
            await channel.send(embed=iembed)
            await InitButton(channel)
        break

    await client.change_presence(status=discord.Status.online, activity=discord.Game(str(len(client.guilds)) + "곳에서 노래 재생"))


@client.event
async def on_message(message):

    #봇 자신이 보낸 메세지인지 체크하고, 등록된 채팅방에서만 노래커맨드 사용하기
    if message.author.bot == 1: return
    if not message.channel in client.channels: return

    #노래옹재 방에 달린 메세지 지우기
    await asyncio.sleep(0.2)
    await message.delete()

    #정규 표현식을 사용해 제대로 된 유튜브 링크인지 검사
    try:
        isRightURL = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', message.content) 

        if isRightURL == None: #유튜브 링크인지 체크
            
            #embed = discord.Embed(title= "제대로 된 유튜브 링크를 입력해주세요! 😥", color=0x62c1cc)
            #msg = await message.channel.send(embed=embed)
            #await asyncio.sleep(1)
            #await msg.delete()

            message.content = VideosSearch(message.content, limit=1).result()["result"][0]['link']
            print("Searching YT...")

    except IndexError as e:
        print(e)
        embed = discord.Embed(title= "오류가 발생했어요! 😥", color=0x62c1cc)
        msg = await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        await msg.delete()
        return

    gid = client.ids.index(message.guild.id)

    if type(message.author.voice) != NoneType:
        try:
            playlist[gid].append(message.content)
            playerlist[gid].append(message.author)
            channellist[gid].append(message.author.voice.channel)
        except Exception as e:
            print("오류!" + e)
    else:
        embed = discord.Embed(title= "채널에 들어가 있으셔야 접속할 수 있어요! 😥", color=0x62c1cc)
        msg = await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        await msg.delete()
        return

    vc = get(client.voice_clients, guild=message.guild) #접속해있는 voice client 있는지 체크

    if not vc:
        print("길드에 접속해있는 노래옹재 없음, 노래 재생")
        await SongPlay(message.guild)
        return
    else:
        print("대기열로 추가")

        await reload_playlist_gui(gid)
        embed = discord.Embed(title= "🌟 대기열 추가 완료", color=0x62c1cc)
        msg = await message.channel.send(embed=embed)
        await asyncio.sleep(1)
        await msg.delete()
        return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#노래 재생과 플레이리스트 설정
async def SongPlay(guild):

    gid = client.ids.index(guild.id)
    vc = get(client.voice_clients, guild=guild)


    if playlist[gid] != []: 
        player = playerlist[gid][0]
        url = playlist[gid][0]
        channel = channellist[gid][0]

        del playerlist[gid][0]
        del playlist[gid][0]
        del channellist[gid][0]

    else:
        try:
            await reset_gui(gid)
            await vc.disconnect()
        except:
            pass
        return

    if not vc:
        try:
            vc = await channel.connect()
        except Exception as e:
            print("오류! " + e)

                
    try:
        if vc.channel != channel:
            await vc.disconnect()
            vc = await channel.connect()
    except Exception as e:
        print("오류! " + str(e))


    try:
        ydl_opts = {'format':'bestaudio/best', 'noplaylist':'True', 'default_search': 'auto'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
    except:
        print("오류!")
        return

    video_info = pafy.new(url)
    banner = discord.Embed(color=0x62c1cc)
    banner.set_image(url= playBannerPng)
    await client.topbanner[gid].edit(embed=banner)
    embed = discord.Embed(color=0x62c1cc)
    embed.add_field(name=video_info.author + " | [" + video_info.duration + "] | " + player.name, value="[%s](<%s>)" % (video_info.title, url), inline=False)
    embed.set_image(url= video_info.bigthumbhd)
    await client.svembed[gid].edit(embed=embed)
    await reload_playlist_gui(gid)
    vc.play(discord.FFmpegOpusAudio(URL, **FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else client.loop.create_task(SongPlay(guild)))
    vc.pause()
    await asyncio.sleep(1)
    vc.resume()

#GUI 전체 리셋
async def reset_gui(gid):

    pembed = discord.Embed(color=0x62c1cc)
    pembed.add_field(name="대기열 | QUEUE", value= "여긴 아직 아무것도 없어요.. 노래를 신청해봐요!", inline=True)
    await client.playlistEmbed[gid].edit(embed=pembed)

    banner = discord.Embed(color=0x62c1cc)
    banner.set_image(url= defaultBannerPng)
    await client.topbanner[gid].edit(embed=banner)

    embed = discord.Embed(color=0x62c1cc)
    embed.add_field(name=client.user.name + " (●'◡'●)", value= "[홈페이지](<%s>) | [개발자 페이지](<%s>) | [노래옹재 사용법](<%s>) | [후원](<%s>)" % (client.webPage, client.developerPage, client.howtoPage, client.donationPage), inline=False)
    embed.set_image(url= bigBannerPng)
    await client.svembed[gid].edit(embed=embed)


#플레이리스트 GUI 리셋
async def reload_playlist_gui(gid):

    embed = discord.Embed(title= "대기열 | QUEUE", color=0x62c1cc)
    for u in range(len(playlist[gid])):
        list_info = pafy.new(playlist[gid][u])
        embed.add_field(name="[" + str(u + 1) + "] | [" + str(playerlist[gid][u]) + "] | [" + str(channellist[gid][u]) + "]", value="[%s](<%s>)" % (list_info.title, playlist[gid][u]), inline=False)

    await client.playlistEmbed[gid].edit(embed=embed)


#버튼 클릭 시 반응~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@buttons.click
async def Play(ctx): #재생버튼

    vc = get(client.voice_clients, guild=ctx.guild)
    gid = client.ids.index(ctx.guild.id)

    if not vc:
        await ctx.reply("제가 들어와 있어야 저를 조작하실 수 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "제가 들어와 있어야 저를 조작하실 수 있어요! 😥":
            await ctx.channel.purge(limit = 1)
        return

    if vc.is_paused():
        vc.resume()
        banner = discord.Embed(color=0x62c1cc)
        banner.set_image(url= playBannerPng)
        await client.topbanner[gid].edit(embed=banner)
        await ctx.reply("▶️")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "▶️":
            await ctx.channel.purge(limit = 1)
    else:
        await ctx.reply("이미 노래가 재생중이거나, 노래를 재생하지 않고 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "이미 노래가 재생중이거나, 노래를 재생하지 않고 있어요! 😥":
            await ctx.channel.purge(limit = 1)
    

@buttons.click
async def Pause(ctx): #정지버튼

    vc = get(client.voice_clients, guild=ctx.guild)
    gid = client.ids.index(ctx.guild.id)

    if not vc:
        await ctx.reply("제가 들어와 있어야 저를 조작하실 수 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "제가 들어와 있어야 저를 조작하실 수 있어요! 😥":
            await ctx.channel.purge(limit = 1)
        return

    if not vc.is_paused():
        vc.pause()
        banner = discord.Embed(color=0x62c1cc)
        banner.set_image(url= pauseBannerPng)
        await client.topbanner[gid].edit(embed=banner)
        await ctx.reply("⏸️")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "⏸️":
            await ctx.channel.purge(limit = 1)
    else:
        await ctx.reply("이미 일시정지되어 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "이미 일시정지되어 있어요! 😥":
            await ctx.channel.purge(limit = 1)


@buttons.click
async def Skip(ctx): #스킵버튼

    vc = get(client.voice_clients, guild=ctx.guild)

    if not vc:
        await ctx.reply("제가 들어와 있어야 저를 조작하실 수 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "제가 들어와 있어야 저를 조작하실 수 있어요! 😥":
            await ctx.channel.purge(limit = 1)
        return

    if vc.is_paused():
        vc.resume()

    if vc.is_playing():
        vc.stop()
        await ctx.reply("노래를 스킵했어요! :wink:")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "노래를 스킵했어요! :wink:":
            await ctx.channel.purge(limit = 1)


@buttons.click
async def Quit(ctx): #나가기버튼

    vc = get(client.voice_clients, guild=ctx.guild)
    gid = client.ids.index(ctx.guild.id)

    if not vc:
        await ctx.reply("제가 들어와 있어야 저를 조작하실 수 있어요! 😥")
        await asyncio.sleep(0.5)
        if (await ctx.channel.history(limit=1).flatten())[0].content == "제가 들어와 있어야 저를 조작하실 수 있어요! 😥":
            await ctx.channel.purge(limit = 1)
        return

    playerlist[gid].clear()
    playlist[gid].clear()
    channellist[gid].clear()

    vc.stop()
    await vc.disconnect()
    await ctx.reply("채널을 나갔어요! :wink:")
    await asyncio.sleep(0.5)
    await reset_gui(gid)
    if (await ctx.channel.history(limit=1).flatten())[0].content == "채널을 나갔어요! :wink:":
            await ctx.channel.purge(limit = 1)

@buttons.click
async def Init(ctx):

    wasInited = False
    guild = ctx.message.guild

    for channel in guild.channels:
        if type(channel) == discord.channel.TextChannel: #채널이 텍스트 채널인지 확인
            if channel.topic is not None and "[" + client.code + "]" in channel.topic: #노래옹재 채널 찾기
                await ctx.reply("이미 설정되어 있는 노래신청방이 있어요! 😥")
                await asyncio.sleep(2)
                if (await ctx.channel.history(limit=1).flatten())[0].content == "이미 설정되어 있는 노래신청방이 있어요! 😥":
                    await ctx.channel.purge(limit = 1)
                return

    name = "🎶 노래신청"
    topic = "[WJSB] 유튜브 링크를 보내어 노래를 재생해보세요 :grinning:"
    channel = await guild.create_text_channel(name = name, topic = topic)

    if not guild.id in client.ids:
        client.ids.append(guild.id)
        wasInited = False
    else:
        wasInited = True

    print(guild.name + " | " + str(guild.id) + " | " + str(client.ids.index(guild.id)) + " 목록 추가")

    #노래옹재 채널 초기 설정
    await channel.purge()
    client.channels.append(channel)

    pembed = discord.Embed(color=0x62c1cc)
    pembed.add_field(name="대기열 | QUEUE", value= "여긴 아직 아무것도 없어요.. 노래를 신청해봐요!", inline=True)
    pEmbed = await channel.send(embed=pembed)

    if wasInited == False:
        client.playlistEmbed.append(pEmbed)
    else:
        print(client.ids.index(guild.id))
        client.playlistEmbed[client.ids.index(guild.id)] = pEmbed

    banner = discord.Embed(color=0x62c1cc)
    banner.set_image(url= defaultBannerPng)
    tbanner = await channel.send(embed=banner)

    if wasInited == False:
        client.topbanner.append(tbanner)
    else:
        client.topbanner[client.ids.index(guild.id)] = tbanner

    embed = discord.Embed(color=0x62c1cc)
    embed.add_field(name=client.user.name + " (●'◡'●)", value= "[홈페이지](<%s>) | [개발자 페이지](<%s>) | [노래옹재 사용법](<%s>) | [후원](<%s>)" % (client.webPage, client.developerPage, client.howtoPage, client.donationPage), inline=False)
    embed.set_image(url= bigBannerPng)
    sembed = await channel.send(embed=embed)

    if wasInited == False:
        client.svembed.append(sembed)
    else:
        client.svembed[client.ids.index(guild.id)] = sembed

    await Buttons(channel)

    playlist.append([])
    playerlist.append([])
    channellist.append([])

    await ctx.reply("✅ 노래옹재 채널 설정을 완료했습니다.")
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#버튼 눌렀을 때 함수
async def Buttons(channel):
    await buttons.send(
        content = "", 
        channel = channel.id,
        components = [
            ActionRow([
                Button(
                    custom_id="Play",
                    emoji = {
                        "id": None,
                        "name": "▶️",
                        "animated": False
                        },
                    label="", 
                    style=ButtonType().Primary
                    ),
                Button(
                    custom_id="Pause",
                    emoji = {
                        "id": None,
                        "name": "⏸️",
                        "animated": False
                        },
                    label="", 
                    style=ButtonType().Primary
                ),
                Button(
                    custom_id="Skip",
                    emoji = {
                        "id": None,
                        "name": "⏩",
                        "animated": False
                        },
                    label="", 
                    style=ButtonType().Primary
                ),
                Button(
                    custom_id="Quit",
                    emoji = {
                        "id": None,
                        "name": "⛔",
                        "animated": False
                        },
                    label="", 
                    style=ButtonType().Danger
                )
            ])
        ]
    )

async def InitButton(channel):
    await buttons.send(
        content = "", 
        channel = channel.id,
        components = [
            ActionRow([
                Button(
                    custom_id="Init",
                    emoji = {
                        "id": None,
                        "name": "▶️",
                        "animated": False
                        },
                    label="초기 설정하기", 
                    style=ButtonType().Primary
                    )
            ])
        ]
    )
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

client.run(token)