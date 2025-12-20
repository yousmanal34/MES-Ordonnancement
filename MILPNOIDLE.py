from gurobipy import Model, GRB
import matplotlib.pyplot as plt
from typing import List, Tuple


import numpy as np
from gurobipy import Model, GRB

def flowshop_scheduling_with_objective_no_idle(processing_times, release_times, deadlines, M):
    num_machines = len(processing_times)  # Nombre de machines = nombre de sous-listes
    num_jobs = len(processing_times[0])  # Nombre de jobs = longueur de la première sous-liste

    # Vérification des deadlines et de l'objectif TT
    if np.array_equal(deadlines, np.zeros(num_jobs)) and M == "TT":
        raise ValueError("Erreur : Les deadlines ne peuvent pas être toutes nulles lorsque l'objectif est 'TT'.")

    # Create a new model
    model = Model("FlowshopScheduling")

    # Decision variables
    x = model.addVars(num_jobs, num_jobs, vtype=GRB.BINARY, name="x")  # Sequencing variables
    c = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="c")  # Completion times
    start = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="start")  # Start times
    tardiness = model.addVars(num_jobs, vtype=GRB.CONTINUOUS, name="tardiness")  # Tardiness variables

    # Contraintes : Assignation des jobs
    for i in range(num_jobs):
        model.addConstr(sum(x[i, j] for j in range(num_jobs)) == 1)  # Chaque job assigné à une position

    for j in range(num_jobs):
        model.addConstr(sum(x[i, j] for i in range(num_jobs)) == 1)  # Chaque position occupée par un job

    # Contraintes pour les temps de fin et début
    for k in range(num_jobs):
        for m in range(num_machines):
            # Temps de fin
            model.addConstr(c[k, m] == start[k, m] + sum(x[i, k] * processing_times[m][i] for i in range(num_jobs)))

            if m == 0:  # Première machine
                model.addConstr(start[k, m] >= sum(x[i, k] * release_times[i] for i in range(num_jobs)))
            else:  # Machines suivantes
                model.addConstr(start[k, m] >= c[k, m - 1])

            if k > 0:  # Jobs suivants
                model.addConstr(start[k, m] >= c[k - 1, m])

    # No-idle constraint: Ensure that no machine is idle between consecutive jobs
    for m in range(num_machines):
        for k in range(1, num_jobs):
            model.addConstr(start[k, m] == c[k - 1, m])

    # Calcul des retards (tardiness)
    for k in range(num_jobs):
        model.addConstr(tardiness[k] >= c[k, num_machines - 1] - deadlines[k])  # Tardiness >= Completion - Deadline
        model.addConstr(tardiness[k] >= 0)  # Tardiness cannot be negative

    # Objective function based on M
    if M == "Cmax":
        # Minimize makespan (last job on the last machine)
        model.setObjective(c[num_jobs - 1, num_machines - 1], GRB.MINIMIZE)
    elif M == "TFT":
        # Minimize Total Flow Time (sum of completion times across all jobs)
        model.setObjective(sum(c[k, num_machines - 1] for k in range(num_jobs)), GRB.MINIMIZE)
    elif M == "TT":
        # Minimize Total Tardiness (sum of tardiness)
        model.setObjective(sum(tardiness[k] for k in range(num_jobs)), GRB.MINIMIZE)
    else:
        raise ValueError("Invalid value for M. Choose 'Cmax', 'TFT', or 'TT'.")

    # Solve the model
    model.optimize()

    if model.Status == GRB.OPTIMAL:
        # Extract the solution
        optimal_sequence = []
        for j in range(num_jobs):
            for i in range(num_jobs):
                if x[i, j].X > 0.5:
                    optimal_sequence.append(i)

        # Extract start times
        start_times = [[start[k, m].X for m in range(num_machines)] for k in range(num_jobs)]
        objective_value = model.ObjVal

        return optimal_sequence, start_times, objective_value
    else:
        return "No optimal solution found"
