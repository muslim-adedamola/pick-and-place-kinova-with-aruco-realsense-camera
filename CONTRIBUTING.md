# Contributing

Thanks for contributing!

## Getting started
1. Fork the repository and clone your fork.
2. Create a new branch:
   - `git checkout -b feature/my-change`

## Install
Create a virtual environment and install requirements:

- `pip install -r requirements.txt`

## Configuration (required for running on hardware)
Copy sample config files and fill in your calibration:

- `config/sample/camera_intrinsics.SAMPLE.yaml` → `config/camera_intrinsics.yaml`
- `config/sample/handeye_T_base_cam.SAMPLE.yaml` → `config/handeye_T_base_cam.yaml`
- `config/sample/task_params.SAMPLE.yaml` → `config/task_params.yaml`

**Do not commit real calibration files** (camera intrinsics and hand-eye transforms are hardware-specific).

## Code style
- Keep changes small and focused
- Prefer reading tunables from `config/task_params.yaml` instead of hard-coding

## Testing
If you have hardware:
- Verify ArUco detection
- Verify pose latching (SPACE)
- Verify approach → grasp → lift sequence

If you do not have hardware:
- Ensure scripts import and configs load correctly
- Run static checks if available

## Pull requests
In your PR description, include:
- What changed and why
- How you tested (hardware / no hardware)
- Any safety notes (workspace assumptions, offsets, etc.)
