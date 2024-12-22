from multiprocessing import Process
from multiprocessing.managers import SyncManager


pids = []
processes = []


def kill_all_processes():
    for process in processes:
        if isinstance(process, Process):
            if process.is_alive():
                process.terminate()
        elif isinstance(process, SyncManager):
            process.shutdown()
