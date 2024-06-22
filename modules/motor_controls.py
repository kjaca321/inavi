import sys
sys.path.append('/home/pi/TurboPi/')
sys.path.append('/home/pi/TurboPi/robot_control/vision/')
sys.path.append('/home/pi/TurboPi/robot_control/gpt_modules/')

import time
import numpy as np
from motion.Bezier import Bezier
from motion.Robot import Robot
from vision.obstacles import get_obstacles
from modules.voice_apis import play_audio
from motion.Path import Path

def move_ahead(desired_dist):
    pathGen = Path()
    robot = Robot()
    robot.stop()
    robot.reset_pos()
    curr_dist = robot.y_pos
    while curr_dist < desired_dist - 0.1:
        delta_dist = desired_dist - curr_dist
        obstacle_arr = get_obstacles()
        if obstacle_arr[0] is None:
            robot.move_forward(min(delta_dist, 1)) # move at most 1m
            robot.stop()
            curr_dist = robot.y_pos
            continue

        point = pathGen.find_target_point(obstacle_arr[0], obstacle_arr[1], obstacle_arr[2], delta_dist)
        if point is None:
            play_audio('/home/pi/TurboPi/robot_control/gpt_modules/assets/blocked.wav')
            return
        x, y = point
        c, k = 0.6, 0.1
        control = x, max(0, min(c*y, np.e ** (k * y)))
        target =  (x, y)
        spline = Bezier(control, target)
        time.sleep(0.1)
        robot.follow_path(spline)
        robot.stop()
        curr_dist = robot.y_pos

def turn_robot(direction):
    robot = Robot()
    if 'left' in direction:
        robot.turnAngle(-90)
    elif 'right' in direction:
        robot.turnAngle(90)
    elif 'around' in direction:
        robot.turnAngle(180)
    robot.stop()
