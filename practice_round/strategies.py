import numpy as np

from assignment import Pizza, Assignment, read_assignment
from vqd.score import score


def strategy_0(assignment):
    """Eerst 4 pizzas naar alle teams van 4. Daarna 3 naar teams van 3, en dan 2 naar teams van 2."""

    pizzas = [pizza.id for pizza in assignment.pizzas]

    orders = list()

    teams_4 = assignment.n_teams_four

    while len(pizzas) >= 4 and teams_4 > 0:
        new_order = pizzas[:4]
        pizzas = pizzas[4:]
        orders.append((4, new_order))
        teams_4 -= 1

    teams_3 = assignment.n_teams_three

    while len(pizzas) >= 3 and teams_3 > 0:
        new_order = pizzas[:3]
        pizzas = pizzas[3:]
        orders.append((3, new_order))
        teams_3 -= 1

    teams_2 = assignment.n_teams_three

    while len(pizzas) >= 2 and teams_2 > 0:
        new_order = pizzas[:2]
        pizzas = pizzas[2:]
        orders.append((2, new_order))
        teams_2 -= 1

    return orders


def strategy_1(problem, state):
    """Eerst pizzas naar alle teams van 4. Daarna naar teams van 3, en dan naar teams van 2.
    Sorteer pizzas eerst op aantal ingredienten om."""

    # assignment.pizzas.sort(key=lambda x: x.n_ingredients, reverse=False)

    np.random.seed(state)

    copy_pizza = assignment.pizzas.copy()

    np.random.shuffle(copy_pizza)

    pizzas = [pizza.id for pizza in copy_pizza]

    orders = list()

    teams_4 = assignment.n_teams_four

    while len(pizzas) >= 4 and teams_4 > 0:
        new_order = pizzas[:4]
        pizzas = pizzas[4:]
        orders.append((4, new_order))
        teams_4 -= 1

    teams_3 = assignment.n_teams_three

    while len(pizzas) >= 3 and teams_3 > 0:
        new_order = pizzas[:3]
        pizzas = pizzas[3:]
        orders.append((3, new_order))
        teams_3 -= 1

    teams_2 = assignment.n_teams_three

    while len(pizzas) >= 2 and teams_2 > 0:
        new_order = pizzas[:2]
        pizzas = pizzas[2:]
        orders.append((2, new_order))
        teams_2 -= 1

    return orders


def strategy_2(problem, state):
    """Eerst pizzas naar alle teams van 4. Daarna naar teams van 3, en dan naar teams van 2.
    Sorteer pizzas eerst op aantal ingredienten om."""

    # assignment.pizzas.sort(key=lambda x: x.n_ingredients, reverse=False)

    np.random.seed(state)

    copy_pizza = assignment.pizzas.copy()

    np.random.shuffle(copy_pizza)

    pizzas = [pizza.id for pizza in copy_pizza]

    orders = list()

    teams_4 = assignment.n_teams_four

    spare_pizzas = []

    while len(pizzas) >= 4 and teams_4 > 0:
        new_order = pizzas[:4]
        pizzas = pizzas[4:]
        orders.append((4, new_order))
        teams_4 -= 1

    teams_3 = assignment.n_teams_three

    while len(pizzas) >= 3 and teams_3 > 0:
        new_order = pizzas[:3]
        pizzas = pizzas[3:]
        orders.append((3, new_order))
        teams_3 -= 1

    teams_2 = assignment.n_teams_three

    while len(pizzas) >= 2 and teams_2 > 0:
        new_order = pizzas[:2]
        pizzas = pizzas[2:]
        orders.append((2, new_order))
        teams_2 -= 1

    return orders


if __name__ == '__main__':
    assignment = read_assignment("b_little_bit_of_everything.in")

    # print(assignment.n_teams_four)

    scores = []

    for seed in range(1000, 2000):
        output = strategy_1(assignment, seed)
        # print(output)

        with open('temp.out', 'w') as file:

            file.write(f'{len(output)}\n')

            for entry in output:
                file.write(f'{entry[0]} {" ".join([str(x) for x in entry[1]])}\n')
        the_score = score('b_little_bit_of_everything.in', 'temp.out')
        scores.append((seed, the_score))
        print(f"{seed}: {the_score}")

    scores.sort(key=lambda s: s[1], reverse=True)
    print(f'{scores[0]=}')

    output = strategy_1(assignment, scores[0][0])

    with open('temp.out', 'w') as file:

        file.write(f'{len(output)}\n')

        for entry in output:
            file.write(f'{entry[0]} {" ".join([str(x) for x in entry[1]])}\n')
    the_score = score('b_little_bit_of_everything.in', 'temp.out')
    print(f'{the_score=}')