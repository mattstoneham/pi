__author__ = 'Matt'

import RPi.GPIO as GPIO
import time


class Colourdetection(object):

    s2 = 20
    s3 = 16
    signal = 21
    NUM_CYCLES = 10

    minimum = 8000
    maximum = 10000

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.s2,GPIO.OUT)
        GPIO.setup(self.s3,GPIO.OUT)

        try:
            self.loop()
        except KeyboardInterrupt:
            self.endprogram()


    def loop(self):
        temp = 1
        while True:

            GPIO.output(self.s2,GPIO.LOW)
            GPIO.output(self.s3,GPIO.LOW)
            time.sleep(0.3)
            start = time.time()
            for impulse_count in range(self.NUM_CYCLES):
                GPIO.wait_for_edge(self.signal, GPIO.FALLING)
            duration = time.time() - start
            red  = self.NUM_CYCLES / duration

            GPIO.output(self.s2,GPIO.LOW)
            GPIO.output(self.s3,GPIO.HIGH)
            time.sleep(0.3)
            start = time.time()
            for impulse_count in range(self.NUM_CYCLES):
                GPIO.wait_for_edge(self.signal, GPIO.FALLING)
            duration = time.time() - start
            blue = self.NUM_CYCLES / duration


            GPIO.output(self.s2,GPIO.HIGH)
            GPIO.output(self.s3,GPIO.HIGH)
            time.sleep(0.3)
            start = time.time()
            for impulse_count in range(self.NUM_CYCLES):
                GPIO.wait_for_edge(self.signal, GPIO.FALLING)
            duration = time.time() - start
            green = self.NUM_CYCLES / duration

            total = red + green + blue
            if total > self.maximum:
                print('Auto calibrated max intensity')
                self.maximum = total
            if total < self.minimum:
                print('Auto calibrated min intensity')
                self.minimum = total
                percentage = total / ((self.maximum-self.minimum) / 100)
                print("Light percent: {0}".format(percentage))

            if green<3000 and blue<4200 and red>8000:
                print("red")
                temp=1
            elif red<2200 and  blue<2800 and green>2900:
                print("green")
                temp=1
            elif green<3700 and red<2500 and blue>7.9000 and percentage >20:
                print("blue")
                temp=1
            elif red>10000 and green>10000 and blue>10000:
                print("white")
                temp=1
            elif red<2000 and green<2000 and blue<2000:
                print("black")
                temp=1
            print('\n')



        def endprogram(self):
            GPIO.cleanup()

if __name__=='__main__':

    Colourdetection()

