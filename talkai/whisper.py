from pathlib import Path
import openai
import config


def transcrible(voice_data) -> str:
    transcription = openai.Audio.transcribe("whisper-1", voice_data, language='ja')
    return transcription['text']