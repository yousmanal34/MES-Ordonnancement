import random
import numpy as np
from simanneal import Annealer
import matplotlib.pyplot as plt

# Fonction pour calculer les temps de fin et les critères
import numpy as np


def calculate_criterion_nowait(jobs, processing_times, release_times, criterion):
    num_jobs = len(jobs)
    num_machines = len(processing_times)
    completion_times = np.zeros((num_jobs, num_machines))
    start_times = np.zeros((num_jobs, num_machines))
    job_sequence=jobs

    # Pour chaque job dans la séquence
    for j, job in enumerate(job_sequence):
        # Pour le premier job
        if j == 0:
            # Première machine
            start_times[j][0] = release_times[job]
            completion_times[j][0] = start_times[j][0] + processing_times[0][job]

            # Autres machines
            for i in range(1, num_machines):
                start_times[j][i] = completion_times[j][i - 1]
                completion_times[j][i] = start_times[j][i] + processing_times[i][job]
        else:
            # Calculer le début au plus tôt possible
            earliest_start = completion_times[j - 1][0]  # Fin du job précédent sur M1

            # Vérifier si ce début respecte la contrainte no-wait
            for i in range(num_machines):
                if i == 0:
                    start_times[j][i] = earliest_start
                else:
                    required_start = completion_times[j][i - 1]
                    machine_available = completion_times[j - 1][i]
                    start_times[j][i] = max(required_start, machine_available)

                completion_times[j][i] = start_times[j][i] + processing_times[i][job]

                # Si on détecte un écart, on ajuste le début du job
                if i > 0 and start_times[j][i] > completion_times[j][i - 1]:
                    shift = start_times[j][i] - completion_times[j][i - 1]
                    # Ajuster tous les temps précédents
                    for k in range(i):
                        start_times[j][k] += shift
                        completion_times[j][k] += shift

    if criterion == "Cmax":
        return completion_times[-1][-1], start_times
    elif criterion == "TFT":
        return sum(completion_times[:, -1]), start_times
    elif criterion == "TT":
        return sum(sum(processing_times[machine][job] for machine in range(num_machines))
                   for job in job_sequence), start_times
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
        return calculate_criterion_nowait(self.state, self.processing_times, self.release_times, self.criterion)[0]


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
    start_times = calculate_criterion_nowait(solution, processing_times, release_times, criterion)[1]
    print("startttt",start_times)

    return solution, start_times, objective_value


def plot_gantt_chart(start_times, processing_times, job_sequence):
    num_jobs, num_machines = start_times.shape
    colors = plt.cm.get_cmap('Set3')(np.linspace(0, 1, num_jobs))

    fig, ax = plt.subplots(figsize=(12, 6))

    for j, job in enumerate(job_sequence):
        for i in range(num_machines):
            ax.barh(i, processing_times[i][job], left=start_times[j][i], color=colors[job], edgecolor='black')
            ax.text(start_times[j][i] + processing_times[i][job] / 2, i, f'J{job}',
                    ha='center', va='center', color='black', fontweight='bold')

    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f'M{i + 1}' for i in range(num_machines)])
    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_title('Gantt Chart - Flow Shop Scheduling')

    plt.tight_layout()
    return fig







