import os

import psutil


class FancyUtilsClass:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.memory_usage = 0
        self.virtual_memory_usage = 0

    def print_memory_usage(self):
        mem_info = self.process.memory_info()
        usage = f"{mem_info.rss / (1024 * 1024 * 1024):.2f}"
        if self.memory_usage != usage:
            self.memory_usage = usage
            print(self.get_memory_message())

    def get_memory_message(self):
        return f"Memory usage: {self.memory_usage} GB"
