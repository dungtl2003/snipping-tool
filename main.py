import sys
import os
import multiprocessing

from components.clipboard_manager import run_clipboard_manager
from components.snipper_window import run_snipper_window
from preload import ICON_DIR
from globals import kill_all_processes, processes

import preload as _  # noqa: F401

APP_ICON = os.path.join(ICON_DIR, "scissors.svg")


def error_handler(etype, value, tb):
    print(f"An error occurred: {value}")
    print("Killing all processes")
    kill_all_processes()
    sys.exit(1)


if __name__ == "__main__":
    if not (3, 10) <= sys.version_info < (3, 11):
        sys.exit(
            "This project requires Python >= 3.10 and < 3.11. Please update your Python version."
        )

    sys.excepthook = error_handler  # redirect std error

    try:
        snipper_window_process = multiprocessing.Process(target=run_snipper_window)
        clipboard_manager_process = multiprocessing.Process(
            target=run_clipboard_manager
        )

        processes.append(clipboard_manager_process)
        processes.append(snipper_window_process)

        print("Starting snipper window process")
        snipper_window_process.start()
        print("Starting clipboard manager process")
        clipboard_manager_process.start()

        snipper_window_process.join()
        processes.remove(snipper_window_process)

        print("Snipper window process has ended. Killing all processes")
        kill_all_processes()
    except Exception as e:
        print(f"Error on main process: {e}")
        kill_all_processes()

        sys.exit(1)
