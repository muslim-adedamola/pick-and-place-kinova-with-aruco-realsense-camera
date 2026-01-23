# Vision-Guided Pick-and-Place with Kinova Gen3

## Demo

<p align="center">
  <img src="assets/demo3.gif" width="350">
</p>


This repository is intended for educational and demonstration purposes. It contains a real-world pick-and-place project implemented on a Kinova Gen3 robotic arm, using an Intel RealSense RGB-D camera and an ArUco marker for object pose estimation.

It demonstrates a minimal but complete vision-to-manipulation pipeline in camera perception → pose estimation → frame transformation → Cartesian motion → gripper execution.

The ArUco marker is attached to the object to be picked, and the robot executes a safe approach, grasp, and lift sequence based on the estimated pose.

This project is intentionally **simple and explicit**, and is aimed at:

* Beginners learning real-robot manipulation  
* Students transitioning from simulation to hardware  
* Engineers interested in vision-guided robotic control

---

**System Overview**

			Intel Real Sense Camera  
				    ↓  
            ArUco Detection (OpenCV)  
                    ↓  
          Object Pose in Camera Frame  
                    ↓  
      Hand–Eye Transform (Camera → Robot Base)  
                    ↓  
           Approach / Grasp / Lift Poses  
                    ↓  
          Kinova Gen3 Cartesian Motion  
                    ↓  
            Gripper Open / Close

---

**Hardware Used**

* **Robot:** Kinova Gen3  
* **Gripper**: Robotiq 2f140  
* **Camera**: Intel RealSense (D435i)  
* **Marker**: ArUco (DICT\_4X4\_50)

---

**Software Dependencies**

* Python ≥ 3.9  
* Kinova Kortex API (Python)  
* OpenCV (with contrib modules)  
* Intel RealSense SDK  
* Ubuntu OS used

---

**Install Python dependencies**:  
```bash  
pip install -r requirements.txt  
```  
**N:B**  
The Kinova Kortex API (python) and Intel RealSense SDK must be installed separately.  
[Install](https://github.com/Kinovarobotics/Kinova-kortex2_Gen3_G3L/tree/master/api_python/examples#install-kinova-kortex-python-api-and-required-dependencies) Kinova Kortex Api  
[Install](https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md#installing-the-packages) intelrealsense SDK

**Running the Project:**  
```bash  
python src/pick.py --ip <ROBOT_IP> --username admin --password admin  
```
**Controls**

* **SPACE** — latch the currently detected object pose and execute pick  
* **q** — quit the program safely

---

**Calibration Procedures and Assumptions**

This implementation assumes:

* Camera intrinsics are known  
* Hand–eye calibration (camera to robot base transform) is precomputed

These values are hardware-specific and must be recalibrated if the setup changes. [Click here for the calibration procedure](docs/handeye_calibration.md)

---

**Code Structure**

```bash  
src/  
├─ pick.py                            # Main entry point  
├─ vision\_aruco.py                   # ArUco detection and pose estimation  
├─ move\_cartesian.py                 # Cartesian waypoint motion  
├─ gripper\_control.py                # Gripper open / close  
├─ grasp\_utils.py                    # Approach, grasp, lift pose computation  
└─ utilities.py                       # Robot connection utilities
```
