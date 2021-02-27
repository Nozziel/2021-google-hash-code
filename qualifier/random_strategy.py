from qualifier.calculate_score import calculate_score
from qualifier.input_data import InputData
from qualifier.output_data import OutputData
from qualifier.simulator.simulator import Simulator
from qualifier.strategy import Strategy


class RandomStrategy(Strategy):
    def __init__(self, strategy, seed=27, tries=100):
        super().__init__(seed)
        self.tries = tries
        self._strategy = strategy

    def solve(self, input: InputData) -> OutputData:
        best_score = 0
        best_result = None
        best_seed = None

        for _ in range(self.tries):
            seed = self.random.randint(0, 1_000_000)

            strategy = self._strategy(seed=seed)
            result = strategy.solve(input)
            score = Simulator(input, result).run()
            if score > best_score:
                best_score = score
                best_seed = seed
                best_result = result
                result.save(f'intermediate_random_result_{score:09}.out')

        print(f""" Best seed: {best_seed}
        Best score: {best_score}
        Best result: {best_result}
        """)

        return best_result
