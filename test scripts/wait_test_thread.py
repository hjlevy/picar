### This code breaks a wait statement in a function,
### and recognizes if esc is pressed everything should be stopped 
### It uses threading to simultaneously run a function collecting data and performing a straight movement

#Note: can't use keyboard for raspberry pi -> try to use signal or figure out a dif way to use keyboard

from threading import Event
import threading
import sys
import time

# import keyboard module.
import keyboard 

import signal 

exit = Event()

class Avoidance(threading.Thread):
  
    # Thread class with a _stop() method. 
    # The thread itself has to check
    # regularly for the stopped() condition.

	def __init__(self, *args, **kwargs):
		super(Avoidance, self).__init__()
		self._stopper = threading.Event()          # ! must not use _stop

	def stop(self):                              #  (avoid confusion)
		print( "base stop()", file=sys.stderr )
		self._stopper.set()                        # ! must not use _stop

	def stopped(self):
		return self._stopper.is_set()              # ! must not use _stop

	def straight(self):
		print("moving straight")
		exit.wait(10)

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C!')
		exit.set()
		sys.exit(0)

	def get_data(self):
		if keyboard.read_key() == 'space':
			print('set')
			exit.set()
		else:
			exit.clear()

	def stop_movement(self):
		if keyboard.read_key() == 'esc':
			print('stop everything')
			exit.set()
			self.stop  

	def run(self):
		if self.stopped():
		 	return
		else:
			self.straight()
			print("All done!")


if __name__ == '__main__':
	t = Avoidance()
	signal.signal(signal.SIGINT, t.signal_handler)
	t.start()
	t.get_data()
	# t.stop_movement()
