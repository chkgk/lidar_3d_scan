import time
import RPi.GPIO as GPIO
import datetime

# if (stayOn == False):
# 	#set enable to high (i.e. power is NOT going to the motor)
# 	gpio.output(self.enablePin, True)

class StepMotorDriver():

	HALF_STEP_CYCLE = [
		[1,0,0,1],
		[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1]
	]
	FULL_STEP_CYCLE = [
		[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]
	]

	# MAX_WAITING_TIME = 0.5
	MIN_WAITING_TIME = 0.005

	INTERMEDIATE_STOP_THRESHOLD = 0.4


	def __init__(self, p1, p2, p3, p4, full_step = False):
		GPIO.setmode(GPIO.BCM)
		self.motor_pins = [p1, p2, p3, p4]

		for pin in self.motor_pins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, False)

		self.full_step = full_step

		self.active_stepping = self.FULL_STEP_CYCLE if self.full_step else self.HALF_STEP_CYCLE
		self.set_speed(0)

		self.current_step = 0
		self.reversed = False

	# set speed between -1 and +1, negative values reverse.
	def set_speed(self, speed):

		if speed < -1:
			speed = -1
		if speed > 1:
			speed = 1

		self.speed = abs(speed)
		if speed == 0:
			# stop motor
			self.stopped = True
			return

		if speed < 0:
			self.set_reverse()
		else:
			self.set_forward() 

		# self.waiting_time = (0.04/self.LOWEST_SPEED) * (self.LOWEST_SPEED/self.speed) 
		self.waiting_time = self.MIN_WAITING_TIME / (pow(self.MIN_WAITING_TIME, 1-self.speed))
		# print(self.waiting_time)


	def set_reverse(self):
		if self.full_step:
			self.active_stepping = list(reversed(self.FULL_STEP_CYCLE))
		else:
			self.active_stepping = list(reversed(self.HALF_STEP_CYCLE))
		self.reversed = True

	def set_forward(self):
		if self.full_step:
			self.active_stepping = self.FULL_STEP_CYCLE
		else:
			self.active_stepping = self.HALF_STEP_CYCLE
		self.reversed = False
	

	def _set_step(self, step_sequence):
		for (pin, output) in zip(self.motor_pins, step_sequence):
			GPIO.output(pin, output)

	def clean_up(self):
		GPIO.cleanup()

	def make_steps(self, steps, fct=None, tilt_step=None):
		self.current_step = 0

		step_list = list(range(steps))
		if self.reversed:
			step_list = list(reversed(step_list))

		for i in step_list:
			self.current_step = i + 1
			# print(self.current_step)
			for sequence in self.active_stepping:
				self._set_step(sequence)
				if self.waiting_time >= self.INTERMEDIATE_STOP_THRESHOLD:
					time.sleep(self.MIN_WAITING_TIME * 2)
					self._set_step([0, 0, 0, 0])
					time.sleep(self.waiting_time - self.MIN_WAITING_TIME * 2)
				else:
					time.sleep(self.waiting_time)
			if callable(fct):
				fct(self.current_step, tilt_step)



if __name__ == "__main__":
	Driver = StepMotorDriver(6, 13, 19, 26, True)

	def test(a):
		print('writing through test:', a)

	try:
		steps = 20
		speed = 1

		Driver.set_speed(speed)
		start = datetime.datetime.now()
		Driver.make_steps(steps, test)
		end = datetime.datetime.now()
		Driver.set_speed(-speed)
		Driver.make_steps(steps)
		print(end-start)
	except: 
		print('error')
	finally:
		Driver.clean_up()