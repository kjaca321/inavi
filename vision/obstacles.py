import cv2
import glob
import numpy as np
import math
import time
import os

from real_sense_cam import get_depth_arr

# Function to calculate the slope of a line
def calculate_slope(x1, y1, x2, y2):
    if x2 - x1 == 0:  # Prevent division by zero
        return float('inf')
    return (y2 - y1) / (x2 - x1)

def get_neighborhood_depth(x, y, dists, a=2):
    avg = dists[y-a:y+a,x-a:x+a].mean()
    return avg if not np.isnan(avg) else dists[y][x]


def get_obstacles():

    # get depth view
    depth_colormap, dists = get_depth_arr()
    depth_colormap = depth_colormap[200:400,:,:]
    dists = dists[200:400,:]
    cv2.imwrite('/home/pi/TurboPi/robot_control/vision/debug_img/depth.png', depth_colormap)

    # get rgb view
    os.system('v4l2-ctl -d /dev/video4 -c auto_exposure=1')
    os.system('v4l2-ctl -d /dev/video4 -c exposure_time_absolute=500')
    os.system('ffmpeg -y -f v4l2 -input_format yuyv422 -video_size 1280x720 -i /dev/video4 -vframes 5 -q:v 2 /home/pi/TurboPi/robot_control/vision/debug_img/color_img/color_%04d.png')

    image_files = glob.glob('/home/pi/TurboPi/robot_control/vision/debug_img/color_img/color_*.png')

    if len(image_files) == 0:
        return

    for img_file in image_files:
        # process rgb with hough lines
        image = cv2.imread(img_file)
        image = image[200:400,:,:]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=15, minLineLength=15, maxLineGap=20)

        slope_threshold_degrees = 75
        slope_threshold = math.tan(math.radians(slope_threshold_degrees))

        # collect vert lines based on slope
        vert_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = calculate_slope(x1, y1, x2, y2)
                if abs(slope) > slope_threshold:  # Filter lines with slope only atleast 80 degrees
                    vert_lines.append((x1, y1, x2, y2))
    

    # discard lines that are too deep, or too close to each other
    prev_x1 = None
    vert_lines.sort()
    final_lines = []
    pixels_apart = 25
    depth_filter = 0.9

    for line in vert_lines:
        x1, y1, x2, y2 = line
        if get_neighborhood_depth(x1,y1,dists) > depth_filter:
            continue
        if (not prev_x1) or (x1 - prev_x1 > pixels_apart):
            prev_x1 = x1
            final_lines.append(line)

    region_lines = []

    # draw lines onto img for debug and save
    for line in final_lines:
        x1, y1, x2, y2 = line
        region_lines.append(x1)
        cv2.line(image, (x1, 0), (x1, 200), (0, 0, 255), 2)
        # cv2.line(image, (x1, y1), (x2,y2), (0, 0, 255), 2)

    cv2.line(image, (640, 0), (640, 200), (0, 255, 0), 2)
    cv2.imwrite('/home/pi/TurboPi/robot_control/vision/debug_img/output_image.png', image)

    stacked = np.vstack((depth_colormap, image))
    cv2.imwrite('/home/pi/TurboPi/robot_control/vision/debug_img/compare.png', stacked)

    # reformat
    region_lines = [0] + region_lines + [1280]
    idx_depth_arr = []
    for i in range(len(region_lines)-1):
        l, r = region_lines[i], region_lines[i+1]
        select_dists = np.array(dists[:,l:r])
        select_dists = select_dists[select_dists <= np.percentile(select_dists, 99)]
        idx_depth_arr.append((l, r, np.mean(select_dists)))

    if len(idx_depth_arr) <= 1:
        idx_depth_arr = None
    depth_left_edge = dists[:,:2].mean()
    depth_right_edge = dists[:,1278:].mean()

    return idx_depth_arr, depth_left_edge, depth_right_edge

