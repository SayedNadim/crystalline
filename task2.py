import logging
from abc import ABC, abstractmethod

import dill as pickle
from aalpy.automata import MealyMachine
from aalpy.base import SUL
from aalpy.learning_algs import run_Lstar
from aalpy.oracles import RandomWalkEqOracle
from aalpy.utils import visualize_automaton
from tqdm import tqdm


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

# Console handler (to output to the console)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# File handler (to save logs to a file)
fh = logging.FileHandler('vending_machine_log.log')
fh.setLevel(logging.DEBUG)  
fh.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(ch)
logger.addHandler(fh)


# Abstract vending machine interface - Provided with the assignment
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
class VendingMachineSUL(SUL): # tried with PyClassSUL, PyMethodSUL, 
    def __init__(self, vending_machine):
        super().__init__()
        self.vending_machine = vending_machine

    def pre(self):
        # if I don't reset, it causes non-deteministic behavior. 
        # I think, the reason is that, after learning, the machine has to reset for the next steps.
        self.vending_machine.reset() 
        logger.debug(f"Vending machine state reset before learning.")

    def post(self):
        # similar to the pre. Not resetting causes non-deterministic behavior.
        self.vending_machine.reset()
        logger.debug(f"Vending machine state reset after learning.")

    def reset(self):
        # TODO: I am not sure if I need this explicit reset function. Will try later
        self.vending_machine.reset()
        logger.debug(f"Vending machine state reset during the test.")

    def step(self, inputs):
        # Expects tuple. Tried with single inputs. Doesn't work. 
        action, value = inputs
        logger.debug(f"Step with inputs: action={action}, value={value}")
        if action == 'add_coin':
            return self.vending_machine.add_coin(value)
        elif action == 'push_button':
            return self.vending_machine.push_button(value)


# 1. Function to learn models for a list of vending machines
def learn_models(vending_machines):
    learned_models = []
    for idx, machine in tqdm(enumerate(vending_machines), desc="Learning models"):
        logger.info(f"Learning model for Vending Machine {idx + 1}")
        sul = VendingMachineSUL(machine)
        
        # Defining the alphabet for the learning process
        alphabet = [('add_coin', c) for c in [0.5, 1, 2]] + [('push_button', p) for p in ['coke', 'peanuts', 'water']]
        
        # TODO: Understand the oracle better. Currently using examples from Example.py
        eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000)

        logger.debug(f"Alphabet: {alphabet}")

        try:
            # Using try-except because I faced non-deterministic behavior..
            # Update: found the issue. Reset in Pre and Post method int the VendingMachineSUL
            # Running the L* algorithm to learn a Mealy machine for each vending machine
            model = run_Lstar(alphabet=alphabet, sul=sul, eq_oracle=eq_oracle, automaton_type='mealy')
            logger.info(f"Model for Vending Machine {idx + 1} learned successfully.")

            # Visualize the learned model
            visualize_automaton(model, path=f'vending_machine_model_{idx + 1}.png', file_type='png')
            logger.info(f"Model for Vending Machine {idx + 1} visualized and saved as vending_machine_model_{idx + 1}.png")

        except Exception as e:
            logger.error(f"Error learning model for Vending Machine {idx + 1}: {e}")
            continue

        learned_models.append(model)
    return learned_models


# 2. Function to validate a model's response for valid inputs
def validate_model(model, valid_inputs):
    for inputs, expected_output in valid_inputs:
        output = model.step(inputs)
        if output != expected_output:
            logger.warning(f"Model failed for inputs {inputs}: expected {expected_output}, got {output}")
            return False
    return True

# 3. Function to compare models and identify the correct one based on valid responses
def compare_models(models):
    correct_model = None
    faults = []

    # Define valid inputs and expected outputs
    # The valid inputs are based on the assignment.
    # # TODO: I assumed the valid ouptuts. Might be wrong. Needs more checking
    valid_inputs = [
        (('add_coin', 0.5), "coin_added"), 
        (('add_coin', 1), "coin_added"), 
        (('add_coin', 2), "coin_added"), 
        (('push_button', 'coke'), "Coke"),
        (('push_button', 'peanuts'), "Peanuts"),
        (('push_button', 'water'), "Water")
    ]
    
    logger.info("Comparing models...")

    # Compare models pair by pair
    for i, model_a in enumerate(models):
        for j, model_b in enumerate(models):
            if i != j:
                logger.info(f"Comparing Model {i + 1} with Model {j + 1}")
                differences = compare_mealy_machines(model_a, model_b, valid_inputs)
                if differences:
                    logger.info(f"Model {i + 1} differs from Model {j + 1}: {differences}")
                    faults.append((i + 1, j + 1, differences))

    # Identify the correct model based on valid responses
    logger.info("Identifying the correct model...")
    for idx, model in enumerate(models):
        if validate_model(model, valid_inputs):
            if correct_model is None:
                correct_model = idx + 1  # First valid model is considered correct
            else:
                logger.warning(f"Model {idx + 1} is valid but another correct model has already been identified.")
        else:
            logger.warning(f"Model {idx + 1} failed validation.")

    return correct_model, faults


