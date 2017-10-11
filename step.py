from dep.StepMotorDriver import StepMotorDriver

def degree_to_step(degree, max_steps = 512):
    step_per_degree = max_steps / 360
    return int(round(degree * step_per_degree))

dirc = input('Direction [f]: ')
speed = input('Speed [1]: ')
deg = input('Degrees: ')
steps = degree_to_step(float(deg))

if speed == '':
    speed = 1.0
else:
    speed = float(speed)

if dirc.lower() in ['b', 'back', 'backward', 'backwards']:
    speed = -speed

Motor = StepMotorDriver(6, 13, 19, 26, True)
Motor.set_speed(speed)
Motor.make_steps(steps)
Motor.clean_up()
