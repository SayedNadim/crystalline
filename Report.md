## P05-C2 Assignment: S_M_NADIM UDDIN

## TASK 1: Theoretical Questions

## Difference Between DHC and L\*M Algorithms

### DHC (Deterministic Hypothesis Construction)
- **Core Idea**: The DHC algorithm incrementally constructs a hypothesis of an automaton by refining it with counterexamples.
- **Strengths**:
  - Simpler and often faster for deterministic systems with fewer states.
  - Efficient when the system behavior is relatively straightforward.
- **Weaknesses**:
  - Less structured, which may lead to inefficiencies in complex systems with many states.
  - Relies heavily on counterexamples, which can be inefficient in larger state spaces.

### L\*M Algorithm
- **Core Idea**: The L\*M algorithm is an extension of Angluin’s L* algorithm designed for Mealy machines. It systematically constructs a model using an observation table, refining it with queries and counterexamples.
- **Strengths**:
  - Efficiently handles complex state spaces with structured exploration using an observation table.
  - Ensures that each state and transition is correctly represented by refining the model iteratively.
- **Weaknesses**:
  - Higher computational complexity due to maintaining and refining the observation table.
  - Can require significant resources, especially with a large number of inputs.

### Summary
The **DHC algorithm** is better suited for simpler, deterministic systems, while the **L\*M algorithm** is ideal for learning models of complex systems where systematic exploration is necessary.

---

## Definition of the Mealy Machine

A **Mealy machine** is defined as follows:
1. **\( S \)** - Set of states: States represent different stages of processing applications.
2. **\( s_0 \)** - Initial state: The starting point of the system.
3. **\( \Sigma \)** - Input alphabet:
   - `receiveApplication`
   - `documentsComplete`
   - `documentsIncomplete`
4. **\( \Omega \)** - Output alphabet:
   - `OK` (Indicating successful processing)
   - `NOK` (Indicating incomplete or unsuccessful processing)

### Example Scenario:
- The system acts as an automated system that receives applications.
- Depending on whether the documents are complete or incomplete, the system transitions between states and produces outputs (`OK` or `NOK`).

---

## Observation Table for the Given Problem

### Explanation of the Observation Table
To construct the observation table for the vending machine that processes applications, we followed these steps:

1. **Initialize the Table**:
   - Start with basic inputs: `receiveApplication`, `documentsComplete`, and `documentsIncomplete`.
   - The rows represent prefixes (sequences of inputs), and the columns represent suffixes to distinguish between different states.

2. **Filling the Table**:
   - Each entry in the table represents the output for a sequence of actions followed by a specific input.
   - For example, if `receiveApplication` followed by `documentsComplete` results in `OK`, that entry is filled with `OK`.

3. **Closure and Consistency Check**:
   - Ensuring that each row represents a distinct state.
   - Adding new prefixes and suffixes to the table if needed to distinguish between states.

4. **Refinement with Counterexamples**:
   - If discrepancies are found (e.g., unexpected outputs), new rows and columns are added to refine the model.

### Observation Table (for Document Processing)

|                         | ε          | receiveApplication | documentsComplete | documentsIncomplete |
|-------------------------|------------|--------------------|-------------------|----------------------|
| **ε**                   | OK         | NOK                | OK               | NOK                  |
| **receiveApplication**  | NOK        | NOK                | OK               | NOK                  |
| **documentsComplete**   | OK         | OK                 | OK               | OK                   |
| **documentsIncomplete** | NOK        | NOK                | NOK              | NOK                  |

### Description of the Observation Table
- **Rows** represent sequences of inputs to reach different states.
  - For example, starting from the initial state (`ε`) and receiving an application (`receiveApplication`) results in an output of `NOK`.
  - If the documents are complete (`documentsComplete`), the system transitions to a state where it outputs `OK`.
  - If the documents are incomplete (`documentsIncomplete`), the system remains in a state where it outputs `NOK`.

- **Columns** represent suffixes used to observe differences in outputs for various states.
  - For instance, after receiving an application, if the documents are complete, the output is `OK`, but if they are incomplete, the output remains `NOK`.

### Analysis of the Observation Table
- The table helps distinguish between states based on the sequence of actions taken (`receiveApplication`, `documentsComplete`, `documentsIncomplete`).
- The system transitions between states depending on the completeness of the documents, producing either `OK` or `NOK` as the output.
- By systematically filling in the table and refining it with counterexamples, the L\*M algorithm efficiently learns the correct model of the system’s behavior.

---

### Conclusion
Using the L\*M algorithm, we constructed an accurate model of the document processing system. The observation table allowed us to systematically distinguish between different states based on the inputs and outputs, ensuring a precise representation of the system's behavior.


---
---

# TASK 2: Practical Questions

### Correct Vending Machine: vending_machine_3
**Description**: 
The correct model (vending_machine_3) correctly handles inputs by:
- Returning `coin_added` when a valid coin (e.g., 2 units) is inserted.
- Dispensing the correct product (`Peanuts`, `Water`, etc.) when the corresponding button is pressed.

### Analysis of Faulty Models:

#### **Vending Machine 1:**
- **Faults**:
  - For coins of 0.5, 1, and 2 units, instead of adding the coin, it returns the coin (`coin_returned` instead of `coin_added`).
  - When pressing the button for 'peanuts', it returns `No_Action` instead of dispensing `Peanuts`.
  - For 'water', it returns `No_Action` instead of dispensing `Water`.

#### **Vending Machine 2:**
- **Faults**:
  - When pressing the button for 'peanuts', it returns `No_Action` instead of dispensing `Peanuts`.
  - For 'water', it incorrectly returns `No_Action` instead of dispensing `Water`.
  - For a coin of 2 units, it adds the coin instead of returning it.

#### **Vending Machine 4:**
- **Faults**:
  - For a coin of 2 units, it incorrectly returns the coin (`coin_returned` instead of `coin_added`).
  - When pressing the button for 'peanuts', it incorrectly returns `No_Action` instead of dispensing `Peanuts`.

---
---
# Issues Faced and Solutions

## Coding Issues

### 1. State Reset Issue in `VendingMachineSUL`
- **Description**: The vending machine did not reset correctly between learning steps, causing inconsistent behavior.
- **Solution**: Updated the `reset()` method within `VendingMachineSUL` to ensure that it correctly resets the internal state of the vending machine instance.

### 2. Comparing Models Functionality
- **Description**: The `compare_models()` function was initially incorrect, making it difficult to differentiate between the faulty and correct models.
- **Solution**: Implemented a robust comparison function that logs differences in behavior for the same inputs, making it easier to identify faults.

### 3. Identifying the Correct Model
- **Description**: Even after implementing comparisons, it was challenging to pinpoint which model was correct due to overlapping behaviors.
- **Solution**: Refined the model validation process by focusing on specific input-output sequences, ensuring that only the correct model produced valid outputs consistently.

## Debugging and Log Analysis

### 1. Inconsistent Results During Testing
- **Description**: The results of the vending machine outputs were inconsistent, especially when dealing with the sequence of actions.
- **Solution**: Added extensive logging to capture state changes and behaviors, and saved these logs to analyze discrepancies.

### 2. Understanding Behavioral Differences Between Models
- **Description**: There were multiple discrepancies between the models for the same inputs, making it hard to determine the root cause.
- **Solution**: Utilized structured logging to highlight differences, which helped identify issues like incorrect coin returns or missing product dispenses.

---
---
### Note
The code, generated visualization, and log file are included for detailed verification and reproducibility of the results.
---
### TODO
If I run the codes for multiple times, I get different outputs. I will try with different seeding techniques.

---
---
EOF
---
---