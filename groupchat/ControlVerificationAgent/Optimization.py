from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Type
import numpy as np
from pydantic import BaseModel
from pyfmi import load_fmu

class ControlParams(BaseModel):
    voltage_control: Dict[str, float]
    current_control: Dict[str, float]

class BaseController:
    def update(self, error: float, dt: float) -> float:
        raise NotImplementedError("Subclasses must implement update method")

class PIController(BaseController):
    def __init__(self, k: float, Ti: float, y_max: float, y_min: float = 0, xi_start: float = 0, y_start: float = 0):
        self.k = k
        self.Ti = Ti
        self.y_max = y_max
        self.y_min = y_min
        self.xi = xi_start
        self.y = y_start

    def update(self, error: float, dt: float) -> float:
        self.xi += error * dt
        self.y = self.k * (error + self.xi / self.Ti)
        self.y = max(min(self.y, self.y_max), self.y_min)
        return self.y

class OptimizationResult(BaseModel):
    best_params: List[float]
    best_score: float
    iteration_results: List[Dict]

class OptimizationTool(ABC):
    def __init__(self, control_algorithm: Type[BaseController], model_path: str, population_size: int,
                 num_variables: int, variable_ranges: List[Tuple[float, float]],
                 max_iterations: int, simulation_time: float, time_step: float, **kwargs):
        self.control_algorithm = control_algorithm
        self.model_path = model_path
        self.population_size = population_size
        self.num_variables = num_variables
        self.variable_ranges = variable_ranges
        self.max_iterations = max_iterations
        self.simulation_time = simulation_time
        self.time_step = time_step
        self.additional_params = kwargs

    @abstractmethod
    def optimize(self) -> OptimizationResult:
        pass

    def objective_function(self, params: List[float]) -> Tuple[float, Dict]:
        control_params = ControlParams(
            voltage_control={"k": params[0], "Ti": params[1], "y_max": 800, "xi_start": 10, "y_start": 1},
            current_control={"k": params[2], "Ti": params[3], "y_max": 0.95, "y_min": 0, "xi_start": 0, "y_start": 0.5}
        )
        times, voltages = self.simulate(self.model_path, self.simulation_time, self.time_step, self.control_algorithm, control_params)
        score, details = self.evaluate_performance(voltages, times, 160)
        return score, details

    def simulate(self, fmu_path: str, simulation_time: float, time_step: float,
                 controller_class: Type[BaseController], control_params: ControlParams):
        model = load_fmu(fmu_path)
        model.setup_experiment(start_time=0)
        model.enter_initialization_mode()
        model.exit_initialization_mode()

        t = 0
        target_voltage = 160
        initial_voltage = 80

        voltage_controller = controller_class(**control_params.voltage_control)
        current_controller = controller_class(**control_params.current_control)

        times, voltages = [], []

        model.set('voltageSensor.v', initial_voltage)

        while t < simulation_time:
            voltage = model.get('voltageSensor.v')[0]
            current = model.get('currentSensor.i')[0]

            voltage_error = target_voltage - voltage
            current_reference = voltage_controller.update(voltage_error, time_step)

            current_error = current_reference - current
            duty_cycle = current_controller.update(current_error, time_step)

            model.set('const3.k', duty_cycle)

            model.do_step(t, time_step)
            t += time_step

            times.append(t)
            voltages.append(voltage)

        return times, voltages

    def evaluate_performance(self, voltages: list, times: list, target_voltage: float):
        settling_time = 0
        overshoot = 0
        integrated_error = 0

        settled = False
        for i, v in enumerate(voltages):
            if not settled and abs(v - target_voltage) / target_voltage <= 0.02:
                settling_time = times[i]
                settled = True

            overshoot = max(overshoot, (v - target_voltage) / target_voltage)
            integrated_error += abs(v - target_voltage) / target_voltage * (times[1] - times[0])

        load_switch_index = int(0.5 / (times[1] - times[0]))
        post_switch_voltages = voltages[load_switch_index:]
        post_switch_times = [t - 0.5 for t in times[load_switch_index:]]

        post_settling_time = 0
        post_overshoot = 0
        post_integrated_error = 0

        settled = False
        for i, v in enumerate(post_switch_voltages):
            if not settled and abs(v - target_voltage) / target_voltage <= 0.02:
                post_settling_time = post_switch_times[i]
                settled = True

            post_overshoot = max(post_overshoot, (v - target_voltage) / target_voltage)
            post_integrated_error += abs(v - target_voltage) / target_voltage * (
                        post_switch_times[1] - post_switch_times[0])

        score = (settling_time + post_settling_time) + 100 * (overshoot + post_overshoot) + 1000 * (
                    100 * integrated_error + post_integrated_error)

        return score, {
            'settling_time': settling_time,
            'overshoot': overshoot,
            'integrated_error': integrated_error,
            'post_settling_time': post_settling_time,
            'post_overshoot': post_overshoot,
            'post_integrated_error': post_integrated_error
        }

