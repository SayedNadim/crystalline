import dill as pickle
from abc import ABC, abstractmethod
from aalpy.SULs import PyClassSUL
from aalpy.oracles import RandomWordEqOracle
from aalpy.learning_algs import run_Lstar
from aalpy.automata import MealyMachine
# from aalpy.visualization import visualize_automaton
from itertools import product

class AbstractVendingMachine(ABC):
    @abstractmethod
    def add_coin(self, coin):
        """User can add any coin (0.5, 1, 2)."""
        pass

    @abstractmethod
    def push_button(self, order):
        """Possible orders are 'coke', 'peanuts', 'water'."""
        pass

    @abstractmethod
    def reset(self):
        """Resets the vending machine state."""
        pass

class VendingMachineWrapper(AbstractVendingMachine):
    def __init__(self, vending_machine_instance):
        """Wraps a loaded vending machine instance to conform to AbstractVendingMachine interface."""
        self.vending_machine_instance = vending_machine_instance

    def add_coin(self, coin):
        return self.vending_machine_instance.add_coin(coin)

    def push_button(self, order):
        return self.vending_machine_instance.push_button(order)

    def reset(self):
        return self.vending_machine_instance.reset()

class VendingMachineTester:
    def __init__(self, model_files):
        """Initialize with a list of file paths for vending machine model pickles."""
        self.model_files = model_files
        self.black_box_models = []
        self.learned_models = []
        self.model_differences = {}
        self.correct_model_index = None

    def load_models(self):
        """Load black-box models from pickle files and wrap them to conform to the required interface."""
        for model_file in self.model_files:
            with open(f'black_box_impl/{model_file}', 'rb') as handle:
                instance = pickle.load(handle)
                # Wrap the loaded instance in VendingMachineWrapper
                self.black_box_models.append(VendingMachineWrapper(instance))


    def learn_vending_machine_model(self, vending_machine, model_index):
        """Uses AALpy to learn a Mealy machine model for the given vending machine instance."""
        inputs = [('add_coin', coin) for coin in [0.5, 1, 2]] + [('push_button', item) for item in ['coke', 'peanuts', 'water']]
        
        # Pass the class type, not the instance, to PyClassSUL
        sul = PyClassSUL(vending_machine)  # Use the class, not the instance
        
        eq_oracle = RandomWordEqOracle(inputs, sul, num_walks=100, min_walk_len=2, max_walk_len=5)
        learned_model = run_Lstar(inputs, sul, eq_oracle, automaton_type='mealy')
        
        # # Visualize and save the learned model for debugging or analysis purposes
        # visualize_automaton(learned_model, path=f"learned_model_{model_index + 1}.png")
        
        return learned_model

    def generate_input_sequences(self, max_length=3):
        """Generate all possible input sequences up to the specified maximum length."""
        inputs = [('add_coin', coin) for coin in [0.5, 1, 2]] + [('push_button', item) for item in ['coke', 'peanuts', 'water']]
        sequences = []
        for length in range(1, max_length + 1):
            sequences.extend(product(inputs, repeat=length))
        return sequences

    def compare_models(self, model_1, model_2):
        """Compares two learned models and returns any input sequences that produce differing outputs."""
        differences = []
        sequences = self.generate_input_sequences()

        for sequence in sequences:
            model_1.reset()
            model_2.reset()
            outputs_1 = [model_1.step(inp) for inp in sequence]
            outputs_2 = [model_2.step(inp) for inp in sequence]
            
            if outputs_1 != outputs_2:
                differences.append((sequence, outputs_1, outputs_2))
        
        return differences

    def run_learning_and_testing(self):
        """Learn models for each vending machine and identify differences among them."""
        self.learned_models = [self.learn_vending_machine_model(vm, idx) for idx, vm in enumerate(self.black_box_models)]
        self.model_differences = {i: [] for i in range(len(self.learned_models))}

        for i in range(len(self.learned_models)):
            for j in range(i + 1, len(self.learned_models)):
                differences = self.compare_models(self.learned_models[i], self.learned_models[j])
                if differences:
                    self.model_differences[i].extend(differences)
                    self.model_differences[j].extend(differences)

        self.correct_model_index = min(self.model_differences, key=lambda k: len(self.model_differences[k]))

    def generate_report(self, filename="Report.md"):
        """Generate a report of the learning and testing results."""
        with open(filename, "w") as report:
            report.write("# Report on Vending Machine Model Learning and Testing\n\n")
            report.write("## Introduction\n")
            report.write("Four vending machine implementations were tested using learning-based testing with AALpy.\n\n")
            
            report.write("## Correct Model\n")
            report.write(f"Model {self.correct_model_index + 1} was identified as the correct implementation based on consistency across tests.\n")
            report.write("### Description of Correct Model Behavior:\n")
            report.write("The correct model dispenses an item if sufficient coins are inserted. It keeps track of the balance and resets after each transaction.\n\n")
            
            report.write("## Faulty Implementations\n")
            for model_index, differences in self.model_differences.items():
                if model_index != self.correct_model_index:
                    report.write(f"### Model {model_index + 1}\n")
                    report.write("Faults identified:\n")
                    for difference in differences:
                        input_sequence, correct_output, faulty_output = difference
                        report.write(f"- **Input sequence**: {input_sequence}\n")
                        report.write(f"  - **Expected Output**: {correct_output}\n")
                        report.write(f"  - **Faulty Output**: {faulty_output}\n")
                    report.write("\n")
            
            report.write("## Conclusion\n")
            report.write("Learning-based testing proved effective in identifying behavioral discrepancies among models.\n")
            report.write("Model comparison was automated to detect inconsistencies without manual inspection.\n")

if __name__ == '__main__':
    model_files = ['vending_machine_1.pickle', 'vending_machine_2.pickle', 'vending_machine_3.pickle', 'vending_machine_4.pickle']
    tester = VendingMachineTester(model_files)
    tester.load_models()
    tester.run_learning_and_testing()
    # Uncomment to generate report after learning and testing
    # tester.generate_report()

    print(f"The correct model is likely Model {tester.correct_model_index + 1}.")
    for model_index, differences in tester.model_differences.items():
        if model_index != tester.correct_model_index:
            print(f"\nFaults in Model {model_index + 1} compared to the correct model:")
            for difference in differences:
                input_sequence, correct_output, faulty_output = difference
                print(f"Input sequence: {input_sequence} | Correct output: {correct_output} | Faulty output: {faulty_output}")
