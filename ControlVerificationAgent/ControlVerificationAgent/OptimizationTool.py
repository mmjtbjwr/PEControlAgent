import numpy as np
from pydantic import BaseModel
from typing import Dict, List, Callable, Tuple
from SimulationTool import SimulationParams, BaseSimulater, SimulationResult, SimulationFactory, BoostSimulationTool
from ControlTool import ControlParams, BaseController, PIDController, ControllerFactory
from EvaluateTool import EvaluateParams, EvaluateFactory, BaseEvaluater

class OptimizationResult(BaseModel):
    best_params: List[float]
    best_score: float
    best_details: Dict[str, float]
    iteration_results: List[Dict]
    best_params_array: List[List[float]]

class OptimizationFactory:
    @staticmethod
    def create_optimizer(name: str, params: Dict[str, float]):
        if name.lower() == "pso":
            return PSOOptimizer(**params)
        elif name.lower() == "ga":
            return GAOptimizer(**params)
        else:
            raise ValueError(f"Unknown optimization algorithm: {name}")

class BaseOptimizer:
    def optimize(self, fmu_path: str, control_tool: ControllerFactory, control_params: ControlParams,
                 simulation_tool: SimulationFactory, simulation_params: SimulationParams,
                 evaluater_tool: EvaluateFactory, evaluate_params: EvaluateParams,
                 bounds: List[Tuple[float, float]], initial_params: List[float]) -> OptimizationResult:
        raise NotImplementedError("Subclasses must implement optimize method")

class PSOOptimizer(BaseOptimizer):
    def __init__(self, swarm_size: int = 10, max_iterations: int = 100, w: float = 0.5, c1: float = 1.5,
                 c2: float = 1.5):
        self.num_particles = int(swarm_size)
        self.num_iterations = int(max_iterations)
        self.w = w
        self.c1 = c1
        self.c2 = c2

    def optimize(self, fmu_path: str, control_tool: ControllerFactory, control_params: ControlParams,
                 simulation_tool: SimulationFactory, simulation_params: SimulationParams,
                 evaluater_tool: EvaluateFactory, evaluate_params: EvaluateParams,
                 bounds: List[Tuple[float, float]], initial_params: List[float]) -> OptimizationResult:
        particles = np.random.rand(self.num_particles - 1, len(bounds))
        for i in range(len(bounds)):
            particles[:, i] = particles[:, i] * (bounds[i][1] - bounds[i][0]) + bounds[i][0]
        particles = np.vstack([particles, initial_params])
        velocities = np.random.randn(self.num_particles, len(bounds)) * 0.01

        personal_best_positions = particles.copy()
        personal_best_scores = []
        personal_best_details = []
        for p in particles:
            score, details = self.objective_function(p, fmu_path, control_tool, control_params,
                                                     simulation_tool, simulation_params,
                                                     evaluater_tool, evaluate_params)
            personal_best_scores.append(score)
            personal_best_details.append(details)
        personal_best_scores = np.array(personal_best_scores)
        global_best_index = np.argmin(personal_best_scores)
        global_best_position = personal_best_positions[global_best_index]
        global_best_score = personal_best_scores[global_best_index]
        global_best_details = personal_best_details[global_best_index]

        iteration_results = []
        best_params_array = []

        for iteration in range(self.num_iterations):
            print(f"\nIteration {iteration + 1}/{self.num_iterations}")
            for i in range(self.num_particles):
                r1, r2 = np.random.rand(2)
                velocities[i] = (self.w * velocities[i] +
                                 self.c1 * r1 * (personal_best_positions[i] - particles[i]) +
                                 self.c2 * r2 * (global_best_position - particles[i]))
                particles[i] += velocities[i]

                for j in range(len(bounds)):
                    particles[i, j] = np.clip(particles[i, j], bounds[j][0], bounds[j][1])

                score, details = self.objective_function(particles[i], fmu_path, control_tool, control_params,
                                                         simulation_tool, simulation_params,
                                                         evaluater_tool, evaluate_params)

                print(f"Particle {i + 1}: params={particles[i]}, Score={score:.4f}")

                if score < personal_best_scores[i]:
                    personal_best_scores[i] = score
                    personal_best_positions[i] = particles[i]
                    personal_best_details[i] = details

                if score < global_best_score:
                    global_best_score = score
                    global_best_position = particles[i]
                    global_best_details = details

            best_params_array.append(global_best_position.tolist())
            print(f"Best score this iteration: {global_best_score:.4f}")
            iteration_results.append({
                'iteration': iteration + 1,
                'best_score': float(global_best_score),
                'best_params': global_best_position.tolist(),
                'best_details': global_best_details
            })

        return OptimizationResult(
            best_params=global_best_position.tolist(),
            best_score=float(global_best_score),
            best_details=global_best_details,
            iteration_results=iteration_results,
            best_params_array=best_params_array
        )

    def objective_function(self, params: List[float], fmu_path: str,
                           control_tool: BaseController, control_params: ControlParams,
                           simulation_tool: BaseSimulater, simulation_params: SimulationParams,
                           evaluater_tool: EvaluateFactory, evaluate_params: EvaluateParams) -> Tuple[float, Dict[str, float]]:
        # Update control_params with the current particle's parameters
        updated_control_params = ControlParams(
            control_params={**control_params.control_params,
                            'voltage_k': params[0], 'voltage_Ti': params[1],
                            'current_k': params[2], 'current_Ti': params[3]}
        )

        # Create controller
        controller = ControllerFactory.create_controller("duallooppid", updated_control_params)

        # Run simulation
        simulation_result = simulation_tool.simulate(fmu_path, simulation_params, controller)

        # Evaluate results
        score, details = evaluater_tool.evaluate(simulation_result)

        return score, details

