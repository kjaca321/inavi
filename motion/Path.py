import numpy as np
import cv2

class Path:
    def __init__(self):
        # intialize constant filters, camera settings
        self.min_gap_dist = 0.1; self.min_depth = 1.2; self.max_real_gap = .25 
        self.offset_constant = 50
        self.horz_FOV = 69 * np.pi / 180

    def find_target_point(self, regions, depth0, depth1280, dist): #regions[i][left_edge, right_edge, avg_depth]
        final_candidates = []
        
        # for every detected region
        for i in range(len(regions)):
            #calculate neighboring average depths based on region's index
            if i == 0:
                left_depth = depth0
                right_depth = regions[i+1][2]
            elif i == len(regions) - 1:
                left_depth = regions[i-1][2]
                right_depth = depth1280
            else:
                left_depth = regions[i-1][2]
                right_depth = regions[i+1][2]

            # calculate difference in neighboring depths and preliminary bias/offset
            depth_diff = right_depth - left_depth
            offset = self.offset_constant * depth_diff
            
            # maximum deviation from center pixel of current region
            diff = 10

            # bound offset to deviation
            offset = max(-diff, min(diff, offset))

            #calculate pixel x-position as average of left/right edges with offset
            x_px = (regions[i][0] + regions[i][1]) / 2 + offset

            # angle from center of x-pixel coordinate from proportions
            targ_angle = (x_px - 640) * self.horz_FOV/2 / 640

            # store average depth of current region, calculate target point (x and y)
            avg_depth = regions[i][2]
            target_x = avg_depth * np.sin(targ_angle)
            target_y = min(1, dist)
            target_point = (target_x, target_y)
            
            # angles of left/right edges from the same angle proportions
            left_edge_angle = (regions[i][0] - 640) * self.horz_FOV/2 / 640
            right_edge_angle = (regions[i][1] - 640) * self.horz_FOV/2 / 640

            # calculate width of the region from the avg depth and edge angles
            gap_distance = np.abs(avg_depth * np.sin(left_edge_angle)) + np.abs(avg_depth * np.sin(right_edge_angle))
            
            # if either the width is not long enough, or the region is not deep enough, skip this region
            if gap_distance < self.min_gap_dist or avg_depth < self.min_depth: 
                continue 

            # otherwise, assign a score to the region proportional to its depth and width
            score = avg_depth * min(gap_distance, self.max_real_gap)

            # add all potential regions to a list
            final_candidates.append([score, target_point, x_px, avg_depth])

        # if there are no potential regions, the path must be blocked, so return None
        if len(final_candidates) == 0:
            return None
        
        # sort by score to return the last one (highest score = most traversable)
        final_candidates.sort()

        # add a line to the output image representing the x-pixel coordinate for debugging
        image = cv2.imread('/robot_control/vision/debug_img/output_image.png')
        cv2.line(image, (int(final_candidates[-1][2]), 0), (int(final_candidates[-1][2]), 200), (255, 0, 0), 2)
        cv2.imwrite('/robot_control/vision/debug_img/output_image.png', image)

        # return the (x,y) coordinates of the best target point, with its average depth
        return final_candidates[-1][1][0], final_candidates[-1][1][0], [-1][3]