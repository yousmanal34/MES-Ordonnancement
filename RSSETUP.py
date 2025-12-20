import random
import numpy as np
from simanneal import Annealer


# Fonction pour calculer les temps de fin et les critères
def calculate_criterion_with_setup(jobs, processing_times, release_times, setup_times, criterion):
    num_jobs = len(jobs)
    num_machines = len(processing_times)
    setup_matrices = np.array(setup_times)

    completion_times = np.zeros((num_jobs, num_machines))
    start_times = np.zeros((num_jobs, num_machines))

    for i, job in enumerate(jobs):
        for machine in range(num_machines):
            prep_time = setup_matrices[machine]
            if i == 0 and machine == 0:
                # Temps de début pour le premier job sur la première machine
                start_times[i][machine] = release_times[job]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif i == 0:
                # Pour les autres machines du premier job (avec temps de préparation)
                start_times[i][machine] = completion_times[i][machine - 1] + prep_time[job-1][job]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif machine == 0:
                # Pour la première machine des jobs suivants
                start_times[i][machine] = max(completion_times[i - 1][machine], release_times[job]) + prep_time[job-1][job]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            else:
                # Pour les machines suivantes des jobs suivants (avec temps de préparation)
                start_times[i][machine] = max(completion_times[i - 1][machine], completion_times[i][machine - 1]) + prep_time[job-1][job]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]

    if criterion == "Cmax":
        return completion_times[-1][-1], start_times
    elif criterion == "TFT":
        return np.sum(completion_times[:, -1]), start_times
    elif criterion == "TT":
        return np.sum(processing_times), start_times
    else:
        raise ValueError("Critère non valide : choisir entre 'Cmax', 'TFT' ou 'TT'.")



# Classe pour l'algorithme de recuit simulé
class FlowshopAnnealer(Annealer):
    def __init__(self, state, processing_times, release_times,S, criterion):
        self.processing_times = processing_times
        self.release_times = release_times
        self.S=S
        self.criterion = criterion
        super().__init__(state)

    def move(self):
        # Générer un voisin en échangeant deux tâches
        i, j = random.sample(range(len(self.state)), 2)
        self.state[i], self.state[j] = self.state[j], self.state[i]

    def energy(self):
        # Calculer la valeur objective selon le critère
        return calculate_criterion_with_setup(self.state, self.processing_times, self.release_times,self.S, self.criterion)[0]


# Fonction d'exécution du recuit simulé avec annealing
def simulated_annealing_scipy_with_setups(processing_times, release_times,S, criterion, initial_temperature=1000, cooling_rate=0.95,
                              max_iterations=1000):
    num_jobs = len(processing_times[0])
    initial_solution = np.random.permutation(num_jobs)

    # Initialiser l'algorithme de recuit simulé
    annealer = FlowshopAnnealer(initial_solution, processing_times, release_times,S, criterion)
    annealer.steps = max_iterations  # Nombre d'itérations
    annealer.temperature = initial_temperature  # Température initiale
    annealer.cooling = cooling_rate  # Facteur de refroidissement

    # Lancer l'algorithme de recuit simulé
    solution, objective_value = annealer.anneal()

    # Retourner la solution, le temps de début pour chaque job et la valeur objective
    start_times = calculate_criterion_with_setup(solution, processing_times, release_times,S, criterion)[1]

    return solution, start_times, objective_value


