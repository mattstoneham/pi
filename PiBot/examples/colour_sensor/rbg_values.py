__author__ = 'Matt'

__author__ = 'Matt'

import RPi.GPIO as GPIO
import time


class RGBvalues(object):


    s2 = 20
    s3 = 16
    signal = 21
    NUM_CYCLES = 10


    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.s2,GPIO.OUT)
        GPIO.setup(self.s3,GPIO.OUT)
        print("\n")

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
            duration = time.time() - start      #seconds to run for loop
            red  = self.NUM_CYCLES / duration   #in Hz
            print("red value - ",red)

            GPIO.output(self.s2,GPIO.LOW)
            GPIO.output(self.s3,GPIO.HIGH)
            time.sleep(0.3)
            start = time.time()
            for impulse_count in range(self.NUM_CYCLES):
                GPIO.wait_for_edge(self.signal, GPIO.FALLING)
            duration = time.time() - start
            blue = self.NUM_CYCLES / duration
            print("blue value - ",blue)

            GPIO.output(self.s2,GPIO.HIGH)
            GPIO.output(self.s3,GPIO.HIGH)
            time.sleep(0.3)
            start = time.time()
            for impulse_count in range(self.NUM_CYCLES):
                GPIO.wait_for_edge(self.signal, GPIO.FALLING)
            duration = time.time() - start
            green = self.NUM_CYCLES / duration
            print("green value - ",green)
            print('\n\n')
            time.sleep(2)


    def endprogram(self):
        GPIO.cleanup()

if __name__=='__main__':

    RGBvalues()


