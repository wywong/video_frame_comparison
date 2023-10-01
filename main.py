from __future__ import unicode_literals
import os
import re
import sys
import youtube_dl

VIDEO_DOWNLOAD_ROOT = "raw"

def download_video(url, video_path):
    print("Downloading %s" % url)
    ydl_opts = {
        'outtmpl': str(video_path)
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    pass


url = input("Video url: ")
filename = re.sub(r'\W+', '_', url)

video_path = os.path.join(VIDEO_DOWNLOAD_ROOT, filename)

if not os.path.exists(video_path):
    download_video(url, video_path)
else:
    print("Already downloaded: %s" % url)


