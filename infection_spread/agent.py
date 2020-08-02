import numpy as np
import enum

from mesa import Agent


class State(enum.IntEnum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    NA = 3


class Human(Agent):
    """ An agent in an epidemic model."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.age = self.random.normalvariate(20, 40)
        self.state = State.SUSCEPTIBLE
        self.infection_time = 0
        self.model = model

    def get_position(self):
        return self.pos

    def move(self):
        """Move the agent"""

        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def status(self):
        """Check infection status"""

        if self.state == State.INFECTED:
            drate = self.model.death_rate
            alive = np.random.choice([0, 1], p=[drate, 1-drate])
            if alive == 0:
                self.model.schedule.remove(self)
            t = self.model.schedule.time-self.infection_time
            if t >= self.recovery_time:
                self.state = State.RECOVERED
            # print (self.model.schedule.time,self.recovery_time,t)

    def contact(self):
        """Find close contacts and infect"""

        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            # other = self.random.choice(cellmates)
            for other in cellmates:
                # print (self.model.schedule.time,self.state,other.state)
                if self.random.random() > self.model.ptrans:
                    continue
                elif self.state is State.INFECTED and \
                        other.state is State.SUSCEPTIBLE:
                    other.state = State.INFECTED
                    other.infection_time = self.model.schedule.time
                    other.recovery_time = self.model.get_recovery_time()

    def step(self):
        self.status()
        self.move()
        self.contact()


"""
ROOM SET UP
"""


class FloorObject(Agent):
    def __init__(self, pos, traversable, model=None):
        super().__init__(pos, model)
        self.pos = pos
        self.traversable = traversable
        self.state = State.NA

    def get_position(self):
        return self.pos


class Door(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=True, model=model)
        self.state = State.NA


class Exit(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=True, model=model)
        self.state = State.NA


class Wall(FloorObject):
    def __init__(self, pos, model):
        super().__init__(pos, traversable=False, model=model)
        self.state = State.NA
