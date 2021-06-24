#This code performs random movements on the car while simultaneously avoiding obstacles 
#plots where car has traced (WIP: need to include the avoidance paths)
#press esc, then control c when wanting to stop the car and finish the program
#GPIO Runtime Error does not affect performance but is unknown bug

#picar packages
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from picar import front_wheels
from picar import back_wheels
import picar

#time/math packages
import time
import random
import numpy as np
import sys

#for plotting
import matplotlib.pyplot as plt

#for running more than one event at once
from threading import Event
import threading

# import keyboard module.
from pynput.keyboard import Key, Listener, KeyCode 
from collections import defaultdict

exit = Event()

force_turning = 0    # 0 = random direction, 1 = force left, 2 = force right, 3 = orderdly

picar.setup()

ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
fw.turning_max = 45

# ultrasonic distance thresholds for backup/turning
back_distance = 15
turn_distance = 30

#initializing car to straight dir 
last_angle = 90
last_dir = 0

#timeout if robot gets stuck on wall
timeout = 10

# movement function definitions
#### replace print statement with code to move car ####

def turn_right(speed,dt):
	print("turning right")
	# 90deg is straight -> to turn must add or subtract from 90
	fw.turn(90+45)
	bw.forward()
	bw.speed = speed
	exit.wait(dt)

def turn_left(speed,dt):
	print("turning left")
	# 90deg is straight -> to turn must add or subtract from 90
	fw.turn(90-45)
	bw.forward()
	bw.speed = speed
	exit.wait(dt)
 
def straight(speed,dt):
	print("moving straight")
	fw.turn_straight()
	bw.forward()
	bw.speed = speed
	exit.wait(dt)

def back_up(speed,dt):
	print("backing up")
	fw.turn_straight()
	bw.backward()
	bw.speed = speed
	exit.wait(dt)

def back_turn_right(speed,dt):
	print("backing up right")
	# turn steering opposite direction to go right
	fw.turn(90-45)
	bw.backward()
	bw.speed = speed
	exit.wait(dt)

def back_turn_left(speed,dt):
	print("backing up left")
	# turn steering opposite direction to go left
	fw.turn(90+45)
	bw.backward()
	bw.speed = speed
	exit.wait(dt)

def stop(speed,dt):
	bw.stop()
	fw.turn_straight()
	print("stopping")
 
# defining dictionary of movement functions
### add to movements dictionary if more functions added ###
movements = {
        0: turn_right,
        1: turn_left,
		2: straight,
        3: back_up,
		4: back_turn_right,
		5: back_turn_left,
		6: stop
    }

# def live_plotter(self,x_vec,y1_data, z_data, line1, identifier='',pause_time=0.1):
# 	if line1==[]:
# 		# this is the call to matplotlib that allows dynamic plotting
# 		plt.ion()
# 		fig = plt.figure(figsize=(13,6))
# 		ax = fig.add_subplot(111,projection='3d')
# 		# create a variable for the line so we can later update it
# 		self.line1, = ax.plot(x_vec,y1_data,z_data,'.',alpha=0.8)        
# 		#update plot label/title
# 		plt.ylabel('dy')
# 		plt.xlabel('dx')
# 		ax.set_zlabel('dz')
# 		ax.set_zlim(-1,1)
# 		plt.title('Title: {}'.format(identifier))
# 		plt.show()

class KeyboardCtrl(Listener):
	def __init__(self):
		self._key_pressed = defaultdict(lambda: False)
        # self._last_action_ts = defaultdict(lambda: 0.0)
		super().__init__(on_press=self._on_press, on_release=self._on_release)
		self.start()

	def _on_press(self, key):
		#printing key pressed
		print('{0} pressed'.format(key))
		#changing keypressed variable to true 
		if isinstance(key, KeyCode):
			self._key_pressed[key.char] = True
		elif isinstance(key, Key):
			self._key_pressed[key] = True
		

	def _on_release(self, key):
		#printing key released 
		print('{0} release'.format(key))
		#changing keypressed variable to false
		if isinstance(key, KeyCode):
			self._key_pressed[key.char] = False
		elif isinstance(key, Key):
			self._key_pressed[key] = False

		if key == Key.esc:
			# Stop listener
			exit.set()
			stop(1,1)
			return False
		else: 
			return True

	def quit(self):
		#return false if not running or escape pressed
		return not self.running or self._key_pressed[Key.esc]	

