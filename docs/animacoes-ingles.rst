Tips for producing animation 
=============================
This document contains technical guidelines and best practices for
production of augmented reality animations for Jandig. Lots of
of these guidelines can be used to produce content for
other platforms.

In addition to producing a version considering the following limitations,
it is recommended that an “ideal” version be produced, which can be
used in controlled environments and/or in the future (as these
limitations will decrease).

File format
~~~~~~~~~~~~~~~~~~

Currently, the only supported format is GIF.

Details
~~~~~~~~

Use as few details and small elements as possible,
as they may not be identifiable by the public.

One way to test here is to save the storyboard images to
300x300px and see if you can identify all the elements. It's
important to remember that the public can see the animation from a distance,
so that it looks very small on the phone screen.

Amount of colors
~~~~~~~~~~~~~~~~~~~

The recommendation is to reduce as much as possible, so it will not
compromise the original colors.

To optimize these values, we recommend minimizing the use of color degradation and
avoid fade transitions.

A technique to plan this usage before producing the animation is
export the storyboard images to GIF with different amounts of
Colors.

Resolution
~~~~~~~~~

Para aumentar a compatibilidade de dispositivos, limitamos a resolução
do quadro de exibição (que aparece em tela cheia no smartphone) em
640x480 pixels. Como a animação só vai aparecer em um trecho desse
quadro, recomendamos a criação do conteúdo em 300x300px.

To increase device compatibility, we limit the resolution
of the display frame (which appears in full screen on the smartphone) in
640x480 pixels. As the animation will only appear in a part of this
framework, we recommend creating the content at 300x300px.

Framerate
~~~~~~~~~

The frame rate (measured in frames per second)
recommended is a maximum of 12 fps.

Loop
~~~~

To create the illusion of continuity, the animation must be looped. In other words, the transition from the last to the first frame must be imperceptible.

Time
~~~~~

The shorter the animation, the better. This will allow for better quality
of images and ensure that the public watches all the material. So far, the longest animation made for Jandig is approximately
20 seconds. The recommendation is that it should have up to 15 seconds.

File size
~~~~~~~~~~~~~~~~~~

While the following parameters have flexibility as to guidelines,
this is the toughest. Files should ideally be up to 500 kB and should not exceed 1 MB. This is a decisive factor in the choice of works to be
included in an exhibition, the smaller the better.

This limitation exists mainly for the following reasons: - We do not have
control of the public connection speed when accessing the content,
which can cause the download of all works to take time. - Not
we want to burden the public's data plan. - Smaller files are more
lightweight require less processing, making the
platform compatible with a greater number of phones.

Conclusion
~~~~~~~~~

To reach an optimal result, the ideal is to test the parameters together.

A recommended process is exporting the parameters,  limiting them as much as possible.
(8 colors, 200x200px, 5 fps) and also with the minimum recommendations of
limitation (256 colors, 300x300px, 12 fps) and compare.

From there, modify one parameter at a time from the minimum limitations, 
reducing only the framerate/resolution/colors to see what is the minimum
that works fine.

If, after reducing the 3 to the minimum that works well, the file is still
large, keep decreasing the parameters in different combinations
to reach an optimal result. Also remember to keep the
high resolution version. Here the recommendation is to save with 1000x1000px and
24fps.

In case you use Adobe Media encoder, there is a tutorial that was developed
by UEMG for `download in
PDF <https://github.com/memeLab/ARte/blob/develop/docs/Tutorial%20de%20Exporta%C3%A7%C3%A3o%20em%20GIF.pdf>`__.
