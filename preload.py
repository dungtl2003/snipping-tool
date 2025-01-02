import pathlib
import os
import platform
import sys
import tempfile

env = os.environ.get("ENV")
if env == "dev":
    print("Running in development mode")


# remember to update the path when adding new modules
def resolve_path():
    curr_directory = str(pathlib.Path(__file__).parent.resolve())

    modules = [
        str(curr_directory),
        os.path.join(curr_directory, "fuctionalities"),
        os.path.join(curr_directory, "components"),
        os.path.join(curr_directory, "utils"),
    ]

    [sys.path.append(module) if module not in sys.path else None for module in modules]


def resolve_system_picture_path():
    os_name = platform.system()

    if os_name == "Windows":
        assert sys.platform == "win32"
        import winreg

        try:
            # Open the registry key for the user's known folder paths
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )

            # Query the value of the "My Pictures" key
            pictures_folder = winreg.QueryValueEx(registry_key, "My Pictures")[0]
            return pictures_folder
        except Exception as e:
            print(f"Error accessing registry: {e}")
            return os.path.join(
                os.environ["USERPROFILE"], "Pictures"
            )  # Fallback to default path

    elif os_name == "Linux":
        user_dirs_file = os.path.expanduser("~/.config/user-dirs.dirs")

        if os.path.exists(user_dirs_file):
            with open(user_dirs_file, "r") as file:
                for line in file:
                    if "XDG_PICTURES_DIR" in line:
                        # Extract the custom path
                        path = line.split("=")[1].strip().strip('"')
                        # Replace $HOME with the actual home directory
                        home_directory = os.environ.get(
                            "HOME", ""
                        )  # Get the value of $HOME
                        path = path.replace("$HOME", home_directory)
                        # If needed, expand any remaining ~ to the full home directory path
                        path = os.path.expanduser(path)
                        return path
        # Fallback to default Pictures folder
        return os.path.join(os.environ["HOME"], "Pictures")
    else:
        raise Exception(f"Unsupported OS: {os_name}")


def resolve_system_video_path():
    os_name = platform.system()

    if os_name == "Windows":
        assert sys.platform == "win32"
        import winreg

        try:
            # Open the registry key for the user's known folder paths
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )

            # Query the value of the "My Video" key
            video_folder = winreg.QueryValueEx(registry_key, "My Video")[0]
            return video_folder
        except Exception as e:
            print(f"Error accessing registry: {e}")
            return os.path.join(
                os.environ["USERPROFILE"], "Videos"
            )  # Fallback to default path

    elif os_name == "Linux":
        user_dirs_file = os.path.expanduser("~/.config/user-dirs.dirs")

        if os.path.exists(user_dirs_file):
            with open(user_dirs_file, "r") as file:
                for line in file:
                    if "XDG_VIDEOS_DIR" in line:
                        # Extract the custom path
                        path = line.split("=")[1].strip().strip('"')
                        # Replace $HOME with the actual home directory
                        home_directory = os.environ.get("HOME", "")
                        path = path.replace("$HOME", home_directory)
                        # If needed, expand any remaining ~ to the full home directory path
                        path = os.path.expanduser(path)
                        return path
        # Fallback to default Pictures folder
        return os.path.join(os.environ["HOME"], "Videos")
    else:
        raise Exception(f"Unsupported OS: {os_name}")


def resolve_app_data_path():
    os_name = platform.system()

    if os_name == "Windows":
        return os.environ["LOCALAPPDATA"]
    elif os_name == "Linux":
        return os.path.join(os.environ["HOME"], ".local", "share")
    else:
        raise Exception(f"Unsupported OS: {os_name}")


def resolve_cred_path(app_data_path: str, app_name: str, root_dir: str):
    if env == "dev":
        return (
            os.path.join(root_dir, "credentials.json"),
            os.path.join(root_dir, "token.json"),
        )
    else:
        return (
            os.path.join(app_data_path, app_name, "credentials.json"),
            os.path.join(app_data_path, app_name, "token.json"),
        )


resolve_path()

APP_NAME = "Becap"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ICON_DIR = os.path.join(ASSETS_DIR, "icons")
ANIMATION_DIR = os.path.join(ASSETS_DIR, "animations")

# Create a temporary folder for 'becap'
TEMP_DIR = os.path.join(tempfile.gettempdir(), APP_NAME)
print(f"Creating temporary directory at {TEMP_DIR}")
os.makedirs(TEMP_DIR, exist_ok=True)

# Get system paths
SYSTEM_PICTURE_PATH = resolve_system_picture_path()
SYSTEM_VIDEO_PATH = resolve_system_video_path()
APP_DATA_PATH = resolve_app_data_path()

CRED_PATH, TOKEN_PATH = resolve_cred_path(APP_DATA_PATH, APP_NAME, ROOT_DIR)
BECAP_PICTURE_PATH = os.path.join(SYSTEM_PICTURE_PATH, APP_NAME)
BECAP_VIDEO_PATH = os.path.join(SYSTEM_VIDEO_PATH, APP_NAME)
BECAP_CLIPBOARD_MANAGER_PATH = os.path.join(
    APP_DATA_PATH, APP_NAME, "clipboard_manager"
)

# Create the 'becap' folder in the system path
print(f"Creating app picture folder at {BECAP_PICTURE_PATH}")
os.makedirs(BECAP_PICTURE_PATH, exist_ok=True)
print(f"Creating app video folder at {BECAP_VIDEO_PATH}")
os.makedirs(BECAP_VIDEO_PATH, exist_ok=True)
print(f"Creating app clipboard manager folder at {BECAP_CLIPBOARD_MANAGER_PATH}")
os.makedirs(BECAP_CLIPBOARD_MANAGER_PATH, exist_ok=True)