class GAOptimizer(BaseOptimizer):
    def __init__(self, population_size: int, max_generations: int):
        self.population_size = population_size
        self.max_generations = max_generations

    def optimize(self, fmu_path: str, control_tool: ControllerFactory, control_params: ControlParams,
                 simulation_tool: SimulationFactory, simulation_params: SimulationParams,
                 evaluater_tool: EvaluateFactory, evaluate_params: EvaluateParams,
                 bounds: List[Tuple[float, float]], initial_params: List[float]) -> OptimizationResult:
        # Implement GA algorithm here
        raise NotImplementedError("GA optimization not implemented yet")

if __name__ == "__main__":
    # Create PSO optimizer parameters
    pso_params = {
        "swarm_size": 10,
        "max_iterations": 5,
        "w": 0.5,
        "c1": 1.5,
        "c2": 1.5
    }

    # Use OptimizationFactory to create PSOOptimizer
    pso_optimizer = OptimizationFactory.create_optimizer("pso", pso_params)

    # Create necessary parameters and tools
    fmu_path = r"C:\Users\17338\Desktop\Multi agent interaction\ControlVerificationAgent\ControlVerificationAgent\boost_converternopid.fmu"

    control_params = ControlParams(control_params={
        'inner_k': 1.0, 'inner_Ti': 0.1, 'inner_Td': 0, 'inner_y_max': 1.0, 'inner_y_min': 0.0,
        'outer_k': 1.0, 'outer_Ti': 0.1, 'outer_Td': 0, 'outer_y_max': 1.0, 'outer_y_min': 0.0
    })

    control_tool = ControllerFactory.create_controller("duallooppid", control_params)

    simulation_params = SimulationParams(
        simulation_time=1.0,
        target_voltage=160,
        initial_voltage=80,
        step_size=0.0001
    )
    simulation_tool = SimulationFactory.create_simulation_tool("boost")
    evaluate_params = EvaluateParams(
        target_voltage=160,
        settling_time_coefficient=1.0,
        overshoot_coefficient=1.0,
        integrated_error_coefficient=1.0,
        post_settling_time_coefficient=1.0,
        post_overshoot_coefficient=1.0,
        post_integrated_error_coefficient=1.0
    )
    evaluater_tool = EvaluateFactory.create_evaluater("duallooppid", evaluate_params)
    # Define optimization bounds
    bounds = [(0, 10), (0, 10), (0, 10), (0, 10)]  # Bounds for inner_k, inner_Ti, outer_k, outer_Ti

    # Use PSOOptimizer to optimize
    optimization_result = pso_optimizer.optimize(
        fmu_path, control_tool, control_params,
        simulation_tool, simulation_params,
        evaluater_tool, evaluate_params,
        bounds, [5, 5, 5, 5]  # Initial parameters
    )

    # Print optimization results
    print(f"Best params: {optimization_result.best_params}")
    print(f"Best score: {optimization_result.best_score}")
    print(f"Best details: {optimization_result.best_details}")