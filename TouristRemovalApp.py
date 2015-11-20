from CommandLineExecutor import CommandLineExecutor

commands = ['--cmd load "path/to/folder"', '--cmd align "image_1" "image_2"']

command_line_executor = CommandLineExecutor()
command_line_executor.parse_commands(commands)

command_executed = True
while (command_executed):
    command_executed = command_line_executor.execute_next_command()
