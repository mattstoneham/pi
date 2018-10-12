#!/usr/bin/env python3

"""
s2_pi.py
 Copyright (c) 2016, 2017 Alan Yorinks All right reserved.
 Python Banyan is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import json
import sys
import time
import os
import pigpio
import psutil
from subprocess import call
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import RPi.GPIO as GPIO


# This class inherits from WebSocket.
# It receives messages from the Scratch and reports back for any digital input
# changes.
class S2Pi(WebSocket):
   
    def handleMessage(self):
        # get command from Scratch2
        payload = json.loads(self.data)
        print(payload)
        client_cmd = payload['command']
        # When the user wishes to set a pin as a digital Input
        if client_cmd == 'getdistance':
            distance = RRB3().get_distance()
            payload = {'report': 'ultrasonicdistance', 'value': str(distance)}
            print('callback', payload)
            msg = json.dumps(payload)
            self.sendMessage(msg)
        
        elif client_cmd == 'ready':
            pass
        else:
            print("Unknown command received", client_cmd)

    # call back from pigpio when a digital input value changed
    # send info back up to scratch
    def input_callback(self, pin, level, tick):
        payload = {'report': 'digital_input_change', 'pin': str(pin), 'level': str(level)}
        print('callback', payload)
        msg = json.dumps(payload)
        self.sendMessage(msg)

    def handleConnected(self):
        self.pi = pigpio.pi()
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


def run_server():
    # checking running processes.
    # if the backplane is already running, just note that and move on.
    found_pigpio = False

    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "pigpiod":
            found_pigpio = True
            print("pigpiod is running")
        else:
            continue

    if not found_pigpio:
        call(['sudo', 'pigpiod'])
        print('pigpiod has been started')

    os.system('scratch2&')
    server = SimpleWebSocketServer('', 9000, S2Pi)
    server.serveforever()


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        sys.exit(0)




# rrb3.py Library



class RRB3:

    MOTOR_DELAY = 0.2

    RIGHT_PWM_PIN = 14
    RIGHT_1_PIN = 10
    RIGHT_2_PIN = 25
    LEFT_PWM_PIN = 24
    LEFT_1_PIN = 17
    LEFT_2_PIN = 4
    SW1_PIN = 11
    SW2_PIN = 9
    LED1_PIN = 8
    LED2_PIN = 7
    OC1_PIN = 22
    OC2_PIN = 27
    OC2_PIN_R1 = 21
    OC2_PIN_R2 = 27
    TRIGGER_PIN = 18
    ECHO_PIN = 23
    left_pwm = 0
    right_pwm = 0
    pwm_scale = 0

    old_left_dir = -1
    old_right_dir = -1

    def __init__(self, battery_voltage=9.0, motor_voltage=6.0, revision=2):

        self.pwm_scale = float(motor_voltage) / float(battery_voltage)

        if self.pwm_scale > 1:
            print("WARNING: Motor voltage is higher than battery votage. Motor may run slow.")

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.LEFT_PWM_PIN, GPIO.OUT)
        self.left_pwm = GPIO.PWM(self.LEFT_PWM_PIN, 500)
        self.left_pwm.start(0)
        GPIO.setup(self.LEFT_1_PIN, GPIO.OUT)
        GPIO.setup(self.LEFT_2_PIN, GPIO.OUT)

        GPIO.setup(self.RIGHT_PWM_PIN, GPIO.OUT)
        self.right_pwm = GPIO.PWM(self.RIGHT_PWM_PIN, 500)
        self.right_pwm.start(0)
        GPIO.setup(self.RIGHT_1_PIN, GPIO.OUT)
        GPIO.setup(self.RIGHT_2_PIN, GPIO.OUT)

        GPIO.setup(self.LED1_PIN, GPIO.OUT)
        GPIO.setup(self.LED2_PIN, GPIO.OUT)

        GPIO.setup(self.OC1_PIN, GPIO.OUT)
        if revision == 1:
            self.OC2_PIN = self.OC2_PIN_R1
        else:
            self.OC2_PIN = self.OC2_PIN_R2

        GPIO.setup(self.OC2_PIN_R2, GPIO.OUT)

        GPIO.setup(self.SW1_PIN, GPIO.IN)
        GPIO.setup(self.SW2_PIN, GPIO.IN)
        GPIO.setup(self.TRIGGER_PIN, GPIO.OUT)
        GPIO.setup(self.ECHO_PIN, GPIO.IN)

    def set_motors(self, left_pwm, left_dir, right_pwm, right_dir):
        if self.old_left_dir != left_dir or self.old_right_dir != right_dir:
            self.set_driver_pins(0, 0, 0, 0)    # stop motors between sudden changes of direction
            time.sleep(self.MOTOR_DELAY)
        self.set_driver_pins(left_pwm, left_dir, right_pwm, right_dir)
        self.old_left_dir = left_dir
        self.old_right_dir = right_dir

    def set_driver_pins(self, left_pwm, left_dir, right_pwm, right_dir):
        self.left_pwm.ChangeDutyCycle(left_pwm * 100 * self.pwm_scale)
        GPIO.output(self.LEFT_1_PIN, left_dir)
        GPIO.output(self.LEFT_2_PIN, not left_dir)
        self.right_pwm.ChangeDutyCycle(right_pwm * 100 * self.pwm_scale)
        GPIO.output(self.RIGHT_1_PIN, right_dir)
        GPIO.output(self.RIGHT_2_PIN, not right_dir)

    def forward(self, seconds=0, speed=1.0):
        self.set_motors(speed, 0, speed, 0)
        if seconds > 0:
            time.sleep(seconds)
            self.stop()

    def stop(self):
        self.set_motors(0, 0, 0, 0)

    def reverse(self, seconds=0, speed=1.0):
        self.set_motors(speed, 1, speed, 1)
        if seconds > 0:
            time.sleep(seconds)
            self.stop()

    def left(self, seconds=0, speed=0.5):
        self.set_motors(speed, 0, speed, 1)
        if seconds > 0:
            time.sleep(seconds)
            self.stop()

    def right(self, seconds=0, speed=0.5):
        self.set_motors(speed, 1, speed, 0)
        if seconds > 0:
            time.sleep(seconds)
            self.stop()

    def step_forward(self, delay, num_steps):
        for i in range(0, num_steps):
            self.set_driver_pins(1, 1, 1, 0)
            time.sleep(delay)
            self.set_driver_pins(1, 1, 1, 1)
            time.sleep(delay)
            self.set_driver_pins(1, 0, 1, 1)
            time.sleep(delay)
            self.set_driver_pins(1, 0, 1, 0)
            time.sleep(delay)
        self.set_driver_pins(0, 0, 0, 0)

    def step_reverse(self, delay, num_steps):
        for i in range(0, num_steps):
            self.set_driver_pins(1, 0, 1, 0)
            time.sleep(delay)
            self.set_driver_pins(1, 0, 1, 1)
            time.sleep(delay)
            self.set_driver_pins(1, 1, 1, 1)
            time.sleep(delay)
            self.set_driver_pins(1, 1, 1, 0)
            time.sleep(delay)
        self.set_driver_pins(0, 0, 0, 0)

    def sw1_closed(self):
        return not GPIO.input(self.SW1_PIN)

    def sw2_closed(self):
        return not GPIO.input(self.SW2_PIN)

    def set_led1(self, state):
        GPIO.output(self.LED1_PIN, state)

    def set_led2(self, state):
        GPIO.output(self.LED2_PIN, state)

    def set_oc1(self, state):
        GPIO.output(self.OC1_PIN, state)

    def set_oc2(self, state):
        GPIO.output(self.OC2_PIN, state)

    def _send_trigger_pulse(self):
        GPIO.output(self.TRIGGER_PIN, True)
        time.sleep(0.0001)
        GPIO.output(self.TRIGGER_PIN, False)

    def _wait_for_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.ECHO_PIN) != value and count > 0:
            count -= 1

    def get_distance(self):
        self._send_trigger_pulse()
        self._wait_for_echo(True, 10000)
        start = time.time()
        self._wait_for_echo(False, 10000)
        finish = time.time()
        pulse_len = finish - start
        distance_cm = pulse_len / 0.000058
        return distance_cm

    def cleanup(self):
        GPIO.cleanup()
