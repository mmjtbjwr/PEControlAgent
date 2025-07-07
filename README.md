````markdown
# LLM-Driven Power Electronics Controller Design Project

## Introduction
This project aims to optimize the parameters of a dual-loop PI controller for a boost converter using automated tools and Particle Swarm Optimization (PSO), followed by simulation to evaluate its performance. The `autogen` library is used to manage and automate the optimization process.

## Project Structure (Example: Dual-Loop PID Control for Boost Converter)
- `main.py`: Main program file, containing the implementation of the optimization and simulation workflow.
- `simulation.py`: Contains functions for simulating the boost converter.
- `optimization.py`: Contains the implementation of the PSO optimization tool.
- `utils.py`: Contains utility functions.
- `controllers.py`: Contains the implementation of PID controllers.

## Dependencies
- Python 3.9+
- autogen
- numpy
- json
- gym
- pyfmi
- simple-pid
- matplotlib
- typing_extensions
- openai
- chainlit
- Cython
- pyautogen
- pybind11
- pyswarm

## Installation
- Clone the repository:
```bash
git clone [REPOSITORY_URL]
````

  - Install the required dependencies:

<!-- end list -->

```bash
pip install -r requirements.txt
```

## Usage

Run the main script to start the optimization process:

```bash
python main.py
```

This will initiate PSO optimization, simulate the boost converter with the optimized parameters, and generate a plot of the output voltage.

## Key Components (Example: Dual-Loop PID Control for Boost Converter)

  - **PI Controller:** The `PIController` class in `controllers.py` implements a Proportional-Integral controller with anti-windup mechanism.
  - **PSO Optimization:** The `PSOOptimizeTool` function in `optimization.py` uses the Particle Swarm Optimization algorithm to find the optimal PI parameters for both voltage and current control loops.
  - **Boost Converter Simulation:** The `simulate_boost_converter` function in `simulation.py` uses an FMU (Functional Mock-up Unit) model and the optimized PI parameters to simulate the boost converter.
  - **Performance Evaluation:** The `evaluate_performance` function in `simulation.py` assesses the control system's performance, including settling time, overshoot, and integral error.

## Optimization Process

The optimization process employs the PSO algorithm to tune the PI controller parameters. This process includes:

  - Initializing the particle swarm.
  - Evaluating the performance of each particle in every iteration.
  - Updating each particle's personal best position and the global best position.
  - Repeating this process until the specified number of iterations is reached.

## Results

Upon completion of the optimization, the program generates a plot of the output voltage over time, saved as 'boost\_converter\_output.png'. Additionally, console output will display the best parameters and performance evaluation results.

## Video Demonstration

[**Link to your video demonstration here**]

## Contributing

Contributions to this project are welcome. Please follow the standard Git workflow by submitting pull requests for review.

## License

[Add your license information here, e.g., MIT License]

```
```
