from src.imaging.scanning import Tracker
from src.tasks.steps.steps import Step, ConditionStep


class ScanOnce(ConditionStep):
    def _setup_condition(self):
        self.tracker = Tracker
        self.data_bank.trackers = None

    def _internal_step_function(self) -> bool:
        pass
