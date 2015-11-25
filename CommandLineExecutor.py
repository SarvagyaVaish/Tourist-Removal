from ImageAligner import ImageAligner
from ImageBlender import ImageBlender
from ImageSource import ImageSource

class CommandLineExecutor:
    """
    Parse command line arguments and call other methods.
    """

    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.command_queue = []


    def parse_commands(self, commands):
        """
        This method parses the string and queues commands to be run when execute_next_command is called.
        :param commands: list of command strings

        Commands accepted:
            '--cmd load "path/to/folder"'
                Loads primary and secondary images from folder.

            '--cmd align 2'
                Aligns secondary image (with provided index) with primary image.

            '--cmd blend 2 10 20 120 300'
                Blends region of secondary image (with provided index) into primary image.
                Parameters: index x y width height

            '--cmd save "path/to/result_filename.ext"'
                Saves primary image at specified location.
        """

        for command_str in commands:
            command_parts = command_str.split(' ')

            # Check if command string has at least 2 parts: '--cmd' and 'command_type'
            if len(command_parts) <= 1:
                print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                continue

            # Extract command and parameters
            command_type = command_parts[1].lower()
            command_parameters = command_parts[2:len(command_parts)]

            # Form a command to be added to the command queue
            command = {}
            if command_type == 'load':
                # Check number of parameters
                if len(command_parameters) != 1:
                    print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                    continue

                folder_path = command_parameters[0].replace('"', '').strip()

                command['method'] = self.app_instance.image_source.load_images
                command['parameters'] = {
                    'folder_path': folder_path
                }

            elif command_type == 'align':
                # Check number of parameters
                if len(command_parameters) != 1:
                    print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                    continue

                secondary_image_index = int(command_parameters[0])

                command['method'] = self.app_instance.align_nth_secondary_image
                command['parameters'] = {
                    'secondary_image_index': secondary_image_index
                }

            elif command_type == 'blend':
                # Check number of parameters
                if len(command_parameters) != 5:
                    print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                    continue

                secondary_image_index = int(command_parameters[0])
                x = int(command_parameters[1])
                y = int(command_parameters[2])
                width = int(command_parameters[3])
                height = int(command_parameters[4])

                command['method'] = self.app_instance.blend_nth_secondary_image
                command['parameters'] = {
                    'secondary_image_index': secondary_image_index,
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height
                }

            elif command_type == 'save':
                # Check number of parameters
                if len(command_parameters) != 1:
                    print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                    continue

                filename = command_parameters[0].replace('"', '').strip()

                command['method'] = self.app_instance.save_result
                command['parameters'] = {
                    'filename': filename
                }

            else:
                print "[ERROR] CommandLineExecutor::parse_commands() - Command not properly formatted: (" + command_str + ")"
                continue

            print "[INFO] Queuing command: " + command_str

            self.command_queue.append(command)


    def execute_next_command(self):
        """
        Execute next queued command.
        Returns false if there was no command left to process.
        """

        if len(self.command_queue) == 0:
            print "[ERROR] CommandLineExecutor::execute_next_command() - No commands in queue."
            return False

        print "[INFO] Processing command..."

        command = self.command_queue.pop(0)
        command['method'](**command['parameters'])

        # Return true if there are more commands left to process
        if len(self.command_queue) > 0:
            return True

        return False
