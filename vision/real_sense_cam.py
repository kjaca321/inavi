
import pyrealsense2 as rs
import numpy as np
import cv2
import time

def get_depth_arr():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    depth_sensor = device.first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)
    base_time = time.time()
    while time.time() - base_time < 0.25:
        depth_frame = pipeline.wait_for_frames().get_depth_frame()
        time.sleep(0.05)
    
    pipeline.stop()

    depth_arr = np.asanyarray(depth_frame.get_data())

    visual = cv2.applyColorMap(cv2.convertScaleAbs(depth_arr, alpha=0.03), cv2.COLORMAP_JET)
    distance = depth_arr * depth_scale

    # rescale arrays
    y,x = distance.shape

    # angle ratios
    new_x = int(x * (69/87))
    new_y = int(y * (42/58))

    x_offset = int((x - new_x) / 2)
    y_offset = int((y - new_y) / 2)

    # refactor dist array
    cropped_dist = distance[y_offset:y_offset+new_y,x_offset:x_offset+new_x]
    resized_dist = cv2.resize(cropped_dist, (1280, 720), interpolation=cv2.INTER_LINEAR)

    # refactor colormap
    cropped_visual = visual[y_offset:y_offset+new_y,x_offset:x_offset+new_x,:]
    resized_visual = cv2.resize(cropped_visual, (1280, 720), interpolation=cv2.INTER_LINEAR)

    return resized_visual, resized_dist
