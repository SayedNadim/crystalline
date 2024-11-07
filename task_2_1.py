import dill as pickle
from abc import ABC, abstractmethod
from aalpy.automata import MealyMachine
from aalpy.base import SUL
from aalpy.SULs import PyClassSUL, FunctionDecorator
from aalpy.oracles import RandomWalkEqOracle
from aalpy.learning_algs import run_Lstar
from aalpy.utils import visualize_automaton

# Define the abstract vending machine interface
class AbstractVendingMachine(ABC):

    @abstractmethod
    def add_coin(self, coin):
        pass

    @abstractmethod
    def push_button(self, order):
        pass

    @abstractmethod
    def reset(self):
        pass


# Wrapper class for interacting with the vending machine implementations
class VendingMachineSUL(SUL):
    def __init__(self, vending_machine):
        super().__init__()
        self.vending_machine = vending_machine

    def reset(self):
        self.vending_machine.reset()

    def step(self, inputs):
        # Handle inputs as a tuple with action type and value
        action, value = inputs
        if action == 'add_coin':
            return self.vending_machine.add_coin(value)
        elif action == 'push_button':
            return self.vending_machine.push_button(value)


# Load vending machine implementations
def load_vending_machines():
    machines = []
    for model_file in ['vending_machine_1.pickle', 'vending_machine_2.pickle',
                       'vending_machine_3.pickle', 'vending_machine_4.pickle']:
        try:
            with open(f'black_box_impl/{model_file}', 'rb') as file:
                machines.append(pickle.load(file))
        except FileNotFoundError:
            print(f"File {model_file} not found.")
        except Exception as e:
            print(f"Error loading {model_file}: {e}")
    return machines


# Learn the Mealy machine model of each vending machine
def learn_models(vending_machines):
    learned_models = []
    for idx, machine in enumerate(vending_machines):
        sul = VendingMachineSUL(machine)
        alphabet = [('add_coin', c) for c in [0.5, 1, 2]] + [('push_button', p) for p in ['coke', 'peanuts', 'water']]
        eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000)
        # model = run_Lstar(MealyMachine, alphabet, sul, eq_oracle, automaton_type='mealy')
        model = run_Lstar(alphabet=alphabet, sul=sul, eq_oracle=eq_oracle, automaton_type='mealy')
        visualize_automaton(model, f'vending_machine_{idx + 1}_model')
        learned_models.append(model)
    return learned_models


# Compare models and identify differences
def compare_models(models):
    correct_model = None
    faults = []
    for i, model_a in enumerate(models):
        is_correct = True
        for j, model_b in enumerate(models):
            if i != j:
                differences = model_a.compare(model_b)
                if differences:
                    faults.append((i + 1, j + 1, differences))
                    is_correct = False
        if is_correct:
            correct_model = i + 1
    return correct_model, faults


if __name__ == '__main__':
    # Load vending machines
    vending_machines = load_vending_machines()

    # Learn models
    models = learn_models(vending_machines)

    # Compare models and identify correct and faulty ones
    correct_model, faults = compare_models(models)

    # Output results
    print(f"The correct vending machine model is: vending_machine_{correct_model}")
    for faulty_idx, compared_to, diffs in faults:
        print(f"Vending Machine {faulty_idx} differs from {compared_to} in the following ways: {diffs}")
