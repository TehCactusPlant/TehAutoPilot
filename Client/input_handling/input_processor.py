import json
import math

import XInput as xi
from . import input_packet
import numpy as np

# Implement hold feature
# Fire and forget
# Timing to sync with frames
# Stick Presses 


class SwitchButtons:
    A = 'A'
    B = 'B'
    Y = 'Y'
    X = 'X'
    RB = 'R'
    LB = 'L'
    LT = 'ZL'
    RT = 'ZR'
    LS = 'L_STICK'
    RS = 'R_STICK'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    LEFT = 'DPAD_LEFT'
    RIGHT = 'DPAD_RIGHT'
    UP = 'DPAD_UP'
    DOWN = 'DPAD_DOWN'


class SwitchPacketAssembler:
    def __init__(self, delay):
        self.current_packet = input_packet.create_input_packet()
        self.delay = delay
        self.unpresses = {}
        self.tps = 1.0 / delay
        pass

    def time_to_ticks(self, seconds: float):
        return seconds * self.tps

    def process_unpresses(self):
        for btn, tick in self.unpresses.items():
            self.unpresses[btn] -= 1
            if tick <= 0:
                self.unpress_button(btn)

    def assemble_state_automated(self):
        new_state = self.current_packet
        # Process unpress
        self.process_unpresses()
        return new_state

    def assemble_state_manual(self):
        new_state = input_packet.create_input_packet()
        state = xi.get_state(0)
        buttons = xi.get_button_values(state)
        sticks = xi.get_thumb_values(state)
        triggers = xi.get_trigger_values(state)
        lx = sticks[0][0]
        ly = sticks[0][1]
        rx = sticks[1][0]
        ry = sticks[1][1]

        # Remap
        new_state["A"] = buttons["B"]
        new_state["B"] = buttons["A"]
        new_state["Y"] = buttons["X"]
        new_state["X"] = buttons["Y"]
        new_state["PLUS"] = buttons["START"]
        new_state["MINUS"] = buttons["BACK"]
        new_state["HOME"] = False
        new_state["L"] = buttons["LEFT_SHOULDER"]
        new_state["R"] = buttons["RIGHT_SHOULDER"]
        new_state["ZL"] = True if triggers[0] > 0.49 else False
        new_state["ZR"] = True if triggers[1] > 0.49 else False

        new_state["L_STICK"]["PRESSED"] = buttons["LEFT_THUMB"]
        new_state["L_STICK"]["X_VALUE"] = math.floor(lx*100)
        new_state["L_STICK"]["Y_VALUE"] = math.floor(ly*100)
        new_state["R_STICK"]["PRESSED"] = buttons["RIGHT_THUMB"]
        new_state["R_STICK"]["X_VALUE"] = math.floor(rx*100)
        new_state["R_STICK"]["Y_VALUE"] = math.floor(ry*100)

        new_state["DPAD_UP"] = buttons["DPAD_UP"]
        new_state["DPAD_LEFT"] = buttons["DPAD_LEFT"]
        new_state["DPAD_RIGHT"] = buttons["DPAD_RIGHT"]
        new_state["DPAD_DOWN"] = buttons["DPAD_DOWN"]
        self.current_packet = new_state
        return new_state

    def automated_state(self):

        return self.current_packet
    def alter_button_state(self, button, state):
        if button is SwitchButtons.RS or button is SwitchButtons.LS:
            self.current_packet[button]["PRESSED"] = state
        else:
            self.current_packet[button] = state

    def unpress_button(self, button):
        self.alter_button_state(button, False)
        self.unpresses[button] = None

    def press_button(self, button, duration_in_seconds: float):
        self.alter_button_state(button, True)
        self.unpresses[button] = self.time_to_ticks(duration_in_seconds)


