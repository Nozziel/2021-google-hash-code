from collections import deque
from copy import deepcopy
import numpy as np

from qualifier.input_data import InputData
from qualifier.output_data import OutputData

from qualifier.simulatorV4.simulator_car_v4 import SimulatorCarV4
from qualifier.simulatorV4.simulator_street_v4 import SimulatorStreetV4


class SimulatorV4:
    def __init__(self, input_data: InputData, verbose: int = 0):

        self.bonus = input_data.bonus
        self.duration = input_data.duration
        self.verbose = verbose

        self.cars_init = [SimulatorCarV4(path=deque(car.path)) for car in input_data.cars]
        self.cars = list()

        self.actions_init = [deque() for _ in range(self.duration)]  # list with cars, at positions equal to time of entering street
        self.actions = list()

        self.streets = dict()

        self.finished = np.zeros(self.duration + 1, dtype=int)
        self.points = self.bonus + np.arange(self.duration, -1, -1)

        for street_name, street in input_data.streets.items():
            self.streets[street_name] = SimulatorStreetV4(street.time, deque())

    def init_run(self, output_data: OutputData):

        self.finished = np.zeros(self.duration + 1, dtype=int)

        # init action queue: list with cars, at positions equal to time of entering street
        self.actions = deepcopy(self.actions_init)

        # init streets with the schedules # todo: optimize and/or rewrite
        for schedule in output_data.schedules:
            sum_other_streets_before = 0
            length_schedule = sum([d for _, d in schedule.street_duration_tuples])
            if length_schedule == 0:
                continue
            for street_name, duration in schedule.street_duration_tuples:
                passing_times = list()
                for seconds_this_street_before in range(duration):
                    passing_times += range(sum_other_streets_before + seconds_this_street_before,
                                           self.duration,
                                           length_schedule)
                sum_other_streets_before += duration
                self.streets[street_name].passing_times = deque(sorted(passing_times))

        # init cars
        self.cars = deepcopy(self.cars_init)
        for car in self.cars:
            starting_street = car.path.popleft()
            while True:
                try:
                    passing_time = self.streets[starting_street].passing_times.popleft()
                except IndexError:
                    break

                if passing_time < car.time_passed:
                    continue  # get next passing time (green light). car has spend more time already.
                else:
                    car.time_passed = passing_time
                    self.actions[passing_time].append(car)  # add car with remaining streets to action queue
                    break

    def run(self, output_data: OutputData) -> int:
        self.init_run(output_data)

        for time in range(self.duration):
            while True:
                try:
                    car = self.actions[time].pop()
                except IndexError:
                    break
                # car enters street. ride street and check if it needs to go to another street
                street = car.path.popleft()
                car.time_passed += self.streets[street].length

                # if car is finished WITHIN duration, add it to finished
                if len(car.path) == 0 and car.time_passed <= self.duration:
                    self.finished[car.time_passed] += 1
                    continue

                while True:
                    try:
                        passing_time = self.streets[street].passing_times.popleft()
                    except IndexError:
                        break

                    if passing_time < car.time_passed:
                        continue  # get next passing time (green light). car has spend more time already.
                    else:
                        car.time_passed = passing_time
                        self.actions[passing_time].append(car)  # add car with remaining streets to action queue
                        break

        return int(np.dot(self.finished, self.points))
