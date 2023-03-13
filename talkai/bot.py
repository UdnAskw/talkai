from io import BytesIO
from pathlib import Path
from datetime import datetime
import discord
from discord import Option
import whisper
import chatgpt
import voicevox
from config import DISCORD_BOT_TOKEN


bot = discord.Bot()
setting = discord.SlashCommandGroup("setting", "設定コマンド")
voice = setting.create_subgroup("voice", "VOICEVOXの設定")
bot.add_application_command(setting)
messages = [
    {'role': 'system', 'content': '口語で話して'},
]
vv = voicevox.Voicevox()


@bot.slash_command(description='ボイスチャンネルに参加')
async def join(ctx):
    if ctx.author.voice is None:
        embed = discord.Embed(
            title='Error',
            description='あなたがボイスチャンネルに参加していません',
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    try:
        await ctx.author.voice.channel.connect()
    except:
        embed = discord.Embed(
            title='Error',
            description='ボイスチャンネルに接続できません',
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            description='ボイスチャンネルに接続しました',
            color=discord.Colour.green()
        )
    finally:
        await ctx.respond(embed=embed)


@bot.slash_command(description='ボイスチャンネルから切断')
async def leave(ctx):
    if ctx.guild.voice_client is None:
        embed = discord.Embed(
            title='Error',
            description='ボイスチャンネルに接続していません',
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.guild.voice_client.disconnect()
        embed = discord.Embed(
            description='ボイスチャンネルから切断しました',
            color=discord.Colour.green()
        )
        await ctx.respond(embed=embed)


@voice.command(description='ボイスのキャラクター変更')
async def character(
    ctx,
    name: Option(
        str,
        description='キャラクター名を指定'
    ),
    style: Option(
        str,
        description='音声スタイルを指定'
    )
):
    if f'{character} {style}' in vv.all_speakers:
        vv.speaker_name = character
        vv.speaker_style = style
        embed = discord.Embed(
            description=f'ボイスを"{character} {style}"に変更しました',
            color=discord.Colour.green()
        )
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(
            title='Error',
            description=f'そのようなボイスは存在しません',
            color=discord.Colour.red()
        )
        await ctx.respond(embed=embed)   


@setting.command()
async def advanced(
    ctx,
    speed: Option(
        float, required=False, description='話速',
        min_value=0.5, max_value=2.0, default=vv.speed_scale,
    ),
    pitch: Option(
        float, required=False, description='音高', default=vv.pitch_scale,
    ),
    intonation: Option(
        float, required=False, description='抑揚', default=vv.intonation_scale,
    ),
    volume: Option(
        float, required=False, description='音量', default=vv.volume_scale,
    ),
):
    vv.speed_scale = speed
    vv.pitch_scale = pitch
    vv.intonation_scale = intonation
    vv.volume_scale = volume
    embed = discord.Embed(
            description=f'ボイス設定を変更しました',
            color=discord.Colour.green()
        )
    await ctx.respond(embed=embed)
 

@bot.slash_command(description='ボイスを一覧を表示')
async def voice_list(ctx):
    embed = discord.Embed(
        description='\n'.join(vv.all_speakers),
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
    start = datetime.now()
    for user_id, audio in sink.audio_data.items():
        audio_data = BytesIO(audio.file.getbuffer())
        audio_data.name = 'voice.wav'
        print(f'GET_WAV: {start - datetime.now()}')
        

        text = whisper.transcrible(audio_data)
        print(f'GET_TXT: {start - datetime.now()}')

        messages += [{'role': 'user', 'content': text}]
        res = chatgpt.chat(messages)
        print(res)
        messages += [{'role': 'assistant', 'content': res}]
        print(f'GET_GPT: {start - datetime.now()}')

        vb_audio = vv.speak(res)
        print(f'GET_VOX: {start - datetime.now()}')
        a = BytesIO(vb_audio)
        voice_client.play(
            discord.FFmpegPCMAudio(a, pipe=True)
        )


bot.run(DISCORD_BOT_TOKEN)