import cv2
import os
import re


class ImageSource:

    def __init__(self):
        self.primary_image = None
        self.secondary_images = []
        self.aligned_secondary_images = {}

        # Intermediate result image
        self.result_image = None


    def load_images(self, folder_path):
        """
        Load images in the folder path provided.
        Return true if
            - exactly 1 primary image was found
            - at least 1 secondary image was found

        Naming convention:
            Each folder will have one "Primary.ext" image and at least one "Secondary-x.ext" image,
            where x corresponds to the image number.
            :param folder_path: String
        """

        # Most image load comes from Assignment 8 test script
        # Extensions recognized by OpenCV
        extensions = ['.bmp', '.pbm', '.pgm', '.ppm', '.sr', '.ras', '.jpeg',
                      '.jpg', '.jpe', '.jp2', '.tiff', '.tif', '.png']

        secondary_names_to_sort = []
        for dir_name, dir_names, file_names in os.walk(folder_path):
            for filename in file_names:
                name, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    if name.lower() == 'primary':
                        self.primary_image = cv2.imread(os.path.join(dir_name, filename))
                    elif 'secondary-' in name.lower():
                        secondary_names_to_sort.append(filename)
            secondary_names_to_sort = self.__natural_sort(secondary_names_to_sort)
            for secondary in secondary_names_to_sort:
                self.secondary_images.append(cv2.imread(os.path.join(dir_name, secondary)))

        # is not [] is only necessary if you want the boolean and not the falsy/truthy value
        return self.primary_image is not None and self.secondary_images is not []


    # Added to sort the files for 1 vs 01 vs 10, etc
    # Taken from https://stackoverflow.com/qsuestions/11150239/python-natural-sorting
    def __natural_sort(self, l):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key = alphanum_key)


    def get_primary_image(self):
        return self.primary_image


    def get_number_of_secondary_images(self):
        return len(self.secondary_images)


    def get_secondary_image(self, index):
        if index < len(self.secondary_images):
            return self.secondary_images[index]
        return None


    def set_aligned_secondary_image(self, image, index):
        self.aligned_secondary_images[index] = image


    def get_aligned_secondary_image(self, index):
        # Boundary checking on index
        if index not in range(len(self.secondary_images)):
            return None

        # If the aligned secondary image does not exist, return None
        if index not in self.aligned_secondary_images:
            return None

        return self.aligned_secondary_images[index]


    def get_result_image(self):
        if self.result_image is None:
            return self.primary_image
        else:
            return self.result_image


    def set_result_image(self, new_result_image):
        self.result_image = new_result_image