# 4. Function to compare two Mealy machines
def compare_mealy_machines(machine_a, machine_b, valid_inputs):
    differences = []
    for inputs, expected_output in valid_inputs:
        output_a = machine_a.step(inputs)
        output_b = machine_b.step(inputs)

        # If outputs are different, log the difference
        if output_a != output_b:
            differences.append((inputs, output_a, output_b))
    return differences

# 5. Function to test with dummy values
def test_with_dummy_values():
    # I was having issues with the pickle files.
    # Needed to check if the implementation is correct or not with dummy values.
    class DummyVendingMachine:
        def __init__(self):
            self.coins = 0

        def add_coin(self, coin):
            self.coins += coin
            return f"coin_added: {coin}"

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
    logger.info("Learning models for dummy vending machines...")
    models = learn_models(vending_machines)

    # Compare models and output results
    logger.info("Comparing models...")
    correct_model, faults = compare_models(models)
    logger.info(f"The correct dummy vending machine model is: vending_machine_{correct_model}")
    for faulty_idx, compared_to, diffs in faults:
        logger.warning(f"Dummy Vending Machine {faulty_idx} differs from {compared_to} in the following ways: {diffs}")

# 6. Function to test with real pickle values
def test_with_pickle_values():
    def load_vending_machines():
        machines = []
        for model_file in ['vending_machine_1.pickle', 'vending_machine_2.pickle',
                        'vending_machine_3.pickle', 'vending_machine_4.pickle']:
            try:
                with open(f'black_box_impl/{model_file}', 'rb') as file:
                    machines.append(pickle.load(file, fix_imports=True, encoding='latin1'))
            except ModuleNotFoundError as e:
                logger.error(f"Error loading {model_file}: {e}. Attempting conversion...")
                # If loading fails, try converting the pickle file
                converted_path = convert_pickle(file_path)
                if converted_path:
                    with open(converted_path, 'rb') as file:
                        machines.append(pickle.load(file))
            except Exception as e:
                logger.error(f"Error loading {model_file}: {e}")
        return machines

    # Load the real vending machine models
    logger.info("Loading real vending machine models...")
    vending_machines = load_vending_machines()
    
    # Check if all vending machines were loaded successfully
    if not vending_machines:
        logger.error("No vending machines were loaded. Exiting.")
        return
    
    # Learn models
    logger.info("Learning models for real vending machines...")
    models = learn_models(vending_machines)

    # Compare models and output results
    logger.info("Comparing models...")
    correct_model, faults = compare_models(models)
    logger.info(f"The correct vending machine model is: vending_machine_{correct_model}")
    for faulty_idx, compared_to, diffs in faults:
        logger.warning(f"Vending Machine {faulty_idx} differs from {compared_to} in the following ways: {diffs}")


# 7. Function to check the pickle files 
def test_pickle_file(file_path):

    # I have found that in MAC, serialized pickles are not working. 
    # One of the reasons can be different os/version settings.

    # Update: Found the issue. Python=3.9 solves it. 
    # If a file is pickled in Python 3.9, it might not open in Python 3.10. Python changes a lot. :( 
    # I don't know why Python 3.10 was recommended. Maybe to check if I try different approaches or not.


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

    try:
        with open(file_path, 'rb') as file:
            obj = pickle.load(file)
            logger.info(f"Loaded {file_path} successfully.")
            logger.debug(f"Obj stats: {vars(obj)}")
            
            # Test each method
            obj.reset()
            logger.debug("Reset successful.")
            
            result = obj.add_coin(1)
            logger.debug(f"Add coin result: {result}")
            
            result = obj.push_button('coke')
            logger.debug(f"Push button result: {result}")

    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")


# 8. Convert Python 2 pickle to Python 3 compatible format
# Not needed anymore. I assumed that the pickle files were created using Pythn 2.
def convert_pickle(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        converted_file_path = file_path.replace('.pickle', '_converted.pickle')
        with open(converted_file_path, 'wb') as file:
            pickle.dump(data, file, protocol=2)
        logger.info(f"Converted {file_path} to {converted_file_path}")
        return converted_file_path
    except Exception as e:
        logger.error(f"Error converting {file_path}: {e}")
        return None




if __name__ == '__main__':
    # Hyperparams
    TEST_REAL = True
    TEST_DUMMY = False
    DEBUG_PICKLES = False

    if TEST_DUMMY:
        logger.info("Testing with dummy values...")
        test_with_dummy_values()
        logger.info("----------x---------")
    if TEST_REAL:
        logger.info("Testing with the real values...")
        test_with_pickle_values()
        logger.info("----------x---------")
    if DEBUG_PICKLES:
        debug_pickles()
