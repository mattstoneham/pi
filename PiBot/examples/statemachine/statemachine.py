__author__ = 'Matt'
# raspirobot_states.py

from examples.statemachine.state import State

class StoppedState(State):

    def on_event(self, event):
        if event == 'start':
            return InitialSearchState()

        return self



class InitialSearchState(State):

    def on_event(self, event):
        if event == 'stop':
            return StoppedState()
        if event == 'search_complete':
            return OrientateState()

        return self



class MoveForwardState(State):

    def on_event(self, event):
        if event == 'stop':
            return StoppedState()
        if event ==  'met_obstacle':
            return WeightedSearchState()

        return self


class WeightedSearchState(State):

    def on_event(self, event):
        if event == 'stop':
            return StoppedState()
        if event == 'search_complete':
            return OrientateState()

        return self


class OrientateState(State):

    def on_event(self, event):
        if event == 'stop':
            return StoppedState()
        if event == 'orientation_complete':
            return MoveForwardState()

        return self


