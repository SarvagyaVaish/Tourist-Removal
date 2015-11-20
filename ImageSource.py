class ImageSource:

    def __init__(self):
        self.primary_image = None
        self.secondary_images = []

    def load_images(self, folder_path):
        """
        Load images in the folder path provided.
        Return true if
            - exactly 1 primary image was found
            - at least 1 secondary image was found

        Naming convention:
            Each folder will have one "Primary.jpg" image and at least one "Secondary-x.jpg" image,
            where x corresponds to the image number.
        """
        pass
