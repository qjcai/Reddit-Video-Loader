import os
import re
import time
import requests
import praw
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm
import settings as s


# Reddit API
reddit = praw.Reddit(client_id=s.client_id,
                     client_secret=s.client_secret,
                     username=s.username,
                     password=s.password,
                     user_agent=s.user_agent)


def download_video(url, filename):
    response = requests.get(url)
    total_size = int(response.headers.get('Content-Length', 0))
    progress_bar = tqdm(total=total_size)
    with open(filename, 'wb') as f:
        for data in response.iter_content(chunk_size=2000):
            progress_bar.update(len(data))
        f.write(response.content)
        f.close()
        f.close()


def download_audio(url, fileaudio):
    response = requests.get(url)
    total_size = int(response.headers.get('Content-Length', 0))
    progress_bar = tqdm(total=total_size)
    with open(fileaudio, 'wb') as f:
        for data in response.iter_content(chunk_size=2000):
            progress_bar.update(len(data))
        f.write(response.content)
        f.close()
        f.close()


def search_and_download():
    save_directory = s.video_save_dir
    subreddit_names = s.subreddit

    max_videos = s.max_video_per_subreddit
    time.sleep(5)
    for subreddit_name in subreddit_names:
        print('Searching in ' + subreddit_name)
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.rising(limit=None):
            # Check if submission is a video, gif, upload time, and if is nsfw
            if submission.is_video and not submission.media['reddit_video']['is_gif'] \
                    and (time.time() - submission.created_utc) / 3600 <= s.video_submission_time \
                    and submission.over_18 == s.over18:
                # Check if video duration is at a desire duration
                if submission.media['reddit_video']['duration'] <= s.video_duration:
                    video_url = submission.media['reddit_video']['fallback_url']
                    video_first_chara = video_url[0:32]
                    audio_url = video_first_chara + 'DASH_audio.mp4'
                    video_title = submission.title
                    # Cleaning video title if contains symbols that is not allow on naming
                    cleaned_video_title = re.sub(r'[\\/?.,:*\n"]', '', video_title)

                    # Define filename and filepath
                    fileaudio = f"{cleaned_video_title}_audio.mp4"
                    filename = f"{cleaned_video_title}.mp4"
                    filepath = os.path.join(save_directory, filename)
                    fileaudiopath = os.path.join(save_directory, fileaudio)

                    # Check if file already exists
                    if not os.path.isfile(filepath):
                        # Download video
                        print('Downloading Video ' + video_url)
                        download_video(video_url, filepath)
                        print('Downloading Audio ' + audio_url)
                        download_audio(audio_url, fileaudiopath)
                        print(f"Downloaded {filename}")

                        # Combine video and audio to form a new video then remove the files used
                        videoClip = VideoFileClip(filepath)
                        try:
                            audioClip = AudioFileClip(fileaudiopath)
                        except(IndexError, OSError):
                            pass
                        final_clip = videoClip.set_audio(audioClip)
                        try:
                            final_clip.write_videofile(s.video_save_dir + '/' + cleaned_video_title + '_withaudio.mp4',
                                                       codec='libx264', audio_codec='aac')
                            print('video saved at ' + s.video_save_dir + ' ' + cleaned_video_title)
                        except(IndexError, OSError, FileNotFoundError):
                            os.remove(s.video_save_dir + cleaned_video_title + '_audio.mp4')
                            pass
                        try:
                            os.remove(filepath)
                            os.remove(fileaudiopath)
                        except (PermissionError, FileNotFoundError):
                            pass

                        # Increment video count
                        max_videos -= 1

                    # Check if maximum number of videos downloaded for this subreddit
                    if max_videos == 0:
                        break

        # Reset maximum number of videos
        max_videos = s.max_video_per_subreddit
