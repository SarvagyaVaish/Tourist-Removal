from CommandLineExecutor import CommandLineExecutor
from ImageAligner import ImageAligner
from ImageBlender import ImageBlender
from ImageSource import ImageSource
import cv2

DISPLAY_INTERMEDIATE_RESULTS = 1

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

        if DISPLAY_INTERMEDIATE_RESULTS:
            window_title = "Intermediate Aligning Result (#" + str(secondary_image_index) + ")"
            cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            cv2.imshow(window_title, aligned_image)


    def blend_nth_secondary_image(self, secondary_image_index, x, y, width, height):
        previous_result_image = self.image_source.get_result_image()
        secondary_image = self.image_source.get_aligned_secondary_image(secondary_image_index)

        if previous_result_image is None or secondary_image is None:
            print "[ERROR] AppInstance::blend_nth_secondary_image() - primary or secondary image is None"
            return

        mask_size = (previous_result_image.shape[0], previous_result_image.shape[1])
        mask_coordinates = (x, y, width, height)

        # Create a mask
        mask = self.image_blender.create_rectangular_mask(mask_size, mask_coordinates)

        # Blend the previous result with the secondary image
        new_result_image = self.image_blender.blend(previous_result_image, secondary_image, mask)

        if new_result_image is None:
            print "[ERROR] AppInstance::blend_nth_secondary_image() - blend result is None"
            return

        # Update result image in image source
        self.image_source.set_result_image(new_result_image)

        if DISPLAY_INTERMEDIATE_RESULTS:
            window_title = "Intermediate Blending Result"
            cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            cv2.imshow(window_title, new_result_image)


    def save_result(self, filename):
        result_image = self.image_source.get_result_image()

        window_title = "Final Result"
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(window_title, result_image)
        cv2.imwrite(filename, result_image)


if __name__ == "__main__":

    commands = [
        '--cmd load "./test1"',
        # '--cmd align 0',
        '--cmd align 1',
        '--cmd align 2',
        # '--cmd blend 0 180 200 100 100',
        '--cmd blend 1 180 200 100 100',
        '--cmd blend 2 180 200 100 100',
        '--cmd save "./test1/result.jpg"',
    ]

    app_instance = AppInstance()
    app_instance.run_as_commandline_app(commands)

    # Keep cv windows open until a key is pressed.
    cv2.waitKey(0)
