from multiprocessing import Process
from multiprocessing.managers import SyncManager

import os
import signal


pids = []
processes = []


def kill_all_processes():
    for process in processes:
        if isinstance(process, Process):
            if process.is_alive():
                process.terminate()
        elif isinstance(process, SyncManager):
            process.shutdown()
        elif isinstance(process, int):  # process is a pid
            try:
                os.kill(process, signal.SIGTERM)
            except Exception as e:
                print(f"Error killing process {process}: {e}")
