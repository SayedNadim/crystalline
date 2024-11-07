import dill as pickle
from abc import ABC, abstractmethod
from aalpy.automata import MealyMachine
from aalpy.base import SUL
from aalpy.SULs import PyClassSUL
from aalpy.oracles import RandomWalkEqOracle
from aalpy.learning_algs import run_Lstar
from aalpy.utils import visualize_automaton
from tqdm import tqdm

# Abstract vending machine interface
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

# VendingMachineSUL class to interact with vending machine implementations
class VendingMachineSUL(SUL):
    def __init__(self, vending_machine):
        super().__init__()
        self.vending_machine = vending_machine

    def pre(self):
        pass

    def post(self):
        pass

    def reset(self):
        self.vending_machine.reset()

    def step(self, inputs):
        action, value = inputs
        if action == 'add_coin':
            return self.vending_machine.add_coin(value)
        elif action == 'push_button':
            return self.vending_machine.push_button(value)

# Function to learn models for a list of vending machines
def learn_models(vending_machines):
    learned_models = []
    for idx, machine in tqdm(enumerate(vending_machines), desc="Learning models"):
        sul = VendingMachineSUL(machine)
        alphabet = [('add_coin', c) for c in [0.5, 1, 2]] + [('push_button', p) for p in ['coke', 'peanuts', 'water']]
        eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000)
        model = run_Lstar(alphabet=alphabet, sul=sul, eq_oracle=eq_oracle, automaton_type='mealy')
        visualize_automaton(model, f'vending_machine_{idx + 1}_model')
        learned_models.append(model)
    return learned_models

# Function to compare models and identify differences
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

# 1. Function to test with dummy values
def test_with_dummy_values():
    class DummyVendingMachine:
        def __init__(self):
            self.coins = 0

        def add_coin(self, coin):
            self.coins += coin
            return f"Added coin: {coin}"

        def push_button(self, order):
            if self.coins >= 2:
                self.coins -= 2
                return f"Dispensing {order}"
            else:
                return "Insufficient funds"

        def reset(self):
            self.coins = 0
            return "Reset successful"

    # Create a list of dummy vending machines
    vending_machines = [DummyVendingMachine() for _ in range(4)]
    
    # Learn models
    models = learn_models(vending_machines)

    # Compare models and output results
    correct_model, faults = compare_models(models)
    print(f"The correct dummy vending machine model is: vending_machine_{correct_model}")
    for faulty_idx, compared_to, diffs in faults:
        print(f"Dummy Vending Machine {faulty_idx} differs from {compared_to} in the following ways: {diffs}")

# 2. Function to test with real pickle values
def test_with_pickle_values():
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

    # Load the real vending machine models
    vending_machines = load_vending_machines()
    
    # Check if all vending machines were loaded successfully
    if not vending_machines:
        print("No vending machines were loaded. Exiting.")
        return
    
    # Learn models
    models = learn_models(vending_machines)

    # Compare models and output results
    correct_model, faults = compare_models(models)
    print(f"The correct vending machine model is: vending_machine_{correct_model}")
    for faulty_idx, compared_to, diffs in faults:
        print(f"Vending Machine {faulty_idx} differs from {compared_to} in the following ways: {diffs}")


# 3. Function to check the pickle files 
# I have found that in MAC, serialized pickles are not working. 
# One of the reasons can be different os settings.

''' output from the following function in MAC
-----------------------x------------------------
Loaded black_box_impl/vending_machine_1.pickle successfully.
Reset successful.
XXX lineno: -1, opcode: 0
Error loading black_box_impl/vending_machine_1.pickle: unknown opcode
Loaded black_box_impl/vending_machine_2.pickle successfully.
Reset successful.
XXX lineno: -1, opcode: 0
Error loading black_box_impl/vending_machine_2.pickle: unknown opcode
Loaded black_box_impl/vending_machine_3.pickle successfully.
Reset successful.
XXX lineno: -1, opcode: 0
Error loading black_box_impl/vending_machine_3.pickle: unknown opcode
Loaded black_box_impl/vending_machine_4.pickle successfully.
Reset successful.
XXX lineno: -1, opcode: 0
Error loading black_box_impl/vending_machine_4.pickle: unknown opcode
-------------------------x-----------------------
'''

def test_pickle_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            obj = pickle.load(file)
            print(f"Loaded {file_path} successfully.")
            
            # Test each method
            obj.reset()
            print("Reset successful.")
            
            result = obj.add_coin(1)
            print(f"Add coin result: {result}")
            
            result = obj.push_button('coke')
            print(f"Push button result: {result}")

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")



# Main section to call the appropriate function
if __name__ == '__main__':
    # Test each pickle file
    print("----------x---------")
    print("Running file debugging..")   
    for i in range(1, 5):
        test_pickle_file(f'black_box_impl/vending_machine_{i}.pickle')
    print("----------x---------")
    print()
    # Test with dummy values
    test_with_dummy_values()
    print("----------x---------")
    print()

    # Test with real pickle values
    test_with_pickle_values()
    print("----------x---------")