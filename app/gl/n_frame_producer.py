import threading
import time

import numpy as np


class CancellationSignal:
    def __init__(self):
        self._canceled = False

    def emit(self):
        self._canceled = True

    def is_canceled(self):
        return self._canceled


class FrameData:
    def __init__(self, buffer_width, buffer_height, visible_grid_part):
        self.buffer_width = buffer_width
        self.buffer_height = buffer_height
        self.visible_grid_part = visible_grid_part
        self.data = None
        self.cancellation_signal = CancellationSignal()
        self._thread = threading.Thread(target=self._load)
        self._thread.start()
        self.ready = False

    def _load(self):
        self.data = np.full((self.buffer_width, self.buffer_height), fill_value=-1, dtype=np.float32)
        self.visible_grid_part.update_scene_buffer_directly(self.data, self.cancellation_signal)
        self.ready = True

    def cancel(self):
        self.cancellation_signal.emit()


class NFrameProducer:
    def __init__(self, n_buffer):
        self._n_buffer = n_buffer
        self._current_frame = None

    def create_frame(self, visible_grid_part):
        print("Creating new frame", self._n_buffer.buffer_width, self._n_buffer.buffer_height)
        if self._current_frame is not None:
            self._current_frame.cancel()
        self._current_frame = FrameData(self._n_buffer.buffer_width, self._n_buffer.buffer_height, visible_grid_part)

    def get_current_frame(self):
        return self._current_frame
