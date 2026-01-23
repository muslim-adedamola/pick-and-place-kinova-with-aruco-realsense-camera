import threading
import utilities
import vision_aruco

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from move_cartesian import move_to_cartesian_pose
from grasp_utils import compute_approach_and_grasp
from gripper_control import open_gripper, close_gripper
from config_loader import load_configs

import time

cfg = load_configs()
approach_offset = float(cfg["task"]["grasp"]["approach_offset_m"])
grasp_offset = float(cfg["task"]["grasp"]["grasp_offset_m"])
lift_offset = float(cfg["task"]["grasp"]["lift_offset_m"])


def main():

    args = utilities.parseConnectionArguments()

    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)

        vision_thread = threading.Thread(target=vision_aruco.vision_loop)  
        vision_thread.start()

        print("[INFO] Press SPACE in vision window to move robot. Press q to quit.")

        while not vision_aruco.stop_event.is_set():
            # Wait for a pose latch OR quit
            vision_aruco.pose_ready_event.wait(timeout=0.1)
            if vision_aruco.stop_event.is_set():
                break

            if vision_aruco.pose_ready_event.is_set():
                # latch pose
                T_base_O = vision_aruco.latest_T_base_O.copy()

                # IMPORTANT: clear event so another SPACE can trigger later
                vision_aruco.pose_ready_event.clear()

                # Compute grasp frames
                T_base_A, _, T_base_L = compute_approach_and_grasp(T_base_O, approach_offset=approach_offset, 
                                                                   grasp_offset=grasp_offset, lift_offset=lift_offset)

                open_gripper(base)
                time.sleep(0.5)

                if not move_to_cartesian_pose(base, T_base_A):
                    print("[ERROR] Failed to reach approach pose")
                    continue
                
                close_gripper(base)
                time.sleep(0.5)

                # Lift
                if not move_to_cartesian_pose(base, T_base_L):
                    print("[ERROR] Failed to retreat")
                    continue

        # ensure clean exit
        vision_aruco.stop_event.set()
        vision_thread.join()


if __name__ == "__main__":
    main()
