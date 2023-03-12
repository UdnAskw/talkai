import json
import requests
from pathlib import Path
from urllib.parse import urljoin


BASE_URL = 'http://localhost:50021'


def gen_query(text: str) -> dict:
    params = {'text': text, 'speaker': 2}
    res = requests.post(
        urljoin(BASE_URL, 'audio_query'),
        params=params
    )
    return res.json()


def gen_synthesis(audio_query_response: dict) -> bytes:
    params = {'speaker': 2}
    headers = {'content-type': 'application/json'}
    audio_query_response_json = json.dumps(audio_query_response)
    res = requests.post(
        'http://localhost:50021/synthesis',
        data=audio_query_response_json,
        params=params,
        headers=headers
    )
    return res.content


def main():
    query = post_audio_query('今日のご飯はやきそばです。しかし、私は焼きそばが嫌いです。')
    audio = post_synthesis(query)
    with open(Path(f'voice.mp3'), "wb") as f:
       f.write(audio)


if __name__ == '__main__':
    main()