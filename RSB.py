import random
import numpy as np
from simanneal import Annealer
import matplotlib.pyplot as plt

# Fonction pour calculer les temps de fin et les critères
import numpy as np


def calculate_criterion_blocking(jobs, processing_times, release_times, criterion):
    num_jobs = len(jobs)
    num_machines = len(processing_times)
    job_sequence = jobs

    completion_times = np.zeros((num_jobs, num_machines))
    start_times = np.zeros((num_jobs, num_machines))
    machine_availability = np.zeros(num_machines)

    for j, job in enumerate(job_sequence):
        # First machine
        if j == 0:
            start_times[j][0] = max(release_times[job], 0)
        else:
            start_times[j][0] = max(release_times[job], completion_times[j - 1][0])

        completion_times[j][0] = start_times[j][0] + processing_times[0][job]
        machine_availability[0] = completion_times[j][0]

        # Subsequent machines
        for i in range(1, num_machines):
            # Consider both machine availability and job's previous operation
            start_times[j][i] = max(machine_availability[i], completion_times[j][i - 1])
            completion_times[j][i] = start_times[j][i] + processing_times[i][job]
            machine_availability[i] = completion_times[j][i]

    if criterion == "Cmax":
        return completion_times[-1][-1], start_times
    elif criterion == "TFT":
        return sum(completion_times[:, -1]), start_times
    elif criterion == "TT":
        return sum(
            sum(processing_times[machine][job] for machine in range(num_machines)) for job in job_sequence), start_times
    else:
        raise ValueError("Invalid criterion: choose between 'Cmax', 'TFT', or 'TT'.")
# Classe pour l'algorithme de recuit simulé
class FlowshopAnnealer(Annealer):
    def __init__(self, state, processing_times, release_times, criterion):
        self.processing_times = processing_times
        self.release_times = release_times
        self.criterion = criterion
        super().__init__(state)

    def move(self):
        # Générer un voisin en échangeant deux tâches
        i, j = random.sample(range(len(self.state)), 2)
        self.state[i], self.state[j] = self.state[j], self.state[i]

    def energy(self):
        # Calculer la valeur objective selon le critère
        return calculate_criterion_blocking(self.state, self.processing_times, self.release_times, self.criterion)[0]


# Fonction d'exécution du recuit simulé avec annealing
def simulated_annealing_scipy_nowait(processing_times, release_times, criterion, initial_temperature=1000, cooling_rate=0.95,
                              max_iterations=1000):
    num_jobs = len(processing_times[0])
    initial_solution = np.random.permutation(num_jobs)

    # Initialiser l'algorithme de recuit simulé
    annealer = FlowshopAnnealer(initial_solution, processing_times, release_times, criterion)
    annealer.steps = max_iterations  # Nombre d'itérations
    annealer.temperature = initial_temperature  # Température initiale
    annealer.cooling = cooling_rate  # Facteur de refroidissement

    # Lancer l'algorithme de recuit simulé
    solution, objective_value = annealer.anneal()

    # Retourner la solution, le temps de début pour chaque job et la valeur objective
    start_times = calculate_criterion_blocking(solution, processing_times, release_times, criterion)[1]

    return solution, start_times, objective_value









