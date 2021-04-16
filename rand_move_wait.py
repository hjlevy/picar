#This code performs random movements on the car while simultaneously avoiding obstacles 
#BUG: can't exit out of program with KeyBoardInterrupt, some GPIO warning

#picar packages
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from picar import front_wheels
from picar import back_wheels
import picar

#time/math packages
import time
import random
import numpy as np

#for running more than one event at once
from threading import Event
import threading

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

def rand_movement():
	#N: number of random movements possible
	N = len(movements)
	# picking random movement 
	n = random.randint(0,N)
	fcn = movements.get(n,"nothing")
	# random speed integer between 50% - 100%
	speed_rnd = random.randint(50,100)
	# random duration between 1-2 seconds
	dt = random.randrange(1,2)
	return fcn(speed_rnd,dt)

## From ultrasonic avoid code 
def rand_dir():
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

def opposite_angle():
	global last_angle
	if last_angle < 90:
		angle = last_angle + 2* fw.turning_max
	else:
		angle = last_angle - 2* fw.turning_max
	last_angle = angle
	return angle

def ua_reading():
	distance = ua.get_distance()
	if distance < turn_distance:
		exit.set()
		print('set')
	else: 
		exit.clear()

def start_avoidance():
	print('start_avoidance')
	backward_speed = 70
	forward_speed = 70

	count = 0
	while True:
		distance = ua.get_distance()
		print("distance: %scm" % distance)
		if distance > 0:
			count = 0
			if distance < back_distance: # backward
				print("avoiding - backward")
				fw.turn(opposite_angle())
				bw.backward()
				bw.speed = backward_speed
				time.sleep(1)
				fw.turn(opposite_angle())
				bw.forward()
				time.sleep(1)
			elif distance < turn_distance: # turn
				print("avoiding - turn")
				fw.turn(rand_dir())
				bw.forward()
				bw.speed = forward_speed
				time.sleep(1)
			else:
				rand_movement()

		#if it can't distance = 0 -> backup or wait until timeout-> stop	
		else:						
			fw.turn_straight()
			if count > timeout:  # timeout, stop;
				bw.stop()
			else:
				bw.backward()
				bw.speed = forward_speed
				count += 1


if __name__ == '__main__':
	#will continue avoiding until keyboard interrupt
	try:
		threading.Thread(target=ua_reading).start()
		threading.Thread(target=start_avoidance).start()
	except KeyboardInterrupt:
		stop(1,1)
