from gurobipy import Model, GRB
import matplotlib.pyplot as plt
from typing import List, Tuple

from gurobipy import Model, GRB

from gurobipy import Model, GRB

def flowshop_scheduling_with_objective(processing_times, release_times, deadlines, M):
    # Nombre de jobs et de machines
    num_machines = len(processing_times)  # Nombre de machines = nombre de sous-listes
    num_jobs = len(processing_times[0])  # Nombre de jobs = longueur de la première sous-liste

    # Créer un nouveau modèle
    model = Model("FlowshopScheduling")

    # Variables de décision
    x = model.addVars(num_jobs, num_jobs, vtype=GRB.BINARY, name="x")  # Variables d'ordonnancement
    c = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="c")  # Temps de fin
    start = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="start")  # Temps de début

    # Variable auxiliaire pour calculer le dépassement du délai (si applicable)
    lateness = model.addVars(num_jobs, vtype=GRB.CONTINUOUS, name="lateness")

    # Contraintes : Assignation des jobs
    for i in range(num_jobs):
        model.addConstr(sum(x[i, j] for j in range(num_jobs)) == 1)  # Chaque job assigné à une position

    for j in range(num_jobs):
        model.addConstr(sum(x[i, j] for i in range(num_jobs)) == 1)  # Chaque position occupée par un job

    # Contraintes pour les temps de fin et début
    for k in range(num_jobs):
        for m in range(num_machines):
            # Temps de fin : Calcul de la fin pour chaque job sur chaque machine
            model.addConstr(c[k, m] == start[k, m] + sum(x[i, k] * processing_times[m][i] for i in range(num_jobs)))

            if m == 0:  # Première machine
                model.addConstr(start[k, m] >= sum(x[i, k] * release_times[i] for i in range(num_jobs)))
            else:  # Machines suivantes
                model.addConstr(start[k, m] >= c[k, m - 1])

            if k > 0:  # Jobs suivants
                model.addConstr(start[k, m] >= c[k - 1, m])

    # Contraintes pour les dépassements de délai (lateness) : Si C_i > D_i, lateness = C_i - D_i
    for i in range(num_jobs):
        model.addConstr(lateness[i] >= 0)  # Lateness ne peut pas être négatif
        model.addConstr(lateness[i] >= c[i, num_machines - 1] - deadlines[i])  # Lateness = max(0, C_i - D_i)

    # Fonction objectif en fonction de M
    if M == "Cmax":
        model.setObjective(c[num_jobs - 1, num_machines - 1], GRB.MINIMIZE)
    elif M == "TFT":
        model.setObjective(sum(c[k, num_machines - 1] for k in range(num_jobs)), GRB.MINIMIZE)
    elif M == "TT":
        # Minimiser la somme des dépassements de délai
        model.setObjective(sum(lateness[i] for i in range(num_jobs)), GRB.MINIMIZE)
    else:
        raise ValueError("Invalid value for M. Choose 'Cmax', 'TFT', or 'TT'.")

    # Résolution du modèle
    model.optimize()

    if model.Status == GRB.OPTIMAL:
        # Extraire la solution
        optimal_sequence = []
        for j in range(num_jobs):
            for i in range(num_jobs):
                if x[i, j].X > 0.5:
                    optimal_sequence.append(i + 1)
        optimal_sequence = [i - 1 for i in optimal_sequence]

        # Extraire les temps de début
        start_times = [[start[k, m].X for m in range(num_machines)] for k in range(num_jobs)]
        objective_value = model.ObjVal
        return optimal_sequence, start_times, objective_value
    else:
        return "No optimal solution found"

