import os
from datetime import datetime
import random

from qualifier.input_data import InputData
from qualifier.output_data import OutputData
from qualifier.schedule import Schedule
from qualifier.simulator.simulator import Simulator
from qualifier.simulatorV2.simulator_v2 import SimulatorV2
from qualifier.simulatorV3.simulator import SimulatorV3
from qualifier.strategies.evolution_strategy import EvolutionStrategy
from qualifier.strategies.smart_random import SmartRandom
from qualifier.strategy import Strategy
from qualifier.submit import zip_submission
from qualifier.util import save_output

from collections import Counter
import numpy as np

THIS_PATH = os.path.realpath(__file__)


class FixedPeriods(Strategy):
    name = 'FixedPeriods'

    def solve(self, input):
        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                trafic_lights.append((street.name, 1))
            schedule = Schedule(intersection.index, tuple(trafic_lights))
            schedules.append(schedule)

        return OutputData(tuple(schedules))


class RandomPeriods(Strategy):
    name = 'RandomPeriods'

    def solve(self, input):
        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                trafic_lights.append((street.name, self.random.randint(1, 3)))
            schedule = Schedule(intersection.index, trafic_lights)
            schedules.append(schedule)

        return OutputData(tuple(schedules))


class RandomPeriodsx(Strategy):
    name = 'RandomPeriodsx'

    def solve(self, input):
        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                trafic_lights.append((street.name, self.random.randint(1, max(1, input.duration // 100))))
            schedule = Schedule(intersection.index, trafic_lights)
            schedules.append(schedule)

        return OutputData(tuple(schedules))


class AtleastOneCar(Strategy):
    name = 'AtleastOneCar'

    def solve(self, input):

        all_streets = [car.path for car in input.cars]
        streets_with_cars = {item for sublist in all_streets for item in sublist}

        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                if street.name in streets_with_cars:
                    trafic_lights.append((street.name, 1))
            if len(trafic_lights):
                schedule = Schedule(intersection.index, trafic_lights)
                schedules.append(schedule)

        return OutputData(tuple(schedules))


class CarsFirst(Strategy):
    name = 'CarsFirst'

    def solve(self, input: InputData) -> OutputData:
        instersections = dict()

        cars = input.cars
        sorted(cars, key=lambda car_: sum([street_.time for street_ in car_.path]))

        for car in cars:
            for street in car.path:
                if street.end not in instersections:
                    instersections[street.end] = [street.name]
                else:
                    if street.name not in instersections[street.end]:
                        instersections[street.end] = instersections[street.end] + [street.name]

        schedules = []
        for intersection, streets in instersections.items():
            schedule = Schedule(intersection, [(street, 1) for street in streets])
            schedules.append(schedule)
        return OutputData(tuple(schedules))


class BusyFirst(Strategy):
    name = 'BusyFirst'

    def solve(self, input: InputData) -> OutputData:
        all_streets = [car.path for car in input.cars]
        all_streets = [item for sublist in all_streets for item in sublist]
        counted = Counter(all_streets)
        priority = {k: v for k, v in sorted(counted.items(), key=lambda item: item[1], reverse=True)}
        values = list(priority.values())
        mean_value = np.mean(values)
        std_value = np.std(values)

        streets_with_cars = {street.name for street in all_streets}

        def seconds(street):
            if counted[street] <= mean_value - std_value * 0:
                return 1
            if counted[street] <= mean_value + std_value * .5:
                return 2
            if counted[street] <= mean_value + std_value * .1:
                return 3
            if counted[street] <= mean_value + std_value * 2:
                return 4
            if counted[street] <= mean_value + std_value * 4:
                return 5
            else:
                return 6

        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                if street.name in streets_with_cars:
                    trafic_lights.append((street.name, seconds(street)))

            schedule = Schedule(intersection.index, tuple(trafic_lights))
            schedules.append(schedule)

        return OutputData(tuple(schedules))


class Eliot(Strategy):
    name = 'Eliot'

    def solve(self, input: InputData) -> OutputData:
        all_streets = [car.path for car in input.cars]
        all_streets = [item for sublist in all_streets for item in sublist]
        counted = Counter(all_streets)
        priority = {k: v for k, v in sorted(counted.items(), key=lambda item: item[1], reverse=True)}

        instersections = dict()

        for street, count in priority.items():
            if street.end not in instersections:
                instersections[street.end] = [(street.name, min(input.duration, count))]
            else:
                if street.name not in instersections[street.end]:
                    instersections[street.end] = instersections[street.end] + [
                        (street.name, min(input.duration, count))]

        schedules = []
        for intersection, streets in instersections.items():
            schedule = Schedule(intersection, [(street[0], street[1]) for street in streets])
            schedules.append(schedule)
        return OutputData(tuple(schedules))


class CarsFirstBusyFirst(Strategy):
    name = 'CarsFirstBusyFirst'

    def solve(self, input: InputData) -> OutputData:
        instersections = dict()

        cars = input.cars
        sorted(cars, key=lambda car_: sum([street_.time for street_ in car_.path]))

        for car in cars:
            for street in car.path:
                if street.end not in instersections:
                    instersections[street.end] = [street.name]
                else:
                    if street.name not in instersections[street.end]:
                        instersections[street.end] = instersections[street.end] + [street.name]

        schedules = []
        for intersection, streets in instersections.items():
            schedule = Schedule(intersection, tuple([(street, 1) for street in streets]))
            schedules.append(schedule)
        return OutputData(tuple(schedules))


class BusyFirstV2(Strategy):
    name = 'BusyFirstV2'

    def solve(self, input: InputData) -> OutputData:
        all_streets = [car.path for car in input.cars]
        all_streets = [item for sublist in all_streets for item in sublist]
        counted = Counter(all_streets)
        priority = {k: v for k, v in sorted(counted.items(), key=lambda item: item[1], reverse=True)}
        values = list(priority.values())
        mean_value = np.mean(values)
        std_value = np.std(values)

        streets_with_cars = {street.name for street in all_streets}

        step_size = max(1, input.duration // input.n_cars)

        def step(multiplier):
            return min(input.duration, step_size * multiplier)

        def seconds(street):
            return int(max(1, step((counted[street] - mean_value) // std_value)))

        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                if street.name in streets_with_cars:
                    trafic_lights.append((street.name, seconds(street)))

            schedule = Schedule(intersection.index, tuple(trafic_lights))
            schedules.append(schedule)

        return OutputData(tuple(schedules))


class BusyFirstV3(Strategy):
    name = 'BusyFirstV3'

    def solve(self, input: InputData) -> OutputData:
        all_streets = [car.path for car in input.cars]
        all_streets = [item for sublist in all_streets for item in sublist]
        counted = Counter(all_streets)
        priority = {k: v for k, v in sorted(counted.items(), key=lambda item: item[1], reverse=True)}
        values = list(priority.values())

        streets_with_cars = {street.name for street in all_streets}

        def in_bounds(value):
            return max(1, min(input.duration, value))

        def seconds(street):
            return in_bounds(counted[street] // (street.time * 10))

        schedules = []
        for intersection in input.intersections:
            trafic_lights = []
            for street in intersection.incoming_streets:
                if street.name in streets_with_cars and counted[street] > 1:
                    trafic_lights.append((street.name, seconds(street)))

            schedule = Schedule(intersection.index,
                                tuple(trafic_lights))
            schedules.append(schedule)

        return OutputData(tuple(schedules))


if __name__ == '__main__':

    directory = os.path.join(THIS_PATH, '../inputs')
    for file_name in os.listdir(directory):
        if file_name in [
            'a.txt',  # instant
            'b.txt',  # 26s
            'c.txt',  # 17s
            'd.txt',  # 2m09s
            'e.txt',  # instant
            # 'f.txt',  # 4s
        ]:
            continue

        start_time = datetime.now()
        input_data = InputData(os.path.join(directory, file_name))

        good_results = {
            'f.txt': [
                'f_000931074_marco-EvolutionStrategy.out',
                'f_qualifier_marco.out',
                'f_980648_EvolutionStrategy.out'
            ]
        }

        # my_strategy = SmartRandom(seed=random.randint(0, 1_000_000), max_duration=10, ratio_permanent_red=0.01)

        parents = []
        if file_name in good_results:
            print(f'Loading good parents')
            for output_file in good_results[file_name]:
                file = os.path.join(THIS_PATH, f'../saved_results/{output_file}')
                parent = OutputData.read(file, input_data)
                parents.append(parent)

        parents = [
            # *parents,
            BusyFirst(seed=random.randint(0, 1_000_000)).solve(input_data),  # bad results atm
            BusyFirstV2(seed=random.randint(0, 1_000_000)).solve(input_data),  # bad results atm
            BusyFirstV3(seed=random.randint(0, 1_000_000)).solve(input_data),
            FixedPeriods(seed=random.randint(0, 1_000_000)).solve(input_data),
            # CarsFirstBusyFirst(seed=random.randint(0, 1_000_000)).solve(input_data), # bad results atm
        ]

        simulator = SimulatorV2(input_data, verbose=0)
        for i, parent in enumerate(parents):
            print(f'{i} {simulator.run(parent)}')
        exit(0)  # debug end

        my_strategy = EvolutionStrategy(
            input_data=input_data,
            seed=random.randint(0, 1_000_000),
            # debug
            # generations=2,
            # children_per_couple=2,
            # survivor_count=2,

            # normal
            generations=3,
            children_per_couple=30,
            generation_size_limit=6,

            # bit arbitrary but scale it with the problem size
            extra_mutations=input_data.n_intersections // 5,
            gene_pool=parents,
            verbose=2,
            simulator_class=SimulatorV2,
            jobs=4
        )

        output = my_strategy.solve(input_data)

        score = SimulatorV2(input_data, verbose=0).run(output)

        # print(f'Org sim score: {Simulator(input_data, verbose=0).run(output)}')

        duration = datetime.now() - start_time

        potential_score = input_data.n_cars * (input_data.duration + input_data.bonus)

        print(f"""
---------- {file_name} ---------- ({duration.seconds} seconds)
Score:  {score}         (Still to gain ~{potential_score - score} points)
                                   Bonus value: {input_data.bonus} cars: {input_data.n_cars} duration: {input_data.duration} *theoretic max: {input_data.n_cars * input_data.bonus} + {input_data.n_cars * input_data.duration} =  {potential_score}
----------------------------------------------------------     
""")

        save_output(output, file_name, score, f'marco-{my_strategy.name}')

    zip_submission()
