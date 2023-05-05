"""
This file contains the Modified Visual Odometry object developed for
CS766 project "Using Multipe Feature Detectors to Improve Visual Odometry Robustness"
To be used in conjunction with pyslam - https://github.com/luigifreda/pyslam 
"""

import numpy as np
import cv2
import math
import time

from feature_tracker_configs import FeatureTrackerConfigs
from visual_odometry import VisualOdometry
from feature_tracker import feature_tracker_factory


# This class uses the VisualOdometry object from pyslam and manipulates the outputs 
# to generate the modified VO results. Tested with 2 feature detection algorithms

class ModifiedVO(object):
    def __init__(self,cam,groundtruth,num_features,algo,method):
        self.cam = cam
        self.groundtruth = groundtruth
        self.num_features = num_features
        self.method = method

        self.w1 = None
        self.w2 = None

        assert len(np.unique(algo)) == 2, "Use 2 different feature detectors"
            
        self.tracker_config1 = getattr(FeatureTrackerConfigs, algo[0])
        self.tracker_config1['num_features'] = num_features
        self.feature_tracker1 = feature_tracker_factory(**self.tracker_config1)

        self.tracker_config2 = getattr(FeatureTrackerConfigs, algo[1])
        self.tracker_config2['num_features'] = num_features
        self.feature_tracker2 = feature_tracker_factory(**self.tracker_config2)

        self.vo1 = VisualOdometry(cam, groundtruth, self.feature_tracker1)
        self.vo2 = VisualOdometry(cam, groundtruth, self.feature_tracker2)
        
        self.traj3d_est = []
        self.traj3d_gt =[]
        self.avg_time = []

        #weights
        if not self.method:
            self.w1 = 0.5 
            self.w2 = 0.5

        self.draw_img1 = None
        self.draw_img2 = None

    def track(self,img,frame_id):
        start_time = time.time()
        self.vo1.track(img, frame_id)
        self.vo2.track(img, frame_id)
        tot_time = time.time() - start_time
        self.avg_time = np.append(self.avg_time,tot_time)
        self.draw_img1 = self.vo1.draw_img
        self.draw_img2 = self.vo2.draw_img

    def get_pos(self):
        x1, y1, z1 = self.vo1.traj3d_est[-1]
        x2, y2, z2 = self.vo2.traj3d_est[-1]
        w = self.w1/(self.w1 + self.w2)
        x, y, z = (1-w)*np.array([x1, y1, z1]) + w*np.array([x2, y2, z2])
        return x, y, z
    
    def get_gt(self):
        x_t, y_t, z_t = self.vo1.traj3d_gt[-1]
        return x_t, y_t, z_t


                    


