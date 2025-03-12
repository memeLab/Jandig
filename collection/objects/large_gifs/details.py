import ffmpeg
vid = ffmpeg.probe("large_1.gif")
print(vid['streams'])