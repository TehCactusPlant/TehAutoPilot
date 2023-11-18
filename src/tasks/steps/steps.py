from abc import ABC, abstractmethod

from src.data.bank import DataBank


class Step(ABC):
    def __init__(self, data_bank: DataBank, args, condition, positive_step, negative_step):
        self.complete = False
        self.data_bank: DataBank = DataBank()
        self.condition: Step = condition
        self.positive_step: Step = positive_step
        self.negative_step: Step = negative_step
        # self.interrupt_task_name = interrupt_task_name
        # self.is_interrupt = True if interrupt_task_name is not None else False

    def run_step(self):
        self._internal_step_function()
        if self.condition is not None:
            self.condition.run_step()

    @abstractmethod
    def _internal_step_function(self):
        raise NotImplemented


class ActionStep(Step):
    def __init__(self, data_bank: DataBank, args, condition, positive_step, negative_step):
        super().__init__(data_bank, args, condition, positive_step, negative_step)

    @abstractmethod
    def _internal_step_function(self):
        pass


class ConditionStep(Step):
    def __init__(self, data_bank: DataBank, args, condition, positive_step, negative_step):
        super().__init__(data_bank, args, condition, positive_step, negative_step)
        self.condition_met = False
        self.condition_setup = False

    def run_step(self):
        if not self.condition_setup:
            self._setup_condition()
        self.condition_met = self._internal_step_function()
        self._internal_step_function()
        if self.condition is not None:
            self.condition.run_step()
        pass

    @abstractmethod
    def _internal_step_function(self) -> bool:
        raise NotImplemented

    @abstractmethod
    def _setup_condition(self):
        raise NotImplemented
