__author__ = 'Matt'

from lib.colour_sensor import ColourSensor as cs

rbgdict = cs.get_rgb_values()

for key, value in rbgdict.items():
    print(key, value)

