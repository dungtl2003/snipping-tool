import pathlib
import os
import sys
import tempfile


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


print("Preloading modules")
resolve_path()

print("Setting up global variables")
APP_NAME = "becap"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ICON_DIR = os.path.join(ASSETS_DIR, "icons")

# Create a temporary folder for 'becap'
TEMP_DIR = os.path.join(tempfile.gettempdir(), APP_NAME)
print(f"Creating temporary directory at {TEMP_DIR}")
os.makedirs(TEMP_DIR, exist_ok=True)
