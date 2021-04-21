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
from pynput.keyboard import Key, Listener, KeyCode 
from collections import defaultdict

exit = Event()

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

	def stop(self):                              #  (avoid confusion)
		print( "base stop()", file=sys.stderr )
		self._stopper.set()                        # ! must not use _stop

	def stopped(self):
		return self._stopper.is_set()              # ! must not use _stop

	def straight(self):
		print("moving straight")
		exit.wait(10)

	def get_data(self):
		if keyboard.read_key() == 'space':
			print('set')
			exit.set()
		else:
			exit.clear()

	def run(self):
		if self.stopped():
		 	return
		else:
			self.straight()
			print("All done!")


if __name__ == '__main__':
	t = Avoidance()
	t.start() 
	t.get_data() 
 