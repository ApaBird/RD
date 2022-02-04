import discord
from discord.ext import commands
from conf import settings
import json
import requests
from pytube import YouTube
import os
from mutagen.mp4 import MP4
import asyncio

bot = commands.Bot(command_prefix=settings['prefix'], intents=discord.Intents.all())
play_next = True
if "queue" in os.listdir():
    print("Ok...")
else:
    os.mkdir("queue")

if "video_dl" in os.listdir():
    print("Ok...")
else:
    os.mkdir("video_dl")

@bot.command(aliases=["j"])
async def join(ctx):
    print("Start connect...")
    server = ctx.guild
    channel = ctx.author.voice.channel
    voice = discord.utils.get(bot.voice_clients, guild=server)

    if voice and voice.is_connected():
        if voice.channel != channel.name:
            await voice.move_to(channel)
            await ctx.send(embed=discord.Embed(title=f"RD тут {channel.name}", color=0xaf7ac5))
            print("Connect on " + channel.name)
        print(voice.channel)
    else:
        await channel.connect()
        await ctx.send(embed=discord.Embed(title=f"RD тут {channel.name}", color=0xaf7ac5))
        print("Connect on " + channel.name)


@bot.command()
async def leave(ctx):
    print("Disconnect")
    server = ctx.guild
    channel = ctx.author.voice.channel

    voice = discord.utils.get(bot.voice_clients, guild=server)

    if voice:
        await voice.disconnect()
        await ctx.send(embed=discord.Embed(title="Удачи", color=0xaf7ac5))


@bot.command(aliases=["p"])
async def play(ctx, arg):
    channel = ctx.author.voice.channel
    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    print(voice)

    # Подключение к гс-чату если не подключен
    if voice == None:
        print("Now join")
        await join(ctx)
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    elif voice.channel != channel.name:
        print("Now join")
        await join(ctx)
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Загрузка музыки и добавление в очередь
    dl = YouTube(arg)
    raw_song = dl.streams.get_audio_only().download(output_path="video_dl")
    print(raw_song)
    print(raw_song.split('\\'))
    queue = os.listdir(path="queue")
    new_file = raw_song.rsplit('\\', 2)[0] + "queue\\" + str(max(queue, key=len)[:-4] + "b" if len(queue) != 0 else "b") + ".mp3"
    print(new_file)
    os.rename(os.path.join(raw_song), os.path.join(new_file))

    # Воспроизведение музыки
    queue = os.listdir(path="queue")
    print(queue)
    if not voice.is_playing():
        try:
            voice.play(discord.FFmpegPCMAudio(executable="ffmpeg\\bin\\ffmpeg.exe", source=os.path.join("queue\\" + queue[0])), after=lambda e: print(e))
            await ctx.send(embed=discord.Embed(title="Флексим под", color=0xaf7ac5, description=ctx.message.content))
            await asyncio.sleep(MP4("queue\\" + queue[0]).info.length + 1)
            await start_play(ctx)
        except Exception as e:
            await ctx.send(f"Возникла ошибка {e}")
            print(e)


@bot.command()
async def start_play(ctx):
    queue = os.listdir(path="queue")
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    os.remove("queue\\" + queue[0])
    if len(queue) > 1:
        try:
            await ctx.send(embed=discord.Embed(title="Флексим под", color=0xaf7ac5, description=ctx.message.content))
            voice.play(discord.FFmpegPCMAudio(executable="ffmpeg\\bin\\ffmpeg.exe", source=os.path.join("queue\\" + queue[1])), after=lambda e: print(e))
            play_next = True
            await asyncio.sleep(MP4("queue\\" + queue[1]).info.length + 1)
            if play_next:
                await start_play(ctx)
        except Exception as e:
            await ctx.send(f"Возникла ошибка {e}")
            print(e)

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        play_next = False
        await ctx.send(embed=discord.Embed(title="Конец танцам", color=0xaf7ac5))
        voice.stop()

@bot.command()
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        play_next = False
        voice.stop()
    await asyncio.sleep(1)
    await ctx.send(embed=discord.Embed(title="Хейтер", color=0xaf7ac5, description=ctx.author.mention))
    await start_play(ctx)


@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot.command()
async def bird(ctx):
    response = requests.get('https://some-random-api.ml/img/birb')
    json_data = json.loads(response.text)

    embed = discord.Embed(color=0xaf7ac5, title='Random Bird')
    embed.set_image(url=json_data['link'])
    await ctx.send(embed=embed)

bot.run(settings['token'])
