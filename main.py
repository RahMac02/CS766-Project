"""
Main function to use Modified VO for CS766 project "Using Multipe Feature Detectors to Improve
Visual Odometry Robustness" 
To be used in conjunction with pyslam - https://github.com/luigifreda/pyslam 
"""

import numpy as np
import cv2
import math
import time

from config import Config

from visual_odometry import VisualOdometry
from camera  import PinholeCamera
from ground_truth import groundtruth_factory
from dataset import dataset_factory

#from mplot3d import Mplot3d
#from mplot2d import Mplot2d
from mplot_thread import Mplot2d, Mplot3d

from feature_tracker import feature_tracker_factory, FeatureTrackerTypes 
from feature_manager import feature_manager_factory
from feature_types import FeatureDetectorTypes, FeatureDescriptorTypes, FeatureInfo
from feature_matcher import feature_matcher_factory, FeatureMatcherTypes

from feature_tracker_configs import FeatureTrackerConfigs
from mod_vo import ModifiedVO


"""
use or not pangolin (if you want to use it then you need to install it by using the script install_thirdparty.sh)
"""
kUsePangolin = False  

if kUsePangolin:
    from viewer3D import Viewer3D




if __name__ == "__main__":

    config = Config()

    dataset = dataset_factory(config.dataset_settings)

    groundtruth = groundtruth_factory(config.dataset_settings)

    cam = PinholeCamera(config.cam_settings['Camera.width'], config.cam_settings['Camera.height'],
                        config.cam_settings['Camera.fx'], config.cam_settings['Camera.fy'],
                        config.cam_settings['Camera.cx'], config.cam_settings['Camera.cy'],
                        config.DistCoef, config.cam_settings['Camera.fps'])


    num_features=2000  # how many features do you want to detect and track?

    # select your tracker configuration (see the file feature_tracker_configs.py) 
    # LK_SHI_TOMASI, LK_FAST
    # SHI_TOMASI_ORB, FAST_ORB, ORB, BRISK, AKAZE, FAST_FREAK, SIFT, ROOT_SIFT, SURF, SUPERPOINT, FAST_TFEAT

    #initialze modified VO object
    #algo = [feat_detector1, feat_detector2]
    #method = 0 for direct average
    #method = 1 for weighted average

    algo = ['BRISK', 'LK_FAST']
    mod_vo = ModifiedVO(cam, groundtruth, num_features, algo, method=1)

    #initial weight = decision factor
    mod_vo.w1 = 1/0.27936426461616737
    mod_vo.w2 = 1/0.29250398206490835
    
    # print("Weights:", mod_vo.w1, mod_vo.w2)

    is_draw_traj_img = True
    traj_img_width = 400
    traj_img_height = 800
    traj_img = 255*np.ones((traj_img_height, traj_img_width, 3), dtype=np.uint8)
    half_traj_img_width = int(0.5*traj_img_width)
    half_traj_img_height = int(0.5*traj_img_height)
    draw_scale = 1

    is_draw_3d = False
    if is_draw_3d:
        if kUsePangolin:
            viewer3D = Viewer3D()
        else:
            plt3d = Mplot3d(title='3D trajectory')

    is_draw_err = True 
    err_plt = Mplot2d(xlabel='img id', ylabel='m',title='error')

    is_draw_matched_points = False 
    matched_points_plt = Mplot2d(xlabel='img id', ylabel='# matches',title='# matches')

    img_id = 0
    
    # initialize variable to track error
    err = 0

    while dataset.isOk() and img_id<840:

        img = dataset.getImage(img_id)

        if img is not None:
            
            mod_vo.track(img, img_id)

            if(img_id > 2):	       # start drawing from the third image (when everything is initialized and flows in a normal way)

                x, y, z = mod_vo.get_pos()
                x_true, y_true, z_true = mod_vo.get_gt()

                if is_draw_traj_img:      # draw 2D trajectory (on the plane xz)
                    draw_x, draw_y = int(draw_scale*x) + half_traj_img_width, half_traj_img_height - int(draw_scale*z)
                    true_x, true_y = int(draw_scale*x_true) + half_traj_img_width, half_traj_img_height - int(draw_scale*z_true)
                    cv2.circle(traj_img, (draw_x, draw_y), 1,(img_id*255/4540, 255-img_id*255/4540, 0), 1)   # estimated from green to blue
                    cv2.circle(traj_img, (true_x, true_y), 1,(0, 0, 255), 1)  # groundtruth in red
                    # write text on traj_img
                    
                    cv2.line(traj_img, (20,35), (60,35), (0,0,255), 2)
                    cv2.line(traj_img, (20,70), (60,70), (0,255,0), 2 )
                    
                    text1 = "Ground Truth"
                    text2 = "Estimated Path"
                    cv2.putText(traj_img, text1, (70, 40), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1, 8)
                    cv2.putText(traj_img, text2, (70, 75), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 1, 8)
                    # show 		
                    cv2.imshow('Trajectory', traj_img)

                if is_draw_3d:           # draw 3d trajectory 
                    if kUsePangolin:
                        viewer3D.draw_vo(vo)   
                    else:
                        plt3d.drawTraj(vo.traj3d_gt,'ground truth',color='r',marker='.')
                        plt3d.drawTraj(vo.traj3d_est,'estimated',color='g',marker='.')
                        plt3d.refresh()

                if is_draw_err:         # draw error signals 
                    errx = [img_id, math.fabs(x_true-x)]
                    erry = [img_id, math.fabs(y_true-y)]
                    errz = [img_id, math.fabs(z_true-z)] 
                    err_plt.draw(errx,'err_x',color='g')
                    err_plt.draw(erry,'err_y',color='b')
                    err_plt.draw(errz,'err_z',color='r')
                    err_plt.refresh() 
                    err = err + np.sqrt(errx[1]**2 + erry[1]**2 + errz[1]**2)        # update error

                if is_draw_matched_points:
                    matched_kps_signal = [img_id, vo.num_matched_kps]
                    inliers_signal = [img_id, vo.num_inliers]                    
                    matched_points_plt.draw(matched_kps_signal,'# matches',color='b')
                    matched_points_plt.draw(inliers_signal,'# inliers',color='g')                    
                    matched_points_plt.refresh()                    


            # draw camera image 
            # cv2.imshow('BRISK Features', mod_vo.draw_img1)
            # cv2.imshow('FAST Features', mod_vo.draw_img2)				

        # press 'q' to exit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Avg Time: ", np.average(mod_vo.avg_time))
            print("Avg Error: ", err/img_id)
            break
        img_id += 1

    #print('press a key in order to exit...')
    #cv2.waitKey(0)

    if is_draw_traj_img:
        print('saving map.png')
        cv2.imwrite('map.png', traj_img)
    if is_draw_3d:
        if not kUsePangolin:
            plt3d.quit()
        else: 
            viewer3D.quit()
    if is_draw_matched_points is not None:
        matched_points_plt.quit()
    if is_draw_err:
        print('saving err.png')
        err_plt.quit()
    # print average computation time & error
    print("Avg Time: ", np.average(mod_vo.avg_time))
    print("Avg Error: ", err/img_id)
    cv2.destroyAllWindows()