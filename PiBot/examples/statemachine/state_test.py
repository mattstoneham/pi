__author__ = 'Matt'
# raspirobot_state_test.py


from examples.statemachine.statemachine import StoppedState

class StateTest(object):

    def __init__(self):

        # start with a default state...
        self.state = StoppedState()

    def on_event(self, event):

        self.state = self.state.on_event(event)


'''

device = StateTest()
device.on_event(event='start')
device.state

'''