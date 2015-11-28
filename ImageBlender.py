import numpy as np
import scipy as sp
import scipy.signal
import sys
import os
import cv2
from scipy.stats import norm
from scipy.signal import convolve2d
import math

def generatingKernel(parameter):
  """ Return a 5x5 generating kernel based on an input parameter.

  Note: This function is provided for you, do not change it.

  Args:
    parameter (float): Range of value: [0, 1].

  Returns:
    numpy.ndarray: A 5x5 kernel.

  """
  kernel = np.array([0.25 - parameter / 2.0, 0.25, parameter,
                     0.25, 0.25 - parameter /2.0])
  return np.outer(kernel, kernel)


def reduce(image):
    """ Convolve the input image with a generating kernel of parameter of 0.4 and
    then reduce its width and height by two.

    Please consult the lectures and readme for a more in-depth discussion of how
    to tackle the reduce function.

    You can use any / all functions to convolve and reduce the image, although
    the lectures have recommended methods that we advise since there are a lot
    of pieces to this assignment that need to work 'just right'.

    Args:
    image (numpy.ndarray): a grayscale image of shape (r, c)

    Returns:
    output (numpy.ndarray): an image of shape (ceil(r/2), ceil(c/2))
      For instance, if the input is 5x7, the output will be 3x4.

    """

    kernel = generatingKernel(0.4)
    convolvedImage = sp.signal.convolve2d(image, kernel, 'same')

    (rowCount, colCount) = convolvedImage.shape

    desiredR = np.arange(0, rowCount, 2)
    desiredC = np.arange(0, colCount, 2)

    subsampledImage = convolvedImage[desiredR, :]
    subsampledImage = subsampledImage[:, desiredC]
    return subsampledImage


def expand(image):
    """ Expand the image to double the size and then convolve it with a generating
    kernel with a parameter of 0.4.

    You should upsample the image, and then convolve it with a generating kernel
    of a = 0.4.

    Finally, multiply your output image by a factor of 4 in order to scale it
    back up. If you do not do this (and I recommend you try it out without that)
    you will see that your images darken as you apply the convolution. Please
    explain why this happens in your submission PDF.

    Please consult the lectures and readme for a more in-depth discussion of how
    to tackle the expand function.

    You can use any / all functions to convolve and reduce the image, although
    the lectures have recommended methods that we advise since there are a lot
    of pieces to this assignment that need to work 'just right'.

    Args:
    image (numpy.ndarray): a grayscale image of shape (r, c)

    Returns:
    output (numpy.ndarray): an image of shape (2*r, 2*c)
    """

    (rowCount, colCount) = image.shape
    upSampledImage = np.ndarray(shape=(rowCount * 2, colCount * 2), dtype=image.dtype)

    for r in np.arange(2*rowCount):
        for c in np.arange(2*colCount):
            if r % 2 == 1 or c % 2 == 1:
                upSampledImage[r][c] = 0
            else:
                upSampledImage[r, c] = image[r/2, c/2]

    kernel = generatingKernel(0.4)
    resultImage = sp.signal.convolve2d(upSampledImage, kernel, 'same')
    resultImage = 4 * resultImage

    return resultImage


def gaussPyramid(image, levels):
  """ Construct a pyramid from the image by reducing it by the number of levels
  passed in by the input.

  Note: You need to use your reduce function in this function to generate the
  output.

  Args:
    image (numpy.ndarray): A grayscale image of dimension (r,c) and dtype float.
    levels (uint8): A positive integer that specifies the number of reductions
                    you should do. So, if levels = 0, you should return a list
                    containing just the input image. If levels = 1, you should
                    do one reduction. len(output) = levels + 1

  Returns:
    output (list): A list of arrays of dtype np.float. The first element of the
                   list (output[0]) is layer 0 of the pyramid (the image
                   itself). output[1] is layer 1 of the pyramid (image reduced
                   once), etc. We have already included the original image in
                   the output array for you. The arrays are of type
                   numpy.ndarray.

  Consult the lecture and README for more details about Gaussian Pyramids.
  """
  output = [image]

  for level in np.arange(levels):
      output.append(reduce(output[level]))

  return output


