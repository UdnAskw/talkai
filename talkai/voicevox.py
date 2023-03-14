import json
import requests
from pathlib import Path
from urllib.parse import urljoin
from dataclasses import dataclass, field
from speaker import ALL_SPEAKERS


@dataclass
class Voicevox:
    speaker_name: str = field(default='ずんだもん')
    speaker_style: str = field(default='ノーマル')
    speed_scale: float = field(default=1.0)
    pitch_scale: float = field(default=0.0)
    intonation_scale: float = field(default=1.0)
    volume_scale: float = field(default=1.0)
    base_url: str = field(default='http://localhost:50021')

    SPEAKER_MAPPING = ALL_SPEAKERS

    @classmethod
    @property
    def all_speakers(cls):
        all = cls.SPEAKER_MAPPING
        return [f'{n} {s}' for n in all for s in all[n]]

    @classmethod
    @property
    def all_speaker_id(cls):
        all = cls.SPEAKER_MAPPING
        return sorted([n[s] for n in all.values() for s in n])

    @property
    def _speaker_id(self) -> int:
        try:
            return self.SPEAKER_MAPPING[self.speaker_name][self.speaker_style]
        except KeyError:
            raise self.InvalidSpeakerError

    def _gen_query(self, text) -> dict:
        params = {'text': text, 'speaker': self._speaker_id}
        query = requests.post(
            urljoin(self.base_url, 'audio_query'),
            params=params
        ).json()
        additional_query = {
            'speedScale': self.speed_scale,
            'pitchScale': self.pitch_scale,
        }
        query.update(additional_query)
        return query 

    def _gen_voice(self, query: dict) -> bytes:
        params = {'speaker': self._speaker_id}
        headers = {'content-type': 'application/json'}
        query = json.dumps(query)
        res = requests.post(
            urljoin(self.base_url, 'synthesis'),
            data=query,
            params=params,
            headers=headers
        )
        return res.content

    def speak(self, text) -> bytes:
        return self._gen_voice(self._gen_query(text))

    class InvalidSpeakerError(Exception):
        pass


def main():
    vv = Voicevox()
    audio = vv.speak('これはテスト音声です。')
    with open(Path(f'test.mp3'), "wb") as f:
       f.write(audio)


if __name__ == '__main__':
    main()



