import logging

from Client.common_utils.models import Event, ReactiveList, ReactiveStore

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
        from Client.models.core import ReferenceType, Location, Reference

        self.initialized = True
        logger.info("Initializing Databank")
        self.dynamic_variables: ReactiveStore = ReactiveStore()

        # Private Variables
        self._game_state = GameState.DEFAULT
        self._debug_entries = {}
        self._current_location = None

        # Global LTS
        self.ref_types: ReactiveStore = ReactiveStore()
        for ref_type in ReferenceType.get_all():
            self.ref_types.update_variable(ref_type.name, ref_type)

        self.references: ReactiveStore = ReactiveStore()
        for ref in Reference.get_all():
            self.references.update_variable(ref.name, ref)

        self.locations: ReactiveStore = ReactiveStore()
        for loc in Location.get_all():
            self.locations.update_variable(loc.location_name, loc)

        # Events
        self.on_location_change = Event()
        self.on_debug_entry_change = Event()

        # Finalize Init
        self.set_location(self.locations.get_variable_value("solaceon"))

    def get_location_by_name(self, name):
        for loc in self.locations:
            if loc.location_name == name:
                return loc

    def update_reference_list(self, reference):
        pass

    def set_location(self, location):
        print(location)
        self._current_location = location
        if location not in self.locations.get_all().values():
            self.locations.update_variable(location.location_name, location)
        self.on_location_change(location)

    def update_debug_entry(self, name, value):
        self._debug_entries[name] = value
        self.on_debug_entry_change(arg_name=name, arg_value=value)

    def set_game_state(self, game_state:int):
        self._game_state = game_state

    def get_game_state(self):
        return self._game_state
