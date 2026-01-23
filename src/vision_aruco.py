import numpy as np
import cv2
import pyrealsense2 as rs
import threading
from config_loader import load_configs


cfg = load_configs()
latest_T_base_O = None
pose_ready_event = threading.Event()
stop_event = threading.Event() 


# load hand-eye transform ( ^B T_C )
# hand-eye: T_base_cam
T_base_C = np.array(cfg["handeye"]["T_base_cam"]["matrix"], dtype=float)

# ArUco setup
dict_name = cfg["task"]["aruco"].get("dictionary", "DICT_4X4_50")
aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
target_id = cfg["task"]["aruco"].get("target_id", None)

marker_length = float(cfg["task"]["aruco"]["marker_length_m"])

# camera intrinsics
Kcfg = cfg["camera"]["intrinsics"]
fx = float(Kcfg["fx"])
fy = float(Kcfg["fy"])
cx = float(Kcfg["cx"])
cy = float(Kcfg["cy"])

#camera matrix
camera_matrix = np.array(
    [[fx, 0.0, cx],
     [0.0, fy, cy],
     [0.0, 0.0, 1.0]],
    dtype=np.float32
)

#distortion coefficients is in the form [k1, k2, p1, p2, k3] in cam_intrinsics yaml file
dist_coeffs = np.array(cfg["camera"]["distortion"]["coeffs"], dtype=np.float64)

print("Running. Press 'q' to quit.")


W = int(cfg["camera"]["camera"]["width"])
H = int(cfg["camera"]["camera"]["height"])
FPS = int(cfg["camera"]["camera"]["fps"])

#vision loop
def vision_loop():
    global latest_T_base_O
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, W, H, rs.format.bgr8, FPS)
    config.enable_stream(rs.stream.depth, W, H, rs.format.z16, FPS)

    pipeline.start(config)

    try:
        for _ in range(30):
            pipeline.wait_for_frames()

        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue

            img = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                ids_flat = ids.flatten().tolist()

                if target_id is not None and int(target_id) in ids_flat:
                    idx = ids_flat.index(int(target_id))
                else:
                    idx = 0

                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, marker_length, camera_matrix, dist_coeffs
                )

                rvec = rvecs[idx]
                tvec = tvecs[idx]

                R_cam_O, _ = cv2.Rodrigues(rvec)

                T_cam_O = np.eye(4)
                T_cam_O[:3, :3] = R_cam_O
                T_cam_O[:3, 3] = tvec.reshape(3)

                latest_T_base_O = T_base_C @ T_cam_O

                # Visualization
                cv2.aruco.drawDetectedMarkers(img, corners, ids)
                cv2.drawFrameAxes(
                    img, camera_matrix, dist_coeffs,
                    rvec, tvec, 0.05
                )

                cv2.putText(
                    img,
                    f"Base XYZ: {latest_T_base_O[0,3]:.3f}, "
                    f"{latest_T_base_O[1,3]:.3f}, "
                    f"{latest_T_base_O[2,3]:.3f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,255,0), 2
                )

            cv2.imshow("ArUco Detection", img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and latest_T_base_O is not None:
                print("[VISION] Pose latched")
                pose_ready_event.set()

            elif key == ord('q'):
                print("[VISION] Quit requested")
                stop_event.set()
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