class PSOOptimizeTool(OptimizationTool):
    def optimize(self) -> OptimizationResult:
        w, c1, c2 = 0.5, 1.5, 1.5

        particles = np.random.rand(self.population_size, self.num_variables)
        for i in range(self.num_variables):
            particles[:, i] = particles[:, i] * (self.variable_ranges[i][1] - self.variable_ranges[i][0]) + self.variable_ranges[i][0]

        velocities = np.random.randn(self.population_size, self.num_variables) * 0.01

        personal_best_positions = particles.copy()
        personal_best_scores = []
        personal_best_details = []
        for p in particles:
            score, details = self.objective_function(p)
            personal_best_scores.append(score)
            personal_best_details.append(details)

        personal_best_scores = np.array(personal_best_scores)
        global_best_index = np.argmin(personal_best_scores)
        global_best_position = personal_best_positions[global_best_index]
        global_best_score = personal_best_scores[global_best_index]
        global_best_details = personal_best_details[global_best_index]

        iteration_results = []

        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
                r1, r2 = np.random.rand(2)
                velocities[i] = (w * velocities[i] +
                                 c1 * r1 * (personal_best_positions[i] - particles[i]) +
                                 c2 * r2 * (global_best_position - particles[i]))
                particles[i] += velocities[i]

                for j in range(self.num_variables):
                    particles[i, j] = np.clip(particles[i, j], self.variable_ranges[j][0], self.variable_ranges[j][1])

                score, details = self.objective_function(particles[i])

                if score < personal_best_scores[i]:
                    personal_best_scores[i] = score
                    personal_best_positions[i] = particles[i]
                    personal_best_details[i] = details

                if score < global_best_score:
                    global_best_score = score
                    global_best_position = particles[i]
                    global_best_details = details

            iteration_results.append({
                'iteration': iteration + 1,
                'best_score': float(global_best_score),
                'best_params': global_best_position.tolist(),
                'best_details': global_best_details
            })

        return OptimizationResult(
            best_params=global_best_position.tolist(),
            best_score=float(global_best_score),
            iteration_results=iteration_results
        )

class GAOptimizeTool(OptimizationTool):
    def optimize(self) -> OptimizationResult:
        population = np.random.rand(self.population_size, self.num_variables)
        for i in range(self.num_variables):
            population[:, i] = population[:, i] * (self.variable_ranges[i][1] - self.variable_ranges[i][0]) + self.variable_ranges[i][0]

        iteration_results = []
        best_individual = None
        best_score = float('inf')
        best_details = None

        for iteration in range(self.max_iterations):
            scores = []
            for individual in population:
                score, details = self.objective_function(individual)
                scores.append(score)
                if score < best_score:
                    best_score = score
                    best_individual = individual
                    best_details = details

            iteration_results.append({
                'iteration': iteration + 1,
                'best_score': float(best_score),
                'best_params': best_individual.tolist(),
                'best_details': best_details
            })

            # Selection
            parents = self._selection(population, scores)

            # Crossover
            offspring = self._crossover(parents)

            # Mutation
            offspring = self._mutation(offspring)

            population = offspring

        return OptimizationResult(
            best_params=best_individual.tolist(),
            best_score=float(best_score),
            iteration_results=iteration_results
        )

    def _selection(self, population, scores):
        # Tournament selection
        selected = []
        for _ in range(self.population_size):
            tournament = np.random.choice(len(population), 3, replace=False)
            winner = tournament[np.argmin([scores[i] for i in tournament])]
            selected.append(population[winner])
        return np.array(selected)

    def _crossover(self, parents):
        offspring = []
        for i in range(0, self.population_size, 2):
            parent1, parent2 = parents[i], parents[i+1]
            crossover_point = np.random.randint(1, self.num_variables)
            child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
            child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
            offspring.extend([child1, child2])
        return np.array(offspring)

    def _mutation(self, offspring):
        mutation_rate = 0.1
        for i in range(self.population_size):
            for j in range(self.num_variables):
                if np.random.rand() < mutation_rate:
                    offspring[i, j] = np.random.uniform(self.variable_ranges[j][0], self.variable_ranges[j][1])
        return offspring

# Example usage
if __name__ == "__main__":
    model_path = "path/to/your/model.fmu"
    population_size = 10
    num_variables = 4  # k and Ti for both voltage and current control
    variable_ranges = [(0, 1), (0, 1), (0, 1), (0, 1)]
    max_iterations = 5
    simulation_time = 1.0
    time_step = 0.0001

    pso_tool = PSOOptimizeTool(PIController, model_path, population_size, num_variables, variable_ranges, max_iterations, simulation_time, time_step)
    pso_result = pso_tool.optimize()
    print("PSO Best Result:", pso_result)

    # ga_tool = GAOptimizeTool(PIController, model_path, population_size, num_variables, variable_ranges, max_iterations, simulation_time, time_step)
    # ga_result = ga_tool.optimize()
    print("GA Best Result:", ga_result)