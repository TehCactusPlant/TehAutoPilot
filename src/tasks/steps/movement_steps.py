from steps import Step
import numpy as np

from src.input_handling.switch_relay import SwitchToPiController
from src.navigation.nodes import Node
class Spin(Step):

    def __init__(self):
        super().__init__()
        self.tick = 0
        self.max_tick = 4 # number of frames before changing input.
        self.sub_step = 0
        self.max_sub_step = 8
        pass

    def run_step(self):
        self._tick_step()
        #Move direction based on current tick

        pass

    def _tick_step(self):
        self.tick += 1
        if self.tick >= self.max_tick:
            self.tick = 0
            self.sub_step += 1
            if self.sub_step >= self.max_sub_step:
                self.sub_step = 0


class MoveTo(Step):
    acceptable_range = 10

    def __init__(self, dest_node: Node, controller: SwitchToPiController):
        super().__init__()
        self.dest_node = dest_node
        self.controller = controller

    def within_range(self, target_val,acceptable_diff):
        if -acceptable_diff <= target_val <= acceptable_diff:
            return True

    def run_step(self):
        player_pos = (480, 270)
        node_pos = self.dest_node.position
        diffs = (player_pos[0] - node_pos[0], player_pos[1] - node_pos[1])
        x_in_range = self.within_range(diffs[0], self.acceptable_range)
        y_in_range = self.within_range(diffs[1], self.acceptable_range)

        if x_in_range and y_in_range:
            # Arrived at destination. Complete Task.
            return True

        if not x_in_range:
            if diffs[0] > self.acceptable_range:
                # Move Left
                pass
            else:
                # Move Right
                pass

        if not y_in_range:
            if diffs[1] > self.acceptable_range:
                # Move Up
                pass
            else:
                # Move Down
                pass
        return False