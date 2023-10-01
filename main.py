from __future__ import unicode_literals
import cv2
import os
import numpy as np
import re
import shutil
import sys
import youtube_dl

VIDEO_DOWNLOAD_ROOT = "raw"
OUTPUT_ROOT = "output"
DEFAULT_SAMPLE_RATE = 24
IMAGE_DIFFERENCE_RATE = 0.30

def download_video(url, video_path):
    print("Downloading %s" % url)
    ydl_opts = {
        'outtmpl': str(video_path)
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_frames(video_path, videoname, sample_rate=DEFAULT_SAMPLE_RATE):
    output_img_dir = os.path.join(OUTPUT_ROOT, videoname)
    prepare_output_dir(output_img_dir)

    video = cv2.VideoCapture(video_path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = 0
    found = False
    prev_frame = None
    output_filecount = 0
    while not found and start_frame < frame_count:
        found, prev_frame = video.read()
        start_frame += sample_rate

    save_image(output_img_dir, prev_frame, output_filecount)

    if found:
        frame_size = prev_frame.size
        for i in range(start_frame, frame_count):
            found, curr_frame = video.read()
            if found and i % sample_rate == 0:
                if are_frames_same(prev_frame, curr_frame, frame_size):
                    output_filecount += 1
                    save_image(output_img_dir, prev_frame, output_filecount)

                prev_frame = curr_frame

def prepare_output_dir(output_img_dir):
    if os.path.exists(output_img_dir):
        shutil.rmtree(output_img_dir)
    os.mkdir(output_img_dir)

def save_image(output_img_dir, frame, output_filecount):
    image_path = os.path.join(output_img_dir, "%04d.jpg" % output_filecount)
    cv2.imwrite(image_path, frame)

def are_frames_same(prev_frame, curr_frame, frame_size):
    frame_diff = curr_frame - prev_frame
    frame_delta = np.abs(np.sum(frame_diff) / 256.0)
    diff_percentage = frame_delta / frame_size
    return diff_percentage > IMAGE_DIFFERENCE_RATE



url = input("Video url: ")
videoname = re.sub(r'\W+', '_', url)

video_path = os.path.join(VIDEO_DOWNLOAD_ROOT, videoname)
output_folder = os.path.join(OUTPUT_ROOT, videoname)

if not os.path.exists(video_path):
    download_video(url, video_path)
else:
    print("Already downloaded: %s" % url)

extract_frames(video_path, videoname)


