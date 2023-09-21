import threading
import logging
logger = logging.getLogger(__name__)


class CLICommand:
    def __init__(self,name ,func, num_args, help_text):
        self.name = name
        self.func = func
        self.help_text = help_text
        self.num_args = num_args
        if num_args > 5:
            logger.error(f"Error occured for command {name}. Too many arguments registered")

    def process_command(self, args):
        if self.num_args == len(args):
            try:
                if self.num_args == 0:
                    self.func()
                elif self.num_args == 1:
                    var1 = self.func(args[0])
                elif self.num_args == 2:
                    var1 = self.func(args[0], args[1])
                elif self.num_args == 3:
                    var1 = self.func(args[0], args[1], args[2])
                elif self.num_args == 4:
                    var1 = self.func(args[0], args[1], args[2], args[3])
                elif self.num_args == 5:
                    var1 = self.func(args[0], args[1], args[2], args[3], args[4])
            except Exception as e:
                logging.error(f"Error during CLI Command process. {self.name} failed, trace:\n{e}")
            finally:
                pass


class CustomCLI:
    cli_active = True
    cli_commands = {}
    thread: threading.Thread = None
    def __init__(self):
        self.register_event("help", self.get_help, 1, "arg1: command name")
        self.register_event("stop", self.stop, 0, "stops CLI\n-DOES NOT AUTO RESTART- ")
        self.register_event("commands", self.list_commands, 0, "provides commands and help text")

    def register_event(self, name, func, num_args, help_text=None):
        if help_text is None:
            help_text = f"No help text registered for command {name}"
        logging.info(f"command {name} registered")
        self.cli_commands[name] = CLICommand(name, func, num_args, help_text)

    def get_help(self, name):
        command = self.cli_commands.get(name)
        if command is None:
            logging.error(f"Command {name} not found.")
            return
        logger.info(f"Command: {name}")
        logger.info(f"{name}:\n{command.help_text}")

    def list_commands(self):
        for name, command in self.cli_commands.items():
            logger.info("----------")
            logger.info(self.get_help(name))

    def start_cli(self):
        thread = threading.Thread(target=self._cli_loop)
        thread.start()

    def _cli_loop(self):
        while self.cli_active:
            cli_input = input("Enter command: ")
            if len(cli_input) >= 1:
                args = str.split(cli_input, " ")
                self._run_command(args)

    def _run_command(self, args):
        if len(args) <= 0:
            return
        name = args[0]
        args = tuple(args[1:])
        if name in self.cli_commands:
            self.cli_commands.get(name).process_command(args)
        else:
            logger.info("Command not found. See 'commands' for command list")

    def stop(self):
        self.cli_active = False
