from pathlib import Path
import config

import openai


with open(Path("voice.mp3"), "rb") as f:
    transcription = openai.Audio.transcribe("whisper-1", f, language='ja')

print(transcription['text'])