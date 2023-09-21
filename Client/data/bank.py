import logging

from Client.models.events import EventFactory, EventHandler, EventArgs

logger = logging.getLogger(__name__)


class GameState:
    DEFAULT = 0
    MENU = 1
    OVERWORLD = 2
    MAP = 3
    DIALOGUE = 4


class DataBank:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Creating new DataBank')
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.dynamic_variables = {}
        self.trackers = []
        self._game_state = GameState.DEFAULT
        self._debug_entries = {}
        self.debug_entry_events = EventFactory("bank_debug_entries")
        self.debug_entry_events.register_new_handler(EventHandler("on_debug_change"))

    def update_debug_entry(self, name, value):
        self._debug_entries[name] = value
        args = EventArgs()
        args.arg_name = name
        args.arg_value = value
        self.debug_entry_events.run_handler("on_debug_change", args)

    def get_debug_entries(self):
        return self._debug_entries

    def set_game_state(self, game_state:int):
        self._game_state = game_state

    def get_game_state(self):
        return self._game_state

    def add_tracker(self, tracker):
        self.trackers.append(tracker)

    def remove_tracker(self, tracker):
        try:
            self.trackers.remove(tracker)
        except Exception as e:
            logger.error(f"Error occured in removing tracker. {tracker.name} does not exist?")
