from CommandLineExecutor import CommandLineExecutor
from ImageAligner import ImageAligner
from ImageBlender import ImageBlender
from ImageSource import ImageSource
import cv2

class AppInstance:
    """
    Class to bind everything together.
    """

    def __init__(self):
        self.command_line_executor = CommandLineExecutor(self)
        self.image_aligner = ImageAligner()
        self.image_blender = ImageBlender()
        self.image_source = ImageSource()


    def run_as_commandline_app(self, commands):
        self.command_line_executor.parse_commands(commands)

        pending_commands = True
        while pending_commands:
            pending_commands = self.command_line_executor.execute_next_command()


    def run_as_gui_app(self):
        pass


    def align_nth_secondary_image(self, secondary_image_index):
        primary_image = self.image_source.get_primary_image()
        secondary_image = self.image_source.get_secondary_image(secondary_image_index)

        if primary_image is None or secondary_image is None:
            print "[ERROR] AppInstance::align_nth_secondary_image() - primary or secondary image is None"
            return

        aligned_image = self.image_aligner.align_image(primary_image, secondary_image)
        self.image_source.set_aligned_secondary_image(aligned_image, secondary_image_index)


    def blend_nth_secondary_image(self, secondary_image_index, x, y, width, height):
        primary_image = self.image_source.get_primary_image()
        secondary_image = self.image_source.get_aligned_secondary_image(secondary_image_index)

        if primary_image is None or secondary_image is None:
            print "[ERROR] AppInstance::blend_nth_secondary_image() - primary or secondary image is None"
            return

        mask_size = (primary_image.shape[0], primary_image.shape[1])
        mask_coordinates = (x, y, width, height)

        mask = self.image_blender.create_rectangular_mask(mask_size, mask_coordinates)

        result_image = self.image_blender.blend(primary_image, secondary_image, mask)


    def save_result(self, filename):
        pass


if __name__ == "__main__":

    commands = [
        '--cmd load "path/to/folder"',
        '--cmd align 2',
        '--cmd blend 2 10 20 120 300',
        '--cmd save "path/to/result_filename.ext"',
    ]

    app_instance = AppInstance()
    app_instance.run_as_commandline_app(commands)
