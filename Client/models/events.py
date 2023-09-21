import logging

logger = logging.getLogger(__name__)


class EventArgs:
    def __init__(self):
        pass


class EventHandler:
    def __init__(self, name):
        self.name = name
        self._event_list: list = []

    def register_event(self, func):
        self._event_list.append(func)
        logger.debug(f"Successfully registered function {func} to EventHandler {self.name}")

    def unregister_event(self, func):
        for f in self._event_list:
            if f == func:
                self._event_list.remove(f)
                logger.warning(f"Successfully removed function {f} from {self.name} events.")
                return
        logger.warning(f"Did not remove function {func} from EventHandler {self.name}. Func not found.")

    def run_events(self, args):
        for func in self._event_list:
            func(args)


class EventFactory:
    def __init__(self, name):
        self.name = name
        self.handlers: dict[str: EventHandler] = {}

    def register_new_handler(self, handler: EventHandler):
        logger.debug(f"Registering new eventhandler for {self.name}: {handler.name}")
        self.handlers[handler.name] = handler

    def unregister_handler(self, handler):
        logger.debug(f"Unregistering new eventhandler for {self.name}: {handler.name}")
        self.handlers[handler.name] = None

    def run_handler(self, handler_name, args=None):
        if handler_name in self.handlers.keys():
            handler: EventHandler = self.handlers.get(handler_name)
            handler.run_events(args)
        else:
            logger.warning("Event run failed...")
            logger.warning(f"Handler {handler_name} not found in EventFactory {self.name}")

    def register_new_event(self, handler_name, func):
        if handler_name in self.handlers.keys():
            handler: EventHandler = self.handlers.get(handler_name)
            handler.register_event(func)
        else:
            logger.warning("Event register failed...")
            logger.warning(f"Handler {handler_name} not found in EventFactory {self.name}")

    def unregister_event(self, handler_name, func):
        if handler_name in self.handlers.keys():
            handler: EventHandler = self.handlers.get(handler_name)
            handler.unregister_event(func)
        else:
            logger.warning("Event unregister failed...")
            logger.warning(f"Handler {handler_name} not found in EventFactory {self.name}")
