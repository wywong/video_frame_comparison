## Video frame extraction

Extracts frames from a video and ignores consecutive frames that are the same.

## Setup

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install --upgrade pip`

`pip install -r requirements.txt`

## Usage

Run the command

`python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`

The raw video will be downloaded and saved to the `raw/` folder.

The consecutive frames that are considered different will be saved to the `output/` folder.