class Avoidance(threading.Thread):  
    # Thread class with a _stop() method. 
    # The thread itself has to check
    # regularly for the stopped() condition.

	def __init__(self, *args, **kwargs):
		super(Avoidance, self).__init__()
		self._stopper = threading.Event()          # ! must not use _stop
		self.control = KeyboardCtrl()
		self.p0 = [0,0] #initial position
		self.xpath = []
		self.ypath = []

	def stop(self):                              #  (avoid confusion)
		print( "base stop()", file=sys.stderr )
		self._stopper.set()                        # ! must not use _stop

	def stopped(self):
		return self._stopper.is_set()              # ! must not use _stop

	def rand_movement(self):
		#N: number of random movements possible
		N = len(movements)-1
		# picking random movement 
		n = random.randint(0,N)
		fcn = movements.get(n,"nothing")
		# random speed integer between 50% - 100%
		speed_rnd = random.randint(50,100)
		# random duration between 1-2 seconds
		dt = random.randrange(1,2)

		# conditional statement for path tracing based on path
		if n == 0 or n == 4: #right forward, right backward
			if n ==0:
				self.point_plot(dt,speed_rnd,90-45)
			else: 
				self.point_plot(dt,-speed_rnd,90-45)
		elif n == 1 or n==5:  #left forward, left backward
			if n ==1:
				self.point_plot(dt,speed_rnd,90+45)
			else: 
				self.point_plot(dt,-speed_rnd,90+45)
		elif n == 2 or n==3:  #forward, backward
			if n ==2:
				self.point_plot(dt,speed_rnd,90)
			else: 
				self.point_plot(dt,-speed_rnd,90)
		else: 
			pass

		return fcn(speed_rnd,dt)

	## From ultrasonic avoid code 
	def rand_dir(self):
		global last_angle, last_dir
		#if want random turning enabled 
		if force_turning == 0:
			_dir = random.randint(0, 1)
		#if want orderly turning
		elif force_turning == 3:
			_dir = not last_dir
			last_dir = _dir
			print('last dir  %s' % last_dir)
		#if set turning left/right
		else:
			_dir = force_turning - 1
		angle = (90 - fw.turning_max) + (_dir * 2* fw.turning_max)
		last_angle = angle
		return angle

	def opposite_angle(self):
		global last_angle
		if last_angle < 90:
			angle = last_angle + 2* fw.turning_max
		else:
			angle = last_angle - 2* fw.turning_max
		last_angle = angle
		return angle

	def ua_reading(self):
		distance = ua.get_distance()
		if distance < turn_distance:
			exit.set()
			print('set')
		else: 
			exit.clear()

	# point generator with initial x0, y0, time duration of movement, speed percentage, degree turn 
	def point_plot(self,dur,spd,deg):
		x0 = self.p0[0]
		y0 = self.p0[1]

		c = np.pi*(2.5*1/12)
		# distance between tires
		L = 5.6*1/12

		# conversion factor ft/sec
		f = c*180*1/60
		v = spd/100*f

		# if turning
		if deg != 90: 
			# turning radius
			alpha = abs(deg-90)*np.pi/180
			R = L/np.sin(alpha)

			# calculating theta traveled
			omega = v/R
			th_f = omega*dur #rads

			# checking if (+) left or (-) right turn
			#front left turn
			if (np.sign(deg-90) == 1 and np.sign(spd) ==1):
				# theta step of sim
				th_0 = 0
				dth = 0.1 
				c = [x0-R,y0]
			# back left turn
			elif (np.sign(deg-90) == 1 and np.sign(spd) == -1):
				th_0 = 0
				dth = -0.1
				c = [x0-R,y0]
			# front right turn
			elif (np.sign(deg-90) == -1 and np.sign(spd) == 1):
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

		# next start point
		self.p0[0] = xs[-1]
		self.p0[1] = ys[-1]

		# collecting all points to plot 
		self.xpath = np.append(self.xpath,xs)
		self.ypath = np.append(self.ypath,ys)

	def plot_path(self):
		#plotting results
		plt.plot(self.xpath,self.ypath)
		plt.xlabel('x position (ft)')
		plt.ylabel('y position (ft)')

		plt.xlim([-6,6])
		plt.ylim([0,24])
		plt.show()

	def run(self):
		print('start_avoidance')
		backward_speed = 70
		forward_speed = 70

		count = 0
		while not self.control.quit():
			distance = ua.get_distance()
			print("distance: %scm" % distance)
			if distance > 0:
				count = 0
				if distance < back_distance: # backward
					print("avoiding - backward")
					fw.turn(self.opposite_angle())
					bw.backward()
					bw.speed = backward_speed
					time.sleep(1)
					fw.turn(self.opposite_angle())
					bw.forward()
					time.sleep(1)
				elif distance < turn_distance: # turn
					print("avoiding - turn")
					fw.turn(self.rand_dir())
					bw.forward()
					bw.speed = forward_speed
					time.sleep(1)
				else:
					self.rand_movement()

			#if it can't distance = 0 -> backup or wait until timeout-> stop	
			else:						
				fw.turn_straight()
				if count > timeout:  # timeout, stop;
					bw.stop()
				else:
					bw.backward()
					bw.speed = forward_speed
					count += 1
		
		self.plot_path()
		self.stop()

if __name__ == '__main__':
	#will continue avoiding until keyboard interrupt
	t = Avoidance() 
	t.start()
	t.ua_reading()
	#t.plot_path()

