import time
import HiwonderSDK.ros_robot_controller_sdk as rrc
import numpy as np
import math

class Robot:
    def __init__(self):
        # initialize robot state and constants
        self.rps = 0.98; self.circum = np.pi * 0.065 # diameter of wheel in meters
        self.x_pos, self.y_pos = 0,0
        self.board = rrc.Board()

        # set motion profile parameters and calculate/save velocity at each point
        self.max_vel, self.num_steps, self.num_regions = 100, 98, 7
        self.velocities = []
        a, v = 0, 0
        for n in range(self.num_steps):
            j = self.get_jerk(n)
            a += j
            self.velocities.append(v)
            v += a

    # define controlling motors for ease of use
    def move(self, v1, v2, v3, v4):
        self.board.set_motor_duty([[1, -v1], [2, v2], [3, -v3], [4, v4]]) # setting motor board control

    # define stopping motors for ease of use
    def stop(self):
        self.move(0, 0, 0, 0)

    # to reset accumulated movement in x/y directions
    def reset_pos(self):
        self.x_pos = 0; self.y_pos = 0

    # map nth point to a jerk profile that follows a (+, 0, -, 0, -, 0, +) pattern
    def get_jerk(self, n):
        V, N, k = self.max_vel, self.num_steps, self.num_regions
        return ((8*V*k*k)/(16*N*N - 10*k*N + k*k) 
                * np.cos(np.pi/2 * np.floor(n / 2 / k)) 
                * (-1) ** np.floor(.25 * np.floor(n / 2 / k)))

    # update x/y position through wheel velocites and time spent on those velocities
    def update_pos(self, v1_, v2_, v3_, v4_, t):
        # convert wheel velocities to linear velocity
        v1 = v1_/100*self.rps*self.circum 
        v2 = v2_/100*self.rps*self.circum
        v3 = v3_/100*self.rps*self.circum
        v4 = v4_/100*self.rps*self.circum

        # transform to translation velocities from holonomic kinematics
        vy = ((v1+v2)/2 + (v1+v3)/2 + (v2+v4)/2 + (v3+v4)/2) / 4
        vx = ((v1-vy) + (vy-v2) + (vy-v3) + (v4-vy)) / 4

        # calculate change in x/y position from time argument, update x/y position
        dx = vx*t
        dy = vy*t
        self.x_pos += dx
        self.y_pos += dy
    
    # moves forward with motion profile for a given distance
    def move_forward(self, dist):
        # split desired distance into num_steps equal sections
        section = dist / self.num_steps

        # iterate through number of steps (for motion profile)
        for i in range(self.num_steps):
            # get velocity at current step
            vel = self.velocities[i]

            # calculate time to move section distance from velocity
            t = 100 * section / vel / self.circum / self.rps

            # move the current step velocity for calculated time, update position
            self.move(vel, vel, vel, vel)
            time.sleep(t)
            self.update_pos(vel, vel, vel, vel, t)

        self.stop()

    # turns with motion profile for a given angle
    def turn_angle(self, angle):
        # convert given angle to radians, define robot trackwidth
        target, r = math.radians(angle), .1349 # trackwidth in meters
        
        # split desired angle into num_steps equal sections
        section = target / self.num_steps

        # iterate through number of steps (for motion profile)
        for i in range(self.num_steps):
            # get velocity at current step, conver to linear velocity
            vel = self.velocities[i]

            #convert to linear, then angular velocity, calculate signed time needed to turn
            w, t = vel* self.circum * self.rps / r, section / w

            # split sign and magnitude of time, turn with current speed for calculated time/direction 
            dirc, t = np.sign(t), np.abs(t)
            self.move(dirc*vel, -dirc*vel, dirc*vel, -dirc*vel)
            time.sleep(t)

        self.stop()
    
    # follows given path with motion profile
    def follow_path(self, spline):
        # iterate through each point (equivalent to self.num_steps - 1) due to uniform point density
        for i in range(len(spline.array()) - 1):
            # get velocity at current point from profile
            v = self.velocities[i]

            # get locations of current and next point from Bezier uniform array
            curr, nxt = spline.array()[i], spline.array()[i+1]

            # calculate change in x/y positions from curr/next points
            dx, dy =  nxt[0] - curr[0], nxt[1] - curr[1]

            # calculate angle change from dx, dy, calculate translation velocities
            dtheta = np.arctan2(dy, dx)
            vx = v * np.cos(dtheta)
            vy = v * np.sin(dtheta)

            # change in distance traveled (through distance formula)
            dr = np.sqrt(dx ** 2 + dy ** 2)

            # time needed to traverse dr (equivalent to traversing (dx, dy) due to holonomic kinematics)
            t = dr / self.circum / self.rps

            # convert translation velocities to wheel velocities
            vels = [vx+vy, vy-vx, vy-vx, vx+vy]
            abs_vels = []

            # to prevent motor saturation, maintain ratio/differences between wheel velocities 
            for i in vels:
                abs_vels.append(np.abs(i))
            ratio = np.max(abs_vels) / 100.0
            for i in range(len(vels)):
                # making sure no wheel velocity exceeds the max (100%)
                vels[i] /= ratio

            # when starting to move (only first index)
            if i == 0:
                # determine maxed versions of wheel velocities as sign variations of 100%
                polar_vels = []
                for i in vels:
                    polar_vels.append(np.sign(i) * 100)

                # to overcome possible friction/inertia, full throttle motors for a short period of time
                self.move(polar_vels[0], polar_vels[1], polar_vels[2], polar_vels[3])
                time.sleep(.01)

            # move with the calculated wheel velocities for the calculated time, update position
            self.move(vels[0], vels[1], vels[2], vels[3])
            time.sleep(t)
            self.update_pos(vels[0], vels[1], vels[2], vels[3], t)

        self.stop()