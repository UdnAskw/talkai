import os
import time
import queue
import asyncio
from io import BytesIO
from pathlib import Path
from datetime import datetime
import discord
import whisper
import chatgpt
import voicevox
from config import DISCORD_BOT_TOKEN


bot = discord.Bot()
q = queue.Queue()
messages = [
    {"role": "system", "content": "口語で話して"},
]
vv = voicevox.Voicevox()


@bot.slash_command(description="ボイスチャンネルに参加")
async def join(ctx):
    if ctx.author.voice is None:
        embed = discord.Embed(
            title="Error",
            description="あなたがボイスチャンネルに参加していません",
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    try:
        await ctx.author.voice.channel.connect()
    except:
        embed = discord.Embed(
            title="Error",
            description="ボイスチャンネルに接続できません",
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            description="ボイスチャンネルに接続しました",
            color=discord.Colour.green()
        )
    finally:
        await ctx.respond(embed=embed)


@bot.slash_command(description="ボイスチャンネルから切断")
async def leave(ctx):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(
            title="Error",
            description="ボイスチャンネルに接続していません",
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            description="ボイスチャンネルから切断しました",
            color=discord.Colour.green()
        )
        await ctx.respond(embed=embed)


@bot.event
async def on_ready():
    print('bot started')


@bot.event
async def on_voice_state_update(member, before, after):
    vc = member.guild.voice_client
    if before.self_mute and not after.self_mute:
        print(f'{member} started talking')
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        audio_file = Path(f'voice_{member.id}_{now}.mp3').resolve()
        vc.start_recording(
            discord.sinks.WaveSink(),
            finished_callback,
            vc,
        )
        print('start recording')
    elif after.self_mute and not before.self_mute:
        print(f'{member} stopped talking')
        try:
            vc.stop_recording()
        except discord.sinks.RecordingException:
            pass
        else:
            print('stop recording')


async def finished_callback(sink, voice_client):
    global messages
    for user_id, audio in sink.audio_data.items():
        audio_data = BytesIO(audio.file.getbuffer())
        audio_data.name = 'voice.wav'

        text = whisper.transcrible(audio_data)
        print(f'user: {text}')

        messages += [{'role': 'user', "content": text}]
        res = chatgpt.chat(messages)
        print(res)
        messages += [{'role': 'assistant', "content": res}]

        vb_audio = vv.speak(res)
        a = BytesIO(vb_audio)
        print(f'TYPE: {type(a)}')
        voice_client.play(
            discord.FFmpegPCMAudio(a, pipe=True)
        )


bot.run(DISCORD_BOT_TOKEN)