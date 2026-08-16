# Hints to produce Tags

This document contains tecnical, aesthetics and good practices
guidelines to the production of Tags of augmented reality Jandig.

You don't need to create a marker file with specific borders, margins or
thicknesses. Just upload any image (PNG or JPG) on the Marker upload
page and Jandig automatically adds the black border needed for
recognition, showing you a preview of the result before you save it.

## Borders

The borders are graphic elements that trigger the recognition of the
object associated with each tag. For this reason, one should not cover
them and them must always be seen completely by the camera. Put the
finger over the border or approach the camera too close to the tag will
derail the recognition, for example. This feature should be always taken
into account in the application of the tags.

The black border is automatically added by the platform around the
image you upload, so there's no need to draw it, measure it, or leave
margin for it in your original image.

If your image has dark edges or low contrast against black, check the
"Add inner border" option when uploading the marker: it inserts a thin
white ring between the image and the black border, making the boundary
between them easier for the camera to detect.

## Square format

Jandig tags are always square. If you upload a rectangular image, it
will be resized to fit a square, which can distort its content
(stretching it horizontally or vertically). To avoid distortion, prefer
using images that are already square (width equal to height).

## Symmetry

Considering that the visualization of the object depends on the position
of the Tag in relation of the camera, we avoid using images with
symmetry vertical as well as horizantal. This rule aim avoid that the
recognition system get confused about which orientation it must show the
image.

## Colors and gradient

Colored images and gradients are fully supported: recognition compares
the central image in color, not just black and white. For more reliable
recognition, try to keep good contrast between your image's colors and
the black border around it.

## Printing and about that

Reflexes, including over the borders, can impede that your Tags be
recognized as a Tag. So that thay are recognized more easily by the
system, they should utilize opaque paints and materials in them
production.

When you download the marker for printing (the "print" version), it
already comes with a white safety margin around the black border, ready
for stickers or application over dark backgrounds — there's no need to
add this margin manually.

## Illumination

The quality and color of ambient lighting can influence the Tag reading.
For a good visualization, prefer a well distributed illumination, that
does not generate reflections and avoid using amber colored lighting.

## Stickers

Although Tags can be recognized even in very small formats, we usually
produce Jandig Tags stickers with 5 x 5 centimeters. This dimension
associates good perfomance with good readability of all elements,
including the text.
