### This code breaks a wait statement in a function,
### and recognizes if esc is pressed everything should be stopped 
### It uses multiprocessing to simultaneously run a function collecting data and performing a straight movement

#note: doesn't work :(

import multiprocessing 
from threading import Event
# import keyboard module.
import keyboard
import signal 
import sys

exit = Event()

def straight():
	print("moving straight")
	exit.wait(10)

def get_data():
	if keyboard.read_key() == 'space':
		print('set')
		exit.set()
	else:
		exit.clear()

def signal_handler(signal, frame):
		print('You pressed Ctrl+C!')
		exit.set()
		sys.exit(0)

def main():
	straight()
	print("All done!")
    # perform any cleanup here

if __name__ == '__main__':
	# try: 
	#  signal.signal(signal.SIGINT, signal_handler)
	p1 = multiprocessing.Process(target=get_data, args=())
	p2 = multiprocessing.Process(target=main, args=())
	p1.start() 
	p2.start()
	try:
		p1.join()
		p2.join()
	except KeyboardInterrupt:
		p1.terminate()  # sends a SIGTERM
		p2.terminate()

	

