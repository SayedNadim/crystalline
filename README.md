# crystalline

## How to run
- Create a virual env.
    - `conda create -n crystalline python=3.9`
- Install `GraphViz`.
- Install `aalpy` and `dill`.
    - `pip install aalpy dill`
    - For MAC, use user-specific pip installation.

- Make sure you have the pickle files in the `black_box_impl` folder.
- Run `task2.py`
    - `python task2.py`

## Issues
- MAC installation issues. 
    - globally managed packages vs locally managed packages for conda.
    - brew-based installation of dill
- Linux
    - No issues.
    - sudo access for `GraphViz`, didn't try the local installation
- Windows
    - I don't have windows. 
    - Judging from the MAC experience, installation may have some issues with paths and dill. 

## Expected outputs
- log file listing all the outputs.
- Visualization of the machine in PDF.