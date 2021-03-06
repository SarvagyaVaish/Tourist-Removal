from ImageAligner import ImageAligner
from ImageSource import ImageSource
import cv2

image_source = ImageSource();
#Change this to your location
loaded = image_source.load_images("./sources")

if(loaded):
    output_img = ImageAligner().align_image(image_source.primary_image, image_source.secondary_images[0]);
    cv2.imwrite('./sources/original_warp.png', output_img)

    output_image = image_source.primary_image

    for row in range(len(output_img)):
        for col in range(len(output_img[0])):
            if output_img[row][col][0] > 0:
                output_image[row][col] = output_img[row][col]

    cv2.imwrite('./sources/simple_merge.png', output_image)
