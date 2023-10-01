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
DEBUG_ON = True

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

    img_name = output_image_name(output_filecount)
    save_image(output_img_dir, prev_frame, img_name)

    if found:
        frame_size = prev_frame.size
        for i in range(start_frame, frame_count):
            found, curr_frame = video.read()
            if found and i % sample_rate == 0:
                if are_frames_same(prev_frame, curr_frame, frame_size):
                    output_filecount += 1
                    img_name = output_image_name(output_filecount)
                    save_image(output_img_dir, prev_frame, img_name)
                    if DEBUG_ON:
                        img_delta = image_shadow(prev_frame, curr_frame)
                        save_image(output_img_dir, img_delta, "SHADOW_%s" % img_name)
                    prev_frame = curr_frame

def prepare_output_dir(output_img_dir):
    if os.path.exists(output_img_dir):
        shutil.rmtree(output_img_dir)
    os.mkdir(output_img_dir)

def output_image_name(output_filecount):
    return "%04d.jpg" % output_filecount

def save_image(output_img_dir, frame, img_name):
    image_path = os.path.join(output_img_dir, img_name)
    cv2.imwrite(image_path, frame)

def are_frames_same(prev_frame, curr_frame, frame_size):
    frame_diff = curr_frame - prev_frame
    frame_delta = np.abs(np.sum(frame_diff) / 255.0)
    diff_percentage = frame_delta / frame_size
    return diff_percentage > IMAGE_DIFFERENCE_RATE

def image_shadow(prev_frame, curr_frame):
    diff = 255 - cv2.absdiff(prev_frame, curr_frame)
    return cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)


url = input("Video url: ")
videoname = re.sub(r'\W+', '_', url)

video_path = os.path.join(VIDEO_DOWNLOAD_ROOT, videoname)
output_folder = os.path.join(OUTPUT_ROOT, videoname)

if not os.path.exists(video_path):
    download_video(url, video_path)
else:
    print("Already downloaded: %s" % url)

extract_frames(video_path, videoname)


