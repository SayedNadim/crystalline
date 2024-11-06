import dill as pickle
from abc import ABC, abstractmethod
from aalpy.SULs import PyClassSUL
from aalpy.oracles import RandomWordEqOracle
from aalpy.learning_algs import run_Lstar
from aalpy.automata import MealyMachine
from itertools import product

# Interface that all loaded implementations implement
class AbstractVendingMachine(ABC):
    
    @abstractmethod
    # user can add any coin (0.5, 1, 2)
    # you can experiment with more to better understand how automata learning works, but it is not necessary
    def add_coin(self, coin):
        pass

    @abstractmethod
    # possible orders are 'coke', 'peanuts', 'water'
    def push_button(self, order):
        pass

    @abstractmethod
    def reset(self):
        pass

def learn_vending_machine_model(vending_machine):
    """
    Uses AALpy to learn a Mealy machine model for the given vending machine instance.
    """
    # Define inputs
    inputs = [('add_coin', coin) for coin in [0.5, 1, 2]] + [('push_button', item) for item in ['coke', 'peanuts', 'water']]
    
    # System Under Learning (SUL) setup
    sul = PyClassSUL(vending_machine)
    
    # Equivalence oracle setup
    eq_oracle = RandomWordEqOracle(inputs, sul, num_walks=100, min_walk_len=2, max_walk_len=5)
    
    # Learn the model using the L* algorithm
    learned_model = run_Lstar(inputs, sul, eq_oracle, automaton_type='mealy')
    
    return learned_model

def generate_input_sequences(max_length=3):
    """
    Generate all possible input sequences up to the specified maximum length.
    """
    inputs = [('add_coin', coin) for coin in [0.5, 1, 2]] + [('push_button', item) for item in ['coke', 'peanuts', 'water']]
    sequences = []
    for length in range(1, max_length + 1):
        sequences.extend(product(inputs, repeat=length))
    return sequences

def compare_models(model_1, model_2):
    """
    Compares two learned models and returns any input sequences that produce differing outputs.
    """
    differences = []
    sequences = generate_input_sequences()

    for sequence in sequences:
        model_1.reset()
        model_2.reset()

        # Execute sequence on both models and record outputs
        outputs_1 = [model_1.step(inp) for inp in sequence]
        outputs_2 = [model_2.step(inp) for inp in sequence]
        
        # Check if there is a difference in outputs
        if outputs_1 != outputs_2:
            differences.append((sequence, outputs_1, outputs_2))
    
    return differences

if __name__ == '__main__':
    
    # Load 4 implementations of the same interface
    black_box_models = []
    for model_pickle in ['vending_machine_1.pickle', 'vending_machine_2.pickle',
                         'vending_machine_3.pickle', 'vending_machine_4.pickle']:
        with open(f'black_box_impl/{model_pickle}', 'rb') as handle:
            loaded_model = pickle.load(handle)
            black_box_models.append(loaded_model)

    # TODO 1. Learn models of Vending Machines
    learned_models = [learn_vending_machine_model(vm) for vm in black_box_models]

    # TODO 2. Write/use a function that performs learning-based testing to find differences between them (if any)
    model_differences = {i: [] for i in range(len(learned_models))}

    # Compare each pair of models to find discrepancies
    for i in range(len(learned_models)):
        for j in range(i + 1, len(learned_models)):
            differences = compare_models(learned_models[i], learned_models[j])
            if differences:
                model_differences[i].extend(differences)
                model_differences[j].extend(differences)

    # TODO 3. Identify the correct model and bugs in other models
    correct_model_index = min(model_differences, key=lambda k: len(model_differences[k]))

    # Output the findings
    print(f"The correct model is likely Model {correct_model_index + 1}.")
    for model_index, differences in model_differences.items():
        if model_index != correct_model_index:
            print(f"\nFaults in Model {model_index + 1} compared to the correct model:")
            for difference in differences:
                input_sequence, correct_output, faulty_output = difference
                print(f"Input sequence: {input_sequence} | Correct output: {correct_output} | Faulty output: {faulty_output}")

    # # TODO 4. Report findings in Report.md
    # with open("Report.md", "w") as report:
    #     report.write("# Report on Vending Machine Model Learning and Testing\n\n")
    #     report.write("## Introduction\n")
    #     report.write("Four vending machine implementations were tested using learning-based testing with AALpy.\n\n")
        
    #     report.write("## Correct Model\n")
    #     report.write(f"Model {correct_model_index + 1} was identified as the correct implementation based on consistency across tests.\n\n")
        
    #     report.write("## Faulty Implementations\n")
    #     for model_index, differences in model_differences.items():
    #         if model_index != correct_model_index:
    #             report.write(f"### Model {model_index + 1}\n")
    #             report.write("Faults identified:\n")
    #             for difference in differences:
    #                 input_sequence, correct_output, faulty_output = difference
    #                 report.write(f"- Input sequence: {input_sequence}\n")
    #                 report.write(f"  - Correct output: {correct_output}\n")
    #                 report.write(f"  - Faulty output: {faulty_output}\n")
    #             report.write("\n")

    #     report.write("## Conclusion\n")
    #     report.write("Learning-based testing proved effective in identifying behavioral discrepancies among models.\n")
    #     report.write("Model comparison was automated to detect inconsistencies without manual inspection.\n")
