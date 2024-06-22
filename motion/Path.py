import numpy as np
import cv2

class Path:
    def __init__(self):
        self.min_gap_dist = 0.1; self.min_depth = 1.2; self.max_real_gap = .25 
        self.scaleConstant = 50
        self.horz_FOV = 69 * np.pi / 180

    def find_target_point(self, regions, depth0, depth1280, dist): #regions[i][leftEdge, rightEdge, avg_depth]
        final_candidates = []
        for i in range(len(regions)):
            if i == 0:
                left_depth = depth0
                right_depth = regions[i+1][2]
            elif i == len(regions) - 1:
                left_depth = regions[i-1][2]
                right_depth = depth1280
            else:
                left_depth = regions[i-1][2]
                right_depth = regions[i+1][2]
            depth_diff = right_depth - left_depth
            scale = self.scaleConstant * depth_diff
            diff = 10
            scale = max(-diff, min(diff, scale))

            x_px = (regions[i][0] + regions[i][1]) / 2 + scale

            targ_angle = (x_px - 640) * self.horz_FOV/2 / 640
            avg_depth = regions[i][2]
            target_x = avg_depth * np.sin(targ_angle) * np.cos(targ_angle)
            target_y = min(1, dist)
            target_point = (target_x, target_y)
            
            px_gap = np.abs(regions[i][0] - regions[i][1])
            left_edge_angle = (regions[i][0] - 640) * self.horz_FOV/2 / 640
            right_edge_angle = (regions[i][1] - 640) * self.horz_FOV/2 / 640
            gap_distance = np.abs(avg_depth * np.sin(left_edge_angle)) + np.abs(avg_depth * np.sin(right_edge_angle))
            if gap_distance < self.min_gap_dist or avg_depth < self.min_depth: 
                continue 
            score = regions[i][2] * min(gap_distance, self.max_real_gap)
            final_candidates.append([score, target_point, x_px]) # highest score is the most traversable

        if len(final_candidates) == 0:
            return None
        final_candidates.sort()
        image = cv2.imread('/home/pi/TurboPi/robot_control/vision/debug_img/output_image.png')
        cv2.line(image, (int(final_candidates[-1][2]), 0), (int(final_candidates[-1][2]), 200), (255, 0, 0), 2)
        cv2.imwrite('/home/pi/TurboPi/robot_control/vision/debug_img/output_image.png', image)
        return final_candidates[-1][1]