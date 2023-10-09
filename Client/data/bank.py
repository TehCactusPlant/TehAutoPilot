import logging

from Client.common_utils.models import Event

logger = logging.getLogger(__name__)


class GameState:
    DEFAULT = 0
    MENU = 1
    OVERWORLD = 2
    MAP = 3
    DIALOGUE = 4


class DataBank:
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info('Creating new Databank')
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True
        logger.info("Initializing Databank")
        self.dynamic_variables = {}
        self.trackers = []
        self._game_state = GameState.DEFAULT
        self._debug_entries = {}
        self.on_debug_entry_change = Event()

    def update_debug_entry(self, name, value):
        self._debug_entries[name] = value
        self.on_debug_entry_change(arg_name = name, arg_value=value)

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
