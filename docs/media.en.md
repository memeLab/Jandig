# Tips for producing media

This document contains technical guidelines and best practices for
producing media (images, animations, videos and 3D models) used in
augmented and mixed reality Artworks on Jandig. Many of these
guidelines can also be useful for producing content for other
platforms.

In addition to producing a version considering the following
limitations, it is recommended that a higher-quality "ideal" version
also be produced, which can be used in controlled environments and/or
in the future (as these limitations decrease).

## Supported formats

When uploading an Object, the currently accepted formats are:

- **GIF** — simple animations, with good compatibility and support for
  transparent backgrounds, allowing the animation to blend well into
  the augmented reality scene.
- **PNG** — static image (no animation).
- **MP4** and **WebM** — video, including transparency support in
  WebM. Recommended for longer or more detailed animations, since video
  compresses much better than GIF.
- **GLB** — 3D model. **Only available for MR Exhibits** (the Mixed
  Reality app for Meta Quest). AR Artworks (the mobile app, based on
  Markers) do not accept GLB Objects.

You can also attach an optional **audio description** to an Object, in
MP3, OGG or WAV format, to make the Artwork more accessible.

## Details

Use as few details and small elements as possible, as they may not be
identifiable by the public.

One way to test this is to save the storyboard images at 300x300px and
check if you can still identify all the elements. It's important to
remember that the public may see the content from a distance, so it
will appear quite small on the phone screen.

## Amount of colors (GIF)

The recommendation is to reduce this as much as possible, without
compromising the original colors.

To optimize these values, we recommend minimizing the use of gradients
and avoiding fade transitions.

A technique to plan this before producing the animation is to export
the storyboard images as GIF with different amounts of colors.

## Resolution

Since the content is mostly viewed on smartphone screens, and often
from a distance, we recommend creating content around 300x300px to
400x400px. Resolutions higher than that rarely bring a perceptible
quality gain on the device, but significantly increase file size and
loading time.

For GLB models (exclusive to MR Exhibits on Meta Quest), the relevant
resolution is the model's textures — prefer optimized, compressed
textures instead of very high-resolution ones.

## Framerate (GIF and video)

There's no fixed ideal number — the recommendation is to test and use
the lowest frame rate that still looks smooth for that particular
animation. Lower frame rates reduce file size and loading time, so it's
worth gradually lowering it until you notice quality starting to be
compromised.

## Loop

To create the illusion of continuity, the animation (GIF or video)
should loop. That is, the transition from the last to the first frame
should be imperceptible.

## Duration

The shorter the content, the better. This allows for better image
quality and ensures the public watches all of the material. We
recommend up to 15 seconds of duration for animations and videos.

## File size

This is the strictest parameter: smaller files load faster and consume
less of the public's mobile data. As a reference (the smaller, the
better):

- **GIF**: ideally up to 500 kB, 1 MB at most.
- **MP4 / WebM**: since it compresses better than GIF, it's possible to
  keep good quality with files up to 1-2 MB for short looping clips.
- **PNG**: ideally up to 300 kB, since it's a static image.
- **GLB**: since it's used in the Meta Quest app (usually over Wi-Fi),
  mobile data matters less, but device performance still matters —
  prefer optimized models (low poly count, compressed textures).

This limitation exists mainly for the following reasons:

- We have no control over the public's connection speed when accessing
  the content, which can make downloading all Artworks slow.
- We don't want to weigh down the public's data plan.
- Smaller files require less processing, making the platform
  compatible with a wider range of devices.

## Conclusion

To achieve an optimal result, it's best to test the parameters
together (resolution, colors, framerate and duration).

A recommended process is to export with heavily reduced parameters
(e.g., few colors, low resolution, low framerate) as well as a
higher-quality version, and compare them. From there, adjust one
parameter at a time, reducing it until you notice the point where
quality starts to be compromised.

If, even after reducing all parameters to the minimum acceptable
level, the file is still large, keep adjusting different combinations
until you reach an optimal result. Also remember to keep a
high-resolution version for use in controlled environments and/or in
the future.

If you use Adobe Media Encoder, there's a tutorial developed by UEMG
available for [download as a
PDF](https://github.com/memeLab/ARte/blob/develop/docs/Tutorial%20de%20Exporta%C3%A7%C3%A3o%20em%20GIF.pdf).

We also prepared a tutorial on how to export GIFs with a transparent
background: [download the PDF](files/como_exportar_gifs_com_transparencia.pdf).
