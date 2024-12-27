# snipping-tool

A simple snipping tool for Linux and Windows.

## Table of contents

- [Features](#features)
- [Installation](#installation)
  - [Build from source](#build-from-source)
  - [Download the executable](#download-the-executable)
- [Usage](#usage)

### Features

- Take a screenshot of a selected area.
- Copy the screenshot to the clipboard.
- Have its own clipboard history.
- Color picker.
- Record video of the selected area (including audio).
- Save the screenshot/video to a file.
- Have shortcuts for almost all features.

### Installation

#### Build from source

You need to have python 3.10 installed on your machine.

1. Clone this repo:
``` bash
git clone git@github.com:dungtl2003/snipping-tool.git
```

2. Install needed packages:
``` bash
pip install -r requirements.txt
```

3. Run the app:
``` bash
python main.py
```

#### Download the executable

You can download the executable for Windows and Linux from the [releases](coming soon) page.

### Usage

- Press `Tab` to switch between the screenshot and video recording mode.
- Press `Ctrl + N` to take a screenshot of a selected area.
- Press `Ctrl + S` to save the screenshot/video to a file.
- Press `Ctrl + C` to copy the screenshot to the clipboard.
- Press `Ctrl + Alt + Up` to show the clipboard history. Press it again to hide it.