def laplPyramid(gaussPyr):
    """ Construct a Laplacian pyramid from the Gaussian pyramid, of height levels.

    Note: You must use your expand function in this function to generate the
    output. The Gaussian Pyramid that is passed in is the output of your
    gaussPyramid function.

    Args:
    gaussPyr (list): A Gaussian Pyramid as returned by your gaussPyramid
                     function. It is a list of numpy.ndarray items.

    Returns:
    output (list): A Laplacian pyramid of the same size as gaussPyr. This
                   pyramid should be represented in the same way as guassPyr,
                   as a list of arrays. Every element of the list now
                   corresponds to a layer of the Laplacian pyramid, containing
                   the difference between two layers of the Gaussian pyramid.

           output[k] = gauss_pyr[k] - expand(gauss_pyr[k + 1])

           Note: The last element of output should be identical to the last
           layer of the input pyramid since it cannot be subtracted anymore.

    Note: Sometimes the size of the expanded image will be larger than the given
    layer. You should crop the expanded image to match in shape with the given
    layer.

    For example, if my layer is of size 5x7, reducing and expanding will result
    in an image of size 6x8. In this case, crop the expanded layer to 5x7.
    """
    output = []

    for i in np.arange(len(gaussPyr) - 1):
        (gaussLayerR, gaussLayerC) = gaussPyr[i].shape

        expandResult = expand(gaussPyr[i + 1])
        expandResult = expandResult[np.arange(gaussLayerR), :]
        expandResult = expandResult[:, np.arange(gaussLayerC)]

        newLayer = gaussPyr[i] - expandResult

        output.append(newLayer)

    output.append(gaussPyr[len(gaussPyr)-1])

    return output


def blend(laplPyrWhite, laplPyrBlack, gaussPyrMask):
    """ Blend the two Laplacian pyramids by weighting them according to the
    Gaussian mask.

    Args:
        laplPyrWhite (list): A Laplacian pyramid of one image, as constructed by
                             your laplPyramid function.

        laplPyrBlack (list): A Laplacian pyramid of another image, as constructed by
                             your laplPyramid function.

        gaussPyrMask (list): A Gaussian pyramid of the mask. Each value is in the
                             range of [0, 1].

    The pyramids will have the same number of levels. Furthermore, each layer
    is guaranteed to have the same shape as previous levels.

    You should return a Laplacian pyramid that is of the same dimensions as the
    input pyramids. Every layer should be an alpha blend of the corresponding
    layers of the input pyramids, weighted by the Gaussian mask. This means the
    following computation for each layer of the pyramid:
    output[i, j] = current_mask[i, j] * white_image[i, j] +
                   (1 - current_mask[i, j]) * black_image[i, j]
    Therefore:
    Pixels where current_mask == 1 should be taken completely from the white
    image.
    Pixels where current_mask == 0 should be taken completely from the black
    image.

    Note: current_mask, white_image, and black_image are variables that refer to
    the image in the current layer we are looking at. You do this computation for
    every layer of the pyramid.
    """

    blended_pyr = []

    layerCount = len(laplPyrWhite)

    for i in np.arange(layerCount):

        whiteImg = laplPyrWhite[i]
        blackImg = laplPyrBlack[i]
        mask = gaussPyrMask[i]

        (rowCount, colCount) = mask.shape
        result = np.ndarray(shape=(rowCount, colCount), dtype=np.float)

        for i in np.arange(rowCount):
            for j in np.arange(colCount):
                result[i, j] = mask[i, j] * whiteImg[i, j] + (1 - mask[i, j]) * blackImg[i, j]

        blended_pyr.append(result)

    return blended_pyr


