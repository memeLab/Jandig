from moviepy import VideoFileClip

file_name = "large_1"
clip = VideoFileClip(f"{file_name}.gif")
clip.write_videofile(f"{file_name}.webm")