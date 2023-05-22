import glob
import datetime
import random
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import settings as s


def combineAll():
    video_files_path = s.video_save_dir

    video_file_list = glob.glob(f"{video_files_path}/*.mp4")

    loaded_video_list = []

    for video in video_file_list:
        print(f"Adding video file:{video}")
        vidResolution = VideoFileClip(video)
        vwidth = vidResolution.w
        vheight = vidResolution.h

        # Resizing the video to match resolution
        while vwidth < 1920 and vheight < 1080:
            vwidth += 1
            vheight += 1

        loaded_video_list.append(VideoFileClip(video).resize((vwidth, vheight)))

    random.shuffle(loaded_video_list)
    vidNum = len(loaded_video_list)
    print('shuffled list' + str(vidNum))

    if s.intro:
        print('Adding intro...')
        loaded_video_list.insert(0, VideoFileClip(s.intro_file_path))
        print('Intro Added')
    else:
        pass

    final_clip = concatenate_videoclips(loaded_video_list, method='compose')

    merged_video_name = ('Final-' + str(datetime.date.today()))

    final_clip.write_videofile(s.final_video_save_dir + f"{merged_video_name}.mp4")
    final_clip.close()
    final_clip.close()
    final_clip.close()
