import os
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from .agent import Human, Wall, Exit, Door
 
class InfectionModel(Model):
    """A model for infection spread."""

def __init__(self, N=10, width=10, height=10, ptrans=0.5, progression_period=3, progression_sd=2, death_rate=0.0193, recovery_days=21, recovery_sd=7, floor_plan_file, human_count, random_spawn, save_plots):
        # Load floorplan
        # floorplan = np.genfromtxt(path.join("infection_spread/floorplans/", floor_plan_file))
        with open(os.path.join("infection_spread/floorplans/", floor_plan_file), "rt") as f:
            floorplan = np.matrix([line.strip().split() for line in f.readlines()])

        # Rotate the floorplan so it's interpreted as seen in the text file
        floorplan = np.rot90(floorplan, 3)

        # Check what dimension our floorplan is
        width, height = np.shape(floorplan)

        # Init params
        self.width = width
        self.height = height
        self.human_count = human_count

 # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, torus=False)

 # Used to easily see if a location is an Exit or Door, since this needs to be done a lot
        self.exit_list = []
        self.door_list = []
        # If random spawn is false, spawn_list will contain the list of possible spawn points according to the floorplan
        self.random_spawn = random_spawn
        self.spawn_list = []

        # Load floorplan objects
        for (x, y), value in np.ndenumerate(floorplan):
            value = str(value)
            floor_object = None

            if value is "W":
                floor_object = Wall((x, y), self)

            elif value is "E":
                floor_object = Exit((x, y), self)
                self.exit_list.append((x, y))
                self.door_list.append((x, y))  # Add exits to doors as well

            elif value is "D":
                floor_object = Door((x, y), self)
                self.door_list.append((x, y))

            elif value is "S":
                self.spawn_list.append((x, y))

            if floor_object:
                self.grid.place_agent(floor_object, (x, y))
                self.schedule.add(floor_object)

        # Create a graph of traversable routes, used by agents for pathing
        self.graph = nx.Graph()
        for agents, x, y in self.grid.coord_iter():
            pos = (x, y)

            # If the location is empty, or a door
            if not agents or any(isinstance(agent, Door) for agent in agents):
                neighbors = self.grid.get_neighborhood(pos, moore=True, include_center=True, radius=1)

                for neighbor in neighbors:
                    # If there is contents at this location and they are not Doors or FireExits, skip them
                    if not self.grid.is_cell_empty(neighbor) and neighbor not in self.door_list:
                        continue

                    self.graph.add_edge(pos, neighbor)

 # Start placing human agents
        for i in range(0, self.human_count):
            if self.random_spawn:  # Place human agents randomly
                pos = self.grid.find_empty()
            else:  # Place human agents at specified spawn locations
                pos = random.choice(self.spawn_list)

            if pos:
                # Create a random human
                health = random.randint(self.MIN_HEALTH * 100, self.MAX_HEALTH * 100) / 100
                speed = random.randint(self.MIN_SPEED, self.MAX_SPEED)

self.running = True

def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()

        # If there's no fire yet, attempt to start one
        if not self.fire_started:
            self.start_fire()

        self.datacollector.collect(self)