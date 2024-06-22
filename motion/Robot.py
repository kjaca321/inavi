import sys
sys.path.append('/home/pi/TurboPi/')
import time
import HiwonderSDK.ros_robot_controller_sdk as rrc
import numpy as np

class Robot:
    def __init__(self):
        self.rps = 0.98; self.circum = np.pi * 0.065 # diameter of wheel in meters
        self.x_pos, self.y_pos = 0,0
        self.board = rrc.Board()
        self.max_vel, self.num_steps, self.num_regions = 100, 98, 7
        self.velocities = []
        a, v = 0, 0
        for n in range(self.num_steps):
            j = self.get_jerk(n)
            a += j
            self.velocities.append(v)
            v += a

    def move(self, v1, v2, v3, v4):
        self.board.set_motor_duty([[1, -v1], [2, v2], [3, -v3], [4, v4]])
        time.sleep(0.001)

    def reset_pos(self):
        self.x_pos = 0; self.y_pos = 0

    def get_jerk(self, n):
        V, N, k = self.max_vel, self.num_steps, self.num_regions
        return ((8*V*k*k)/(16*N*N - 10*k*N + k*k) 
                * np.cos(np.pi/2 * np.floor(n / 2 / k)) 
                * (-1) ** np.floor(.25 * np.floor(n / 2 / k)))

    def update_pos(self, v1_, v2_, v3_, v4_, t):
        v1 = v1_/100*self.rps*self.circum 
        v2 = v2_/100*self.rps*self.circum
        v3 = v3_/100*self.rps*self.circum
        v4 = v4_/100*self.rps*self.circum
        vy = ((v1+v2)/2 + (v1+v3)/2 + (v2+v4)/2 + (v3+v4)/2) / 4
        vx = ((v1-vy) + (vy-v2) + (vy-v3) + (v4-vy)) / 4
        dx = vx*t
        dy = vy*t
        self.x_pos += dx
        self.y_pos += dy
    
    def move_forward(self, dist):
        t = dist / self.circum / self.rps
        self.move(100, 100, 100, 100)
        time.sleep(t)
        self.stop()
        self.update_pos(100, 100, 100, 100, t)

    def turn_angle(self, angle):
        avg_speed = np.mean(self.velocities)
        v = self.circum * avg_speed/100
        w, t = v/r, angle * np.pi / 180 / w
        dirc, t = np.sign(t), np.abs(t)
        for n in range(self.num_steps):
            speed, r = self.velocities[n], 5.31
            self.move(dirc*speed, -dirc*speed, dirc*speed, -dirc*speed)
            time.sleep(t/self.num_steps)
        self.stop()

    def stop(self):
        self.move(0, 0, 0, 0)

    
    def follow_path(self, spline):
        for i in range(len(spline.array()) - 1):
            v = self.velocities[i]
            curr, nxt = spline.array()[i], spline.array()[i+1]
            dx =  nxt[0] - curr[0]
            dy = nxt[1] - curr[1]
            theta = np.arctan2(dy, dx)
            vx = v * np.cos(theta)
            vy = v * np.sin(theta)
            dr = np.sqrt(dx ** 2 + dy ** 2)
            t = dr / self.circum / self.rps * 1.15
            vels = [vx+vy, vy-vx, vy-vx, vx+vy]
            av = []
            for i in vels:
                av.append(np.abs(i))
            r = np.max(av) / 100.0
            for i in range(len(vels)):
                vels[i] /= r
                if np.abs(vels[i]) < 0.0001:
                    vels[i] = 0
                vels[i] = int(vels[i])

            mvels = []
            for i in vels:
                mvels.append(np.sign(i) * 100)
            
            for i in range(len(mvels)):
                mvels[i] = int(mvels[i])

            if i == 0:
                self.move(mvels[0], mvels[1], mvels[2], mvels[3])
                time.sleep(.05)

            self.move(vels[0], vels[1], vels[2], vels[3])
            time.sleep(t)
            self.update_pos(vels[0], vels[1], vels[2], vels[3], t)

        self.stop()