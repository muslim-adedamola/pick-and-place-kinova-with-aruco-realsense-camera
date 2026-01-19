# Hand–Eye Calibration Procedure

This document describes the **hand–eye calibration procedure** used to compute
the rigid transformation between the **Intel RealSense camera frame** and the
**Kinova Gen3 robot base frame** for this project.

---

## Overview
- Camera: Intel RealSense D435i
- Robot: Kinova Gen3
- Calibration type: Eye-to-hand (camera fixed in workspace, i.e. fixed camera, moving robot)
- **Output:** Homogeneous transform from camera frame to robot base frame  
  (`T_base_C`)
  
---

## Steps Reference Workflow (MATLAB)
The resulting transform (`T_base_C`) is required to express object poses detected by the camera in the robot base coordinate frame.

In this setup, the camera is rigidly mounted in the workspace, while the robot moves a calibration target through different poses.

The calibration approach used in this project follows the **stationary camera (eye-to-hand)** workflow described by MathWorks:

🔗 **Estimate Pose of Fixed Camera Relative to Robot Base**  
https://www.mathworks.com/help/robotics/ug/estimate-pose-of-fixed-camera-relative-to-robot-base.html

This reference provides:
- MATLAB implementation details
- Visualization and validation steps

Rather than duplicating that content here, this document summarizes how the workflow was applied in this project and how the result is used in the code.

### High-Level Procedure Used

1. **Camera Intrinsics**
   - Camera intrinsics for the Intel RealSense were estimated (or obtained from
     prior calibration).
   - These intrinsics are required for accurate pose estimation.
   - For users unfamiliar with camera intrinsic calibration, the following
   references provide clear, step-by-step guidance using MATLAB tools:
   https://www.mathworks.com/help/vision/ug/using-the-single-camera-calibrator-app.html or https://www.youtube.com/watch?v=SoULhS9Ccgo

2. **Calibration Target**
   - A checkerboard calibration target was rigidly attached to the robot
     end-effector.
   - The target pose relative to the end-effector was assumed fixed.

3. **Data Collection**
   - The robot was moved through multiple, diverse poses within the camera’s field of view.
   - At each pose:
     - An image was captured by the fixed camera.
     - The corresponding robot end-effector pose relative to the robot base
       was recorded (via forward kinematics).

4. **Pose Estimation**
   - For each captured image:
     - The pose of the checkerboard relative to the camera frame was estimated
       using standard camera calibration techniques.
     - The pose of the end-effector relative to the robot base frame was known
       from the robot model.

5. **Hand–Eye Calibration**
   - Using the stationary-camera formulation, the fixed transform between the camera frame and the robot base frame was solved.

6. **Validation**
   - The resulting transform was validated by transforming calibration target
     points into the robot base frame and checking for consistency across poses.

---

### Output Used in This Repository

The final calibration result is the homogeneous transformation matrix:  (`T_base_C`) which is the camera frame expressed in the robot base frame.
This transform is hardcoded in `src/vision_aruco.py` and used to convert the detected ArUco pose from camera frame to robot base frame:
`T_base_O = T_base_C @ T_cam_O`

---

## Notes
- Calibration is hardware-specific
- Must be redone if camera mounting changes or camera is replaced or robot base frame defintion changes
