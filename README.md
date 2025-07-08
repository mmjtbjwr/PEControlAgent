
# LLM-Driven Multi-Agent Framework for Autonomous Power Electronics Controller Design Project

## Introduction
This project aims to achieve autonomous design and optimization of a dual-loop PI controller for a boost converter using Large Language Models (LLMs) and automated tools, followed by simulation to evaluate its performance. This framework addresses significant challenges in traditional controller design, such as complexity, high cost, and time consumption. It utilizes LLMs for natural language-based simulation model instantiation and employs an LLM-guided dual-layer optimization strategy to concurrently explore controller structures and refine parameters, leading to the generation of high-performance controllers through iterative feedback. The `autogen` library is used to manage and automate the LLM-driven optimization process.

## Project Structure (Example: Dual-Loop PI Control for DC-DC Boost Converter)
- `main.py`: Main program file, containing the implementation of the automation workflow and agent coordination logic.
- `simulation.py`: Contains functions for simulating the boost converter.
- `optimization.py`: Contains auxiliary tools for the LLM-guided optimization process.
- `utils.py`: Contains utility functions.
- `controllers.py`: Contains the implementation of PI controllers.

## Dependencies
- Python 3.9+
- `autogen`
- `numpy`
- `json`
- `gym`
- `pyfmi`
- `simple-pid`
- `matplotlib`
- `typing_extensions`
- `openai`
- `chainlit`
- `Cython`
- `pyautogen`
- `pybind11`

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

Run the main script to initiate the controller design and optimization process:

```bash
python main.py
```

This will start the LLM-driven optimization, simulate the boost converter with the optimized parameters, and generate a plot of the output voltage.

## Key Components (Example: Dual-Loop PI Control for DC-DC Boost Converter)

  - **PI Controller:** The `PIController` class in `controllers.py` implements a Proportional-Integral controller with an anti-windup mechanism.
  - **LLM-Guided Optimization:** Functions in `optimization.py` (guided by the Large Language Model) are responsible for finding the optimal PI parameters for both voltage and current control loops, including exploring controller structures and fine-tuning parameters.
  - **Boost Converter Simulation:** The `simulate_boost_converter` function in `simulation.py` uses an FMU (Functional Mock-up Unit) model and the optimized PI parameters to simulate the boost converter.
  - **Performance Evaluation:** The `evaluate_performance` function in `simulation.py` assesses the control system's performance, including settling time, overshoot, and integral error.

## Optimization Process

The optimization process employs an LLM-guided dual-layer optimization strategy. This process includes:

  - **Outer-Layer Optimization:** The LLM explores and proposes changes to the controller structure $[C^\*]$.
  - **Inner-Layer Optimization:** For a fixed controller structure, the LLM guides the refinement of parameters $[\\theta]$ to find the optimal parameter set $[\\theta\_C^\*]$.
  - Evaluating the performance of the controller in each iteration.
  - The LLM adapts its strategy based on performance feedback $[P\_{fb}]$, progressively guiding the search process.
  - This process repeats until the specified number of iterations is reached or termination criteria are met.

## Results

Upon completion of the optimization, the program generates a plot of the output voltage over time, saved as 'boost\_converter\_output.png'. Additionally, console output will display the best parameters and performance evaluation results. In the DC-DC boost converter case study, the LLM-driven autonomous optimization process reduced the cost function by 93.64%.

## Video Demonstration
![MP4 演示](video.MP4)



## Contributing

Contributions to this project are welcome. Please follow the standard Git workflow by submitting pull requests for review.

## License

[]

```
```
