# Fisch Bot

An autoclicker for the Roblox game Fisch that automates the fishing process.

## Features

- Automatically casts the fishing line
- Detects and clicks on "Shake" icons
- Handles the fish catching minigame by keeping the fish within the target area
- Monitors the catching bar progress

## Requirements

- Python 3.8 or higher
- Windows OS
- Roblox game "Fisch" running in windowed mode

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Open the Roblox game "Fisch" in windowed mode
2. Run the bot:

```bash
python fisch_bot.py
```

3. The bot will start automatically:
   - It will cast the line
   - Look for and click on shake icons
   - Handle the fish catching minigame
4. Press 'q' to quit the bot

## Safety Features

- PyAutoGUI failsafe: Move your mouse to any corner of the screen to stop the bot
- Click cooldown to prevent rapid clicking
- Easy quit with 'q' key

## Notes

- Make sure the game window is visible and not minimized
- The bot uses screen capture and image processing, so it may need adjustments based on your screen resolution
- You may need to adjust the thresholds in the code if the detection is not working properly