def collapse(pyramid):
    """ Collapse an input pyramid.

    Args:
    pyramid (list): A list of numpy.ndarray images. You can assume the input is
                  taken from blend() or laplPyramid().

    Returns:
    output(numpy.ndarray): An image of the same shape as the base layer of the
                           pyramid and dtype float.

    Approach this problem as follows, start at the smallest layer of the pyramid.
    Expand the smallest layer, and add it to the second to smallest layer. Then,
    expand the second to smallest layer, and continue the process until you are
    at the largest image. This is your result.

    Note: sometimes expand will return an image that is larger than the next
    layer. In this case, you should crop the expanded image down to the size of
    the next layer. Look into numpy slicing / read our README to do this easily.

    For example, expanding a layer of size 3x4 will result in an image of size
    6x8. If the next layer is of size 5x7, crop the expanded image to size 5x7.
    """

    (rowCount, colCount) = pyramid[0].shape
    result = np.ndarray(shape=(rowCount, colCount), dtype=np.float)
    layerCount = len(pyramid)

    # start at the last layer
    onGoingSum = pyramid[layerCount - 1]
    for layer in np.arange(layerCount-2, -1, -1):
        expandResult = expand(onGoingSum)
        currLayer = pyramid[layer]

        # Crop layer to match next layer
        (rowCount, colCount) = currLayer.shape
        expandResult = expandResult[np.arange(rowCount), :]
        expandResult = expandResult[:, np.arange(colCount)]

        onGoingSum = expandResult + currLayer

    return onGoingSum

def run_blend(black_image, white_image, mask):
  """ This function administrates the blending of the two images according to
  mask.

  Assume all images are float dtype, and return a float dtype.
  """

  # Automatically figure out the size
  min_size = min(black_image.shape)
  depth = int(math.floor(math.log(min_size, 2))) - 4 # at least 16x16 at the highest level.

  gauss_pyr_mask = gaussPyramid(mask, depth)
  gauss_pyr_black = gaussPyramid(black_image, depth)
  gauss_pyr_white = gaussPyramid(white_image, depth)


  lapl_pyr_black  = laplPyramid(gauss_pyr_black)
  lapl_pyr_white = laplPyramid(gauss_pyr_white)

  outpyr = blend(lapl_pyr_white, lapl_pyr_black, gauss_pyr_mask)
  outimg = collapse(outpyr)

  outimg[outimg < 0] = 0 # blending sometimes results in slightly out of bound numbers.
  outimg[outimg > 255] = 255
  outimg = outimg.astype(np.uint8)

  return lapl_pyr_black, lapl_pyr_white, gauss_pyr_black, gauss_pyr_white, \
      gauss_pyr_mask, outpyr, outimg


class ImageBlender:
    """
    Handles creating masks and performing image blending.
    """

    def __init__(self):
        pass

    def blend(self, white_image, black_image, mask):
        """
        Blend white and black images using provided mask.
        """
        if white_image is None or black_image is None or mask is None:
            print "[ERROR] ImageBlender::blend() - Black/white/mask images are None"
            return None

        if black_image.shape != white_image.shape or black_image.shape != mask.shape:
            print "[ERROR] ImageBlender::blend() - The sizes of images and the mask are not equal"
            return None

        black_img = black_image.astype(float)
        white_img = white_image.astype(float)
        mask_img = mask.astype(float) / 255

        out_layers = []

        for channel in range(3):
            lapl_pyr_black, lapl_pyr_white, gauss_pyr_black, gauss_pyr_white, gauss_pyr_mask,\
                outpyr, outimg = run_blend(black_img[:,:,channel], white_img[:,:,channel], mask_img[:,:,channel])

            out_layers.append(outimg)

        outimg = cv2.merge(out_layers)

        return outimg


    def create_rectangular_mask(self, mask_size, mask_coordinates):
        """
        Return a WHITE image of size 'mask_size' and
        a BLACK region located at 'mask_coordinates'.

        'mask_size' is a tuple (width, height)
        'mask_coordinates' is a tuple (x, y, width, height).
        """

        (rowCount, colCount) = mask_size
        (x, y, width, height) = mask_coordinates

        mask_image = np.ndarray(shape=(rowCount, colCount, 3), dtype=np.float)

        for row in np.arange(rowCount):
            for col in np.arange(colCount):
                if row >= y and row <= y + height and col >= x and col <= x + width:
                    mask_image[row, col, 0] = 0
                    mask_image[row, col, 1] = 0
                    mask_image[row, col, 2] = 0
                else:
                    mask_image[row, col, 0] = 255
                    mask_image[row, col, 1] = 255
                    mask_image[row, col, 2] = 255

        return mask_image


