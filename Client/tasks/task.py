import numpy as np
from abc import ABC, abstractmethod

from Client.tasks.steps.steps import Step


class Task:
    def __init__(self, name, t_id, steps: list, should_restart) -> None:
        self.name = name
        self.task_id = t_id
        self.steps: list[Step] = steps
        self.interrupts: list[Step] = []
        self.parse_interrupts()
        self.current_step: Step = steps[0]
        self.current_index = 0
        self.num_steps = len(steps)
        self.complete = False
        self.should_restart = should_restart

    def restart(self):
        self.current_step = self.steps[0]
        self.current_index = 0

    def parse_interrupts(self):
        for step in self.steps:
            if step.is_interrupt:
                self.interrupts.append(step)
                self.steps.remove(step)


    def run_current_step(self):
        int_res = self.run_interrupts()
        if int_res is not None:
            return int_res.interrupt_task_name
        result = self.current_step.run_step()
        if result is True:
            self.update_next_step()

    def run_interrupts(self):
        for interrupt in self.interrupts:
            result = interrupt.run_step()
            if result is True:
                return interrupt
        return None

    def update_next_step(self):
        self.current_index += 1
        if self.num_steps >= self.current_index:
            # End Task
            self.complete = True
        else:
            self.current_step = self.steps[self.current_index]


