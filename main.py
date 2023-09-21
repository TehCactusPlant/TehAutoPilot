from time import sleep

from nxbt.nxbt import Nxbt, PRO_CONTROLLER

#Loop
if __name__ == "__main__":
    nx = Nxbt()
    controller_index = nx.create_controller(
        PRO_CONTROLLER,
        reconnect_address=None)
    print(f"Controller created at index {controller_index}")
    sleep(15)

    print(f"Removing controller at index {controller_index}")
    nx.remove_controller(controller_index)
