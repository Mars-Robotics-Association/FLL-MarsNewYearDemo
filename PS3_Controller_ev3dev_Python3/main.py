#!/usr/bin/env python3

# Based on the excellent tutorial from Anton Vanhoucke
# See:
# - https://www.ev3dev.org/docs/tutorials/using-ps3-sixaxis/
# - https://antonsmindstorms.com/2019/04/24/how-to-connec-a-ps3-sixaxis-gamepad-to-an-ev3-brick/
# - https://antonsmindstorms.com/

# Note: This does not use the MicroPython implementation. It uses ev3dev2-Python on Python3

__author__ = 'Anton Vanhoucke'
__author__ = 'Erik Anderson'

import evdev
import ev3dev2.auto as ev3
import threading
#import os.system

## Some helpers ##
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    -- val: float or int
    -- src: tuple
    -- dst: tuple
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scale_stick(value):
    # stickPosition = scale(value,(0,255),(-100,100))
    stickPosition = scale(value,(0,255),(-50,50))
    if abs(stickPosition) < 15:
        return 0
    else:
        return stickPosition

## Initializing ##
print("Finding ps3 controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn
        print(" ... Found.")

gamepad = evdev.InputDevice(ps3dev)

speed = 0
speedFront = 0
speedRear = 0
turnSpeed = 0
steering = 0
running = True
turning = False

class MotorThread(threading.Thread):
    def __init__(self):
        self.motorFront = ev3.MediumMotor(ev3.OUTPUT_A)
        self.motorRear = ev3.MediumMotor(ev3.OUTPUT_D)
        self.drive = ev3.MoveSteering(ev3.OUTPUT_C, ev3.OUTPUT_B)
        self.tank = ev3.MoveTank(ev3.OUTPUT_C, ev3.OUTPUT_B)

        threading.Thread.__init__(self)

    def run(self):
        print("Engine running!")
        # os.system('espeak "I am ready."')
        while running:
            self.drive.on(steering, speed*0.3)
            self.motorFront.on(speedFront*0.2)
            self.motorRear.on(speedRear*0.2)

            while turning:
                self.tank.on(turnSpeed, -turnSpeed)



        self.drive.stop()
        self.motorRight.stop()
        self.motorleft.stop()

motor_thread = MotorThread()
motor_thread.setDaemon(True)
motor_thread.start()


for event in gamepad.read_loop():   #this loops infinitely
    if event.type == 3:             #A stick is moved
        if event.code == 4:         #Y axis on right stick
            speed = -3 * scale_stick(event.value)
        if event.code == 3:         # X axis on the right stick
            steering = scale_stick(event.value)
        if event.code == 1:         # Y axis on the left stick
            speedFront = 3 * scale_stick(event.value)
        if event.code == 0:         # X axis on the right stick
            speedRear = 3 * scale_stick(event.value)


    if event.type == 1 and event.code == 311:
        if event.value == 1:
            turnSpeed = 50
            turning = True
        else:
            turning = False
            turnSpeed = 0
    if event.type == 1 and event.code == 310:
        if event.value == 1:
            turnSpeed = -50
            turning = True
        else:
            turning = False
            turnSpeed = 0



    if event.type == 1 and event.code == 304 and event.value == 1:
        print("X button is pressed. Stopping.")
        running = False
        break