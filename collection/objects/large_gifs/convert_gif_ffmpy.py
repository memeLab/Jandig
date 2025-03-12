import ffmpy

bitrate = 32
ff = ffmpy.FFmpeg(
inputs={'large_1.gif': None},
outputs={'large_1_lixo_lossless.webm': f'-c:v vp8 -auto-alt-ref 0 -vf "premultiply=inplace=1" -crf 10 -b:v {bitrate}M -maxrate {bitrate}M -bufsize {2*bitrate}M'}
)
ff.run()