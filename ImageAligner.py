import numpy as np
import cv2

try:
    from cv2 import ORB as SIFT
except ImportError:
    try:
        from cv2 import SIFT
    except ImportError:
        try:
            SIFT = cv2.ORB_create
        except:
            raise AttributeError("Your OpenCV(%s) doesn't have SIFT / ORB."
                                 % cv2.__version__)


def get_image_corners(image):
    return np.array([[[0, 0]], [[0, image.shape[0]]], [[image.shape[1], 0]], [[image.shape[1], image.shape[0]]]], dtype=np.float32)


def find_matches_between_images(image_1, image_2, num_matches):
    matches = None
    image_1_kp = None
    image_1_desc = None
    image_2_kp = None
    image_2_desc = None

    image_1_kp, image_1_desc = SIFT().detectAndCompute( image_1, None )
    image_2_kp, image_2_desc = SIFT().detectAndCompute( image_2, None )
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(image_1_desc, image_2_desc)
    matches = sorted(matches, key = lambda x:x.distance)
    return image_1_kp, image_2_kp, matches[:num_matches]


def find_homography(image_1_kp, image_2_kp, matches):
    image_1_points = np.zeros((len(matches), 1, 2), dtype=np.float32)
    image_2_points = np.zeros((len(matches), 1, 2), dtype=np.float32)
    for match_idx, match in enumerate(matches):
        image_1_points[match_idx] = image_1_kp[match.queryIdx].pt
        image_2_points[match_idx] = image_2_kp[match.trainIdx].pt
    return cv2.findHomography(image_1_points, image_2_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)[0]


def warpImagePair(image_1, image_2, homography):
    warped_image = None
    x_min = 0
    y_min = 0
    x_max = 0
    y_max = 0

    image_1_corners = get_image_corners(image_1)
    image_2_corners = get_image_corners(image_2)

    image_1_corners = cv2.perspectiveTransform(image_1_corners, homography)
    corners = np.concatenate((image_1_corners, image_2_corners))

    x_min = min(corners[:, 0, 0])
    x_max = max(corners[:, 0, 0])
    y_min = min(corners[:, 0, 1])
    y_max = max(corners[:, 0, 1])

    translation_matrix = np.array([[1, 0, -1 * x_min], [0, 1, -1 * y_min], [0, 0, 1]])
    translated_homography = np.dot(translation_matrix, homography)

    warped_image_1 = cv2.warpPerspective(image_1, translated_homography, (x_max - x_min, y_max - y_min))

    # Select a sub-region of the warped image that matches image_2's (primary image's) coordinate frame
    warped_image_1 = warped_image_1[-y_min:-y_min+image_2.shape[0], -x_min:-x_min+image_2.shape[1]]

    return warped_image_1


class ImageAligner:

    """
    Handles aligning images using feature detection and image transformation.
    """

    def __init__(self):
        pass

    def align_image(self, primary_image, secondary_image):
        """
        Transform the secondary image to be aligned to the primary image.
        :param primary_image:
        :param secondary_image:
        """
        secondary_kp, primary_kp, matches = find_matches_between_images(secondary_image, primary_image, 50)
        homography = find_homography(secondary_kp, primary_kp, matches)
        warped = warpImagePair(secondary_image, primary_image, homography)

        return warped