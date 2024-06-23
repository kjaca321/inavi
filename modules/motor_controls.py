import numpy as np
from motion.Bezier import Bezier
from motion.Robot import Robot
from vision.obstacles import get_obstacles
from modules.voice_apis import play_audio
from motion.Path import Path

# function to be called when moving forward command is chosen
def move_ahead(desired_dist):
    # initialize robot and path 
    path_gen = Path()
    robot = Robot()

    # reset distance traveled
    robot.reset_pos()

    # repeat until robot forward distance meets desired distance
    curr_dist = robot.y_pos
    while curr_dist < desired_dist:
        # calculate remaining distance to move, retrieve obstacles
        delta_dist = desired_dist - curr_dist
        obstacle_arr = get_obstacles()

        # if no obstacles detected, just move forward
        if obstacle_arr[0] is None:
            robot.move_forward(min(delta_dist, 1)) # move at most 1m
            robot.stop()

            # update distance traveled, move to next iteration
            curr_dist = robot.y_pos
            continue

        # retrieve target point from path planner
        point = path_gen.find_target_point(obstacle_arr[0], obstacle_arr[1], obstacle_arr[2], delta_dist)
        
        # if there is no suitable target point, path must be blocked, notify and exit function
        if point is None:
            play_audio('/robot_control/gpt_modules/assets/blocked.wav')
            return
        
        # evaluate control point from avg depth of selected region
        x, y, depth = point
        c, k = 0.6, 0.1
        target = x, y
        control = x, max(0, min(c*y, np.e ** (k*depth)))

        # generate Bezier trajectory, follow path
        spline = Bezier(control, target)
        robot.follow_path(spline)
        robot.stop()
        
        # updated distance traveled
        curr_dist = robot.y_pos

# function to be called when turning command is chosen
def turn_robot(direction):
    # initialize robot
    robot = Robot()

    # turn angle depending on direction argument
    if 'left' in direction:
        robot.turnAngle(-90)
    elif 'right' in direction:
        robot.turnAngle(90)
    elif 'around' in direction:
        robot.turnAngle(180)
    robot.stop()
