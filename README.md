# UW Madison: CS766-Project
# Using Multiple Feature Detectors to Improve Visual Odometry Robustness

---
## Usage

This repo contains the custom modified files to run the modified visual odometry(VO). 
The project uses the [PySLAM](https://github.com/luigifreda/pyslam) to implement the background VO algorithms.
Follow pySLAM installation instructions and then copy files from this repo inside the pySLAM directory to run this project.

---

To run the baseline single feature detector based VO, run the following command inside the pySLAM directory:

`python3 main_vo.py`

To run the modified VO which uses 2 different feature detectors to improve perfromance, run the following command inside pySLAM directory:

`python3 main.py`

---

To modify the feature detector algorithms, follow instructions in the *main.py*. 
