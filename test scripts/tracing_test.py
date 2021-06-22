#testing point plotting function used for tracing path of picar

import time
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.function_base import piecewise

# point generator with initial x0, y0, time duration of movement, speed percentage, degree turn 
def point_plot(x0,y0,dur,spd,deg):
    # specs of car: 180 rot/min 100% speed
    # wheel circumference in ft
    c = np.pi*(2.5*1/12)
    # distance between tires
    L = 5.6*1/12

    # conversion factor ft/sec
    f = c*180*1/60
    v = spd/100*f

    # if turning
    if deg != 0: 
        # turning radius
        alpha = abs(deg)*np.pi/180
        R = L/np.sin(alpha)

        # calculating theta traveled
        omega = v/R
        th_f = omega*dur #rads

        # checking if (+) left or (-) right turn
        #front left turn
        if (np.sign(deg) == 1 and np.sign(spd) ==1):
            # theta step of sim
            th_0 = 0
            dth = 0.1 
            c = [x0-R,y0]
        # back left turn
        elif (np.sign(deg) == 1 and np.sign(spd) == -1):
            th_0 = 0
            dth = -0.1
            c = [x0-R,y0]
        # front right turn
        elif (np.sign(deg) == -1 and np.sign(spd) == 1):
            th_f = -th_f
            th_0 = np.pi
            dth = -0.1
            c = [x0+R,y0]
        # back right turn
        else:
            th_f = -th_f
            th_0 = np.pi
            dth = 0.1
            c = [x0+R,y0]

        thetas = np.arange(th_0, th_0+th_f, dth)
        # print(thetas) #for debug
        xs = c[0] + R*np.cos(thetas)
        ys = c[1] + R*np.sin(thetas)

    else: #if straight or backward
        x_f = x0 
        y_f = y0 + v*dur
        if np.sign(spd) == 1:
            # theta step of sim
            dxy = 0.1 
        else:
            dxy = -0.1
        ys = np.arange(y0,y_f,dxy)
        xs = x0*np.ones_like(ys)

    #plotting results
    plt.plot(xs,ys)
    plt.xlabel('x position (ft)')
    plt.ylabel('y position (ft)')

    plt.xlim([-6,6])
    plt.ylim([0,24])
    plt.show()

if __name__ == '__main__':
    point_plot(2,2,1,50,45)