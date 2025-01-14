# snipping-tool

A simple snipping tool for Linux.

## Table of contents

- [Features](#features)
- [Installation](#installation)
    - [Linux](#linux)
    - [Windows](#windows)
- [For developers](#for-developers)
- [Usage](#usage)

### Features

- Take a screenshot of a selected area or the whole screen.
- Copy the screenshot to the clipboard.
- Have its own clipboard history.
- Color picker.
- Blur.
- Draw on the screenshot.
- Record video of the selected area (including audio).
- Save the screenshot/video to a file.
- Have shortcuts for almost all features.
- Upload the screenshot/video to google drive.

### Installation

#### Linux

Warning: Currently, this app only supports on Xorg display server. The Wayland display server is not supported yet.

Pre-requisite:
- You need to have python 3.10 installed on your machine. You can download it [here](https://www.python.org/downloads/).

Clone this repo:
``` bash
git clone git@github.com:dungtl2003/snipping-tool.git
```

Run the following command in the terminal:

``` bash
make install_linux
```

Uninstall the app:

``` bash
make uninstall_linux
```

#### Windows

Pre-requisite:
- You need to have python 3.10 installed on your machine. You can download it [here](https://www.python.org/downloads/).

Clone this repo:
``` bash
git clone git@github.com:dungtl2003/snipping-tool.git
```

Run the following command in the terminal:

``` bash
make install_windows
```

### For developers

1. Create a virtual environment:
``` bash
python -m venv venv
```

2. Activate the virtual environment:
``` bash
source venv/bin/activate
```

3. Install needed packages:
``` bash
pip install -r requirements.txt
```

4. Run the app:
``` bash
make run_dev
```

### Usage

#### Capture an image

- Choose the screenshot mode before capturing.
- Drag the mouse to select the area you want to take a screenshot of.
- Press instead of dragging to take a screenshot of the whole screen.
- Press any key to cancel taking a screenshot.
- You can press zoom in/out icon to zoom in/out the image or press on the zoom number to reset the zoom level to 100%.

#### Record a video

- Choose the video mode before capturing.
- Drag the mouse to select the area you want to record.
- Press instead of dragging to record the whole screen.
- Press any key to cancel recording.
- When recording, you can drag the timer button to move it around using the right mouse button.
- Left-click on the timer button to pause/resume the recording.


#### Play the video

- Only available when you have just recorded a video.
- Press the play button to toggle play/pause.
- Drag the progress bar to seek the video.
- Press the left/right arrow keys to seek the video by 5 seconds.

#### Blur

- Only available when you have just taken a screenshot.
- Choose blur option.
- Drag the mouse to select the area you want to blur.
- Press blur option again to cancel blurring.

#### Color picker

- Only available when you have just taken a screenshot.
- Choose color picker option.
- Click on the image to pick the color hex code from that pixel.
- Press color picker option again to cancel picking color.

#### Draw on the screenshot

- Only available when you have just taken a screenshot.
- Choose draw option.
- Choose the color.
- Left-click and drag the mouse to draw on the image.
- Right-click to toggle the color selection dialog.
- Press draw option again to cancel drawing.

#### Save the screenshot/video

- Press the save button to save the screenshot/video to a file.
- This will save the screenshot/video to the default directory. The default image directory is `/path-to-your-default-image-directory/becap/` and the default video directory is `/path-to-your-default-video-directory/becap/`. Image format is `png` and video format is `mp4`.

#### Copy the screenshot to the clipboard

- Press the copy button to copy the screenshot to the clipboard.
- The screenshot will be copied as an image.

#### Upload the screenshot/video to google drive

- Press the upload button to upload the screenshot/video to google drive.
- You need to authenticate with your google account before uploading.
- Select the path to save the screenshot/video on google drive.
- The screenshot/video will be uploaded to the selected path.

#### Clipboard history

- Each time you copy a screenshot, it will be added to the clipboard history.
- Press `Ctrl + Alt + Up` to show the clipboard history.
- Press `Ctrl + Alt + Up` again to hide the clipboard history.
- Left-click on an item in the clipboard history to copy it to the clipboard.
- The clipboard history will contain at most 20 items and will be saved when you close the app so that you can access it later.
- Right-click on an item in the clipboard history to copy it to the clipboard and remove it from the history.

#### Shortcuts

| Shortcut | Description |
| --- | --- |
| `Tab` | Switch between the screenshot and video recording mode. |
| `Ctrl + N` | Take a screenshot of a selected area. |
| `Ctrl + S` | Save the screenshot/video to a file. |
| `Ctrl + C` | Copy the screenshot to the clipboard. |
| `Ctrl + Alt + Up` | Toggle the clipboard history. |
| `Ctrl + Z` | Undo the last editing action. |
| `Ctrl + Y` | Redo the last editing action. |
| `Ctrl + P` | Toggle the color picker. |
| `Ctrl + B` | Toggle the blur. |
| `Ctrl + D` | Toggle the draw. |
| `Ctrl + U` | Upload the screenshot/video to google drive. |
| `Ctrl + Scroll` | Zoom in/out the image. |
