import json

DIRECT_INPUT_PACKET = {
    # Sticks
    "L_STICK": {
        "PRESSED": False,
        "X_VALUE": 0,
        "Y_VALUE": 0,
        # Keyboard position calculation values
        "LS_UP": False,
        "LS_LEFT": False,
        "LS_RIGHT": False,
        "LS_DOWN": False
    },
    "R_STICK": {
        "PRESSED": False,
        "X_VALUE": 0,
        "Y_VALUE": 0,
        # Keyboard position calculation values
        "RS_UP": False,
        "RS_LEFT": False,
        "RS_RIGHT": False,
        "RS_DOWN": False
    },
    # Dpad
    "DPAD_UP": False,
    "DPAD_LEFT": False,
    "DPAD_RIGHT": False,
    "DPAD_DOWN": False,
    # Triggers
    "L": False,
    "ZL": False,
    "R": False,
    "ZR": False,
    # Joy-Con Specific Buttons
    "JCL_SR": False,
    "JCL_SL": False,
    "JCR_SR": False,
    "JCR_SL": False,
    # Meta buttons
    "PLUS": False,
    "MINUS": False,
    "HOME": False,
    "CAPTURE": False,
    # Buttons
    "Y": False,
    "X": False,
    "B": False,
    "A": False
}


def create_input_packet():
    return json.loads(json.dumps(DIRECT_INPUT_PACKET))
