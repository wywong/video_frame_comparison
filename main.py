from __future__ import unicode_literals
import argparse
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
DEFAULT_DIFFERENCE_THRESHOLD = 0.01

def download_video(url, video_path):
    print("Downloading %s" % url)
    ydl_opts = {
        'outtmpl': str(video_path)
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

class ImageExtractor:
    def __init__(self,
                 url,
                 debug_enabled=False,
                 sample_rate=DEFAULT_SAMPLE_RATE,
                 image_difference_threshold=DEFAULT_DIFFERENCE_THRESHOLD):
        videoname = re.sub(r'\W+', '_', url)
        self.video_path = os.path.join(VIDEO_DOWNLOAD_ROOT, videoname)
        self.output_img_dir = os.path.join(OUTPUT_ROOT, videoname)

        self.debug_enabled = debug_enabled
        self.sample_rate = sample_rate
        self.image_difference_threshold = image_difference_threshold

        self.output_filecount = 0

    def extract_frames(self):
        self.prepare_output_dir()

        video = cv2.VideoCapture(self.video_path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        start_frame = 0
        found = False
        prev_frame = None
        while not found and start_frame < frame_count:
            found, prev_frame = video.read()
            start_frame += self.sample_rate

        if not found:
            # no valid frames
            return None

        img_name = self.output_image_name()
        self.save_image(prev_frame, img_name)

        self.frame_size = prev_frame.size
        for i in range(start_frame, frame_count):
            found, curr_frame = video.read()
            if found and i % self.sample_rate == 0:
                if self.are_frames_same(prev_frame, curr_frame):
                    self.output_filecount += 1
                    img_name = self.output_image_name()
                    self.save_image(curr_frame, img_name)
                    if self.debug_enabled:
                        img_delta = self.image_shadow(prev_frame, curr_frame)
                        self.save_image(img_delta, "SHADOW_%s" % img_name)
                prev_frame = curr_frame

    def prepare_output_dir(self):
        if os.path.exists(self.output_img_dir):
            shutil.rmtree(self.output_img_dir)
        os.mkdir(self.output_img_dir)

    def output_image_name(self):
        return "%04d.jpg" % self.output_filecount

    def save_image(self, frame, img_name):
        image_path = os.path.join(self.output_img_dir, img_name)
        cv2.imwrite(image_path, frame)

    def are_frames_same(self, prev_frame, curr_frame):
        img_delta = self.image_shadow(prev_frame, curr_frame)
        ret, threshold = cv2.threshold(img_delta, 200, 255, cv2.THRESH_BINARY_INV)

        num_zeros = np.count_nonzero(threshold == 0)
        percent_pixels_different = 3.0 * num_zeros / self.frame_size

        return percent_pixels_different > self.image_difference_threshold

    def image_shadow(self, prev_frame, curr_frame):
        diff = cv2.absdiff(prev_frame, curr_frame)
        return cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

parser = argparse.ArgumentParser()
parser.add_argument("--debug",
                    help="Enable debug output",
                    action="store_true")
parser.add_argument("--url",
                    help="The url of the video we want to process.",
                    type=str)
parser.add_argument("--samplerate",
                    help="The number of frames we want to increment by when comparing",
                    type=int,
                    default=DEFAULT_SAMPLE_RATE)
args = parser.parse_args()

url = args.url
image_extractor = ImageExtractor(url,
                                 debug_enabled=args.debug,
                                 sample_rate=args.samplerate)

video_path = image_extractor.video_path

if not os.path.exists(video_path):
    download_video(url, video_path)
else:
    print("Already downloaded: %s" % url)

image_extractor.extract_frames()


