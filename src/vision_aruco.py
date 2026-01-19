import numpy as np
import cv2
import pyrealsense2 as rs
import threading

latest_T_base_O = None
pose_ready_event = threading.Event()
stop_event = threading.Event() 


# load hand-eye transform ( ^B T_C )
T_base_C = np.array([
                [0.0566, 0.6264,  -0.7775,  1.5330],
                [0.9963, -0.0858,  0.0034,  0.1072],
                [-0.0645,  -0.7748, -0.6289,  0.9694],
                [0,  0,  0,  1]])


# ArUco setup
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

marker_length = 0.04  

# Camera intrinsics
fx = 889.2416
fy = 888.8014
ppx = 625.8390
ppy = 376.3067

camera_matrix = np.array([
    [fx, 0, ppx],
    [0, fy, ppy],
    [0,    0,      1    ]
], dtype=np.float32)

dist_coeffs = np.array([
    0.1836,   # k1
    -0.3504,   # k2
    0.0,      # p1
    0.0,      # p2
    0.0       # k3
], dtype=np.float64)

print("Running. Press 'q' to quit.")


#vision loop
def vision_loop():
    global latest_T_base_O
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

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
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, marker_length, camera_matrix, dist_coeffs
                )

                rvec = rvecs[0]
                tvec = tvecs[0]

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

