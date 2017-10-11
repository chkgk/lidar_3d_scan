from dep.lidar_lite import Lidar_Lite
from dep.StepMotorDriver import StepMotorDriver
import pigpio

from math import sin, cos, radians, sqrt
import time

import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from pprint import pprint
import pickle

pi = pigpio.pi()


Motor = StepMotorDriver(6, 13, 19, 26, True)

Lidar = Lidar_Lite()
connected = Lidar.connect(1)

if connected < -1:
    exit("Not Connected")

measurements = []
measurements_3d = []

def servo_degree(degree):
    cycle =  int(round((34000-75000)/90 * float(degree)+75000))
    pi.hardware_PWM(12, 50, cycle)


def measure(step, reversed):
    global measurements
    measurements.append((step, Lidar.getSure()))


def measure_3d(pan_step, tilt_step, tilt_deg = 5):
    global measurements_3d
    
    pan_degree = pan_step_to_degree(pan_step)

    tilt_degree = tilt_step_to_degree(tilt_step, tilt_deg)

    measurements_3d.append((pan_degree, tilt_degree, Lidar.getSure()))

def turn_measure(steps):
    Motor.set_speed(1)
    Motor.make_steps(steps, measure)
    Motor.set_speed(-1)
    Motor.make_steps(steps)


def turn_measure_3d(pan_steps, tilt_steps, tilt_deg = 5):
    speed = 1
    Motor.set_speed(1)
    for tilt_step in range(tilt_steps+1):
        servo_degree(tilt_step * tilt_deg)
        time.sleep(0.2)
        Motor.make_steps(pan_steps, measure_3d, tilt_step)
        speed = -speed
        Motor.set_speed(speed)

    if tilt_steps % 2 == 0:
        print('going back to start')
        Motor.set_speed(-1)
        Motor.make_steps(pan_steps)

    for tilt_step in reversed(range(tilt_steps)):
        target = tilt_step*tilt_deg
        servo_degree(target)
        time.sleep(0.1)



def get_coordinates_2d(measurements, max_steps = 512):
    coordinates = []
    for step, distance in measurements:
        coordinates.append(angle_distance_to_coordinates(pan_step_to_degree(step, max_steps), distance))

    return coordinates

def get_coordinates_3d(measurements):
    coordinates = []
    for m in measurements:
        pan_deg, tilt_deg, dist = m

        # phi = 90 - pan_deg
        # theta = 90 - tilt_deg

        phi = 90 - pan_deg
        theta = 90 - tilt_deg
        

        x = dist * sin(radians(theta)) * cos(radians(phi))
        y = dist * sin(radians(theta)) * sin(radians(phi))
        z = dist * cos(radians(theta))

        # y = dist * sin(radians(theta)) * cos(radians(phi))
        # x = dist * sin(radians(theta)) * sin(radians(phi))
        # z = dist * cos(radians(theta))
        
        print(phi, theta, dist, x, y, z)

        coordinates.append((x, y, z))
    return coordinates

    
def pan_step_to_degree(step, max_steps = 512):
    degree_per_step = 360 / max_steps
    return step * degree_per_step

def tilt_step_to_degree(step, step_deg = 5):
    return step * step_deg


def pan_degree_to_step(degree, max_steps = 512):
    step_per_degree = max_steps / 360
    return int(round(degree * step_per_degree))

def tilt_degree_to_step(degree, degree_per_step = 5):
    return int(degree/degree_per_step)

def angle_distance_to_coordinates(degree, distance):
    x = sin(radians(degree)) * distance
    y = cos(radians(degree)) * distance
    return (x, y)


def scatter(coordinates, limit):
    fig = plt.figure(figsize=(5,5), dpi=200)
    ax = fig.add_subplot(111, projection='3d')
    # plt.ylim(-limit, limit)
    # plt.xlim(-limit, limit)

    ax.set_xlim3d(-limit, limit)
    ax.set_ylim3d(-limit, limit)
    ax.set_zlim3d(-limit, limit)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    ax.scatter(*zip(*coordinates), s=4)
    #fig.savefig('scan.png')
    plt.show()

def write_to_file(coordinates):
    pickle.dump( coordinates, open( "last.p", "wb" ) )

pan_deg = input('Pan degree: ')
tilt_deg = input('Tilt degree: ')
tstep = int(input('Tilt degree per step: '))

pan_steps = pan_degree_to_step(float(pan_deg))
tilt_steps = tilt_degree_to_step(float(tilt_deg), tstep)



try:
    turn_measure_3d(pan_steps, tilt_steps, tstep)
except:
    pass
finally:
    Motor.clean_up()

coordinates = get_coordinates_3d(measurements_3d)
write_to_file(coordinates)
# pprint(measurements_3d)
# pprint(coordinates)


#coordinates = get_coordinates_2d(measurements, 512)
# pprint(coordinates)
# max_x, max_y = max(coordinates)
# d = sqrt(max_x**2 + max_y**2) + 10
# np_arr = np.array(coordinates)
# perc = np.percentile(np_arr, 90)
# d = perc + 10
# print(perc)
# scatter(coordinates, d)