import random
import numpy as np
from simanneal import Annealer


# Fonction pour calculer les temps de fin et les critères
def calculate_criterion(jobs, processing_times, release_times, criterion):
    num_jobs = len(jobs)
    num_machines = len(processing_times)

    completion_times = np.zeros((num_jobs, num_machines))
    start_times = np.zeros((num_jobs, num_machines))

    for i, job in enumerate(jobs):
        for machine in range(num_machines):
            if i == 0 and machine == 0:
                # Temps de début pour le premier job sur la première machine
                start_times[i][machine] = release_times[job]  # Respecter le release_time du job
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif i == 0:
                # Pour les autres machines du premier job
                start_times[i][machine] = completion_times[i][machine - 1]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif machine == 0:
                # Pour la première machine des jobs suivants
                start_times[i][machine] = max(completion_times[i - 1][machine], release_times[job])
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            else:
                # Pour les machines suivantes des jobs suivants
                start_times[i][machine] = max(completion_times[i - 1][machine], completion_times[i][machine - 1])
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]

    if criterion == "Cmax":
        return completion_times[-1][-1], start_times
    elif criterion == "TFT":
        return sum(completion_times[:, -1]), start_times
    elif criterion == "TT":
        return sum(sum(processing_times[machine][job] for machine in range(num_machines)) for job in jobs), start_times
    else:
        raise ValueError("Critère non valide : choisir entre 'Cmax', 'TFT' ou 'TT'.")


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
        return calculate_criterion(self.state, self.processing_times, self.release_times, self.criterion)[0]


# Fonction d'exécution du recuit simulé avec annealing
def simulated_annealing_scipy(processing_times, release_times, criterion, initial_temperature=1000, cooling_rate=0.95,
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
    start_times = calculate_criterion(solution, processing_times, release_times, criterion)[1]

    return solution, start_times, objective_value


