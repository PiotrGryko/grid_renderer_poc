import sounddevice as sd
import threading
from enum import Enum
import time


class PlaybackState(Enum):
    PLAYING = "playing"
    IDLE = "idle"


class AudioPlayer:
    def __init__(self):
        self.state = {}
        self.lock = threading.Lock()

    def play(self, id, audio_data, sampling_rate):
        # Ensure that each audio play request runs in its own thread
        thread = threading.Thread(target=self._play_audio, args=(id, audio_data, sampling_rate))
        thread.start()

    def _play_audio(self, id, audio_data, sampling_rate):
        with self.lock:
            self.state[id] = PlaybackState.PLAYING

        sd.play(audio_data, sampling_rate)
        sd.wait()

        with self.lock:
            self.state[id] = PlaybackState.IDLE

    def get_state(self, id):
        with self.lock:
            return self.state.get(id, PlaybackState.IDLE)
