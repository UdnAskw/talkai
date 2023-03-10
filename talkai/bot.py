import os
from pathlib import Path
from datetime import datetime
import discord

from config import DISCORD_BOT_TOKEN


bot = discord.Bot()


@bot.slash_command(description="ボイスチャンネルに参加")
async def join(
    ctx,
):
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
            title="Success",
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
            title="Success",
            description="ボイスチャンネルから切断しました",
            color=discord.Colour.green()
            )
        await ctx.respond(embed=embed)


@bot.slash_command(description="録音を開始")
async def record(ctx):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(
            title="Error",
            description="ボイスチャンネルに接続していません",
            color=discord.Colour.red()
            )
        await ctx.respond(embed=embed)
    else:
        ctx.voice_client.start_recording(
            discord.sinks.MP3Sink(),
            finished_callback,
            ctx
            )
        embed = discord.Embed(
            title="Success",
            description="ボイスチャンネルの録音を開始しました",
            color=discord.Colour.green()
            )
        await ctx.respond(embed=embed)


@bot.slash_command(description="録音を停止します。")
async def record_stop(ctx):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(title="Error",
            description="ボイスチャンネルに接続していません",
            color=discord.Colour.red()
            )
        await ctx.respond(embed=embed)
    else:
        ctx.voice_client.stop_recording()
        embed = discord.Embed(
            title="Success",
            description="ボイスチャンネルの録音を停止しました",
            color=discord.Colour.green()
            )
        await ctx.respond(embed=embed)


async def finished_callback(sink, ctx):
    t = datetime.now().strftime('%Y%m%d%H%M%S')
    for user_id, audio in sink.audio_data.items():
        with open(Path(f'voice_{t}.mp3'), "wb") as f:
            f.write(audio.file.getbuffer())


bot.run(DISCORD_BOT_TOKEN)