class CommandLineExecutor:
    """
    Parse command line arguments and call other methods.
    """

    def __init__(self):
        pass

    def parse_commands(self, commands):
        """
        'commands' is a list of command strings.
        For example:
            ['--cmd load "path/to/folder"', '--cmd align "image_1" "image_2"']

        This method parses the string and queues commands to be run when execute_next_command is called.
        """
        pass

    def execute_next_command(self):
        """
        Execute next queued command.
        Returns false if there was no command left to process.
        """
        pass
