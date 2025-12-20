import random
import numpy as np
from simanneal import Annealer

# Fonction pour calculer les temps de fin et les critères avec la contrainte "No Idle"
def calculate_criterion_noidle(jobs, processing_times, release_times, criterion):
    num_jobs = len(jobs)
    num_machines = len(processing_times)

    completion_times = np.zeros((num_jobs, num_machines))
    start_times = np.zeros((num_jobs, num_machines))

    # Calcul des temps de début pour le premier job sur chaque machine
    L = np.zeros(num_machines)
    L[0]=0

    for i in range(1,num_machines):
        max1 = []
        for k in range(num_jobs):
            sum_prev = sum(processing_times[i - 1][j] for j in  jobs)
            sum_current = sum(processing_times[i][j] for j in jobs if j != k)
            somme = sum_prev - sum_current
            max1.append(somme)
        L[i] =L[i-1]+max(max1)
    print ("L=",L)

    for i, job in enumerate(jobs):
        for machine in range(num_machines):
            if i == 0 and machine == 0:
                # Temps de début pour le premier job sur la première machine
                start_times[i][machine] = max(release_times[job],0)  # Respecter le release_time et L
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif i == 0:
                # Pour les autres machines du premier job
                start_times[i][machine] = max(release_times[job], L[machine])
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            elif machine == 0:
                # Pour la première machine des jobs suivants
                start_times[i][machine] = max(completion_times[i - 1][machine], release_times[job])
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]
            else:
                # Pour les machines suivantes des jobs suivants
                start_times[i][machine] = completion_times[i - 1][machine]
                completion_times[i][machine] = start_times[i][machine] + processing_times[machine][job]

    if criterion == "Cmax":
        return completion_times[-1][-1], start_times
    elif criterion == "TFT":
        return sum(completion_times[:, -1]), start_times
    elif criterion == "TT":
        return sum(sum(processing_times[machine][job] for machine in range(num_machines)) for job in jobs), start_times
    else:
        raise ValueError("Critère non valide : choisir entre 'Cmax', 'TFT' ou 'TT'.")

# Classe pour l'algorithme de recuit simulé avec la contrainte "No Idle"
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
        return calculate_criterion_noidle(self.state, self.processing_times, self.release_times, self.criterion)[0]

# Fonction d'exécution du recuit simulé avec annealing
def simulated_annealing_scipy_noidle(processing_times, release_times, criterion, initial_temperature=1000, cooling_rate=0.95,
                              max_iterations=1000):
    num_jobs = len(processing_times[0])
    initial_solution = np.random.permutation(num_jobs)

    # Initialiser l'algorithme de recuit simulé
    annealer = FlowshopAnnealer(initial_solution, processing_times, release_times, criterion)
    annealer.steps = max_iterations  # Nombre d'itérations
    annealer.Tmax = initial_temperature  # Température initiale
    annealer.Tmin = initial_temperature * (cooling_rate ** max_iterations)  # Température finale

    # Lancer l'algorithme de recuit simulé
    solution, objective_value = annealer.anneal()

    # Retourner la solution, le temps de début pour chaque job et la valeur objective
    start_times = calculate_criterion_noidle(solution, processing_times, release_times, criterion)[1]

    return solution, start_times, objective_value

