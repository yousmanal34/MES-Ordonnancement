from gurobipy import Model, GRB
import numpy as np

import gurobipy as gp
from gurobipy import GRB
import numpy as np

import gurobipy as gp
from gurobipy import GRB
import numpy as np

import gurobipy as gp
from gurobipy import GRB
import numpy as np


import gurobipy as gp
from gurobipy import GRB
import numpy as np

import numpy as np
import gurobipy as gp
from gurobipy import GRB

from gurobipy import Model, GRB
import numpy as np


import numpy as np
from gurobipy import Model, GRB

from gurobipy import Model, GRB
import numpy as np
from typing import List, Tuple


def flowshop_scheduling_with_preparation(processing_times: List[List[int]],
                                         release_times: List[int],
                                         setup_matrices: List[np.ndarray],deadlines,
                                         objective_type: str) -> Tuple[List[int], List[List[float]], float]:
    """
    Résolution du problème d'ordonnancement avec contraintes de préparation.

    Args:
        processing_times (List[List[int]]): Temps de traitement pour chaque job sur chaque machine.
        release_times (List[int]): Temps de libération de chaque job.
        setup_matrices (List[np.ndarray]): Matrices de temps de préparation pour chaque machine.
        objective_type (str): Type d'objectif ("Cmax", "TFT", ou "TT").

    Returns:
        Tuple: Séquence optimale, temps de début, valeur de la fonction objectif.
    """
    # Nombre de machines et de jobs
    num_machines = len(processing_times)
    num_jobs = len(processing_times[0])

    # Création du modèle
    model = Model("FlowshopSchedulingWithPreparation")

    # Variables de décision
    x = model.addVars(num_jobs, num_jobs, vtype=GRB.BINARY, name="x")  # Variables d'ordonnancement
    c = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="c")  # Temps de fin
    start = model.addVars(num_jobs, num_machines, vtype=GRB.CONTINUOUS, name="start")  # Temps de début

    # Grande constante pour les contraintes (Big-M)
    big_M = 1e6

    # Contraintes : Assignation des jobs
    for i in range(num_jobs):
        model.addConstr(sum(x[i, j] for j in range(num_jobs)) == 1)  # Chaque job assigné à une position
    for j in range(num_jobs):
        model.addConstr(sum(x[i, j] for i in range(num_jobs)) == 1)  # Chaque position occupée par un job

    # Contraintes pour les temps de fin et de début
    for k in range(num_jobs):
        for m in range(num_machines):

            # Temps de fin = Temps de début + Temps de traitement
            model.addConstr(c[k, m] == start[k, m] + sum(x[i, k] * processing_times[m][i] for i in range(num_jobs)))
            if m == 0:  # Première machine
                model.addConstr(start[k, m] >= sum(x[i, k] * release_times[i] for i in range(num_jobs)))
            else:  # Machines suivantes
                model.addConstr(start[k, m] >= c[k, m - 1])



            if k > 0:  # Contraintes de non-chevauchement entre jobs
                model.addConstr(start[k, m] >= c[k - 1, m])

    # Contraintes de préparation
    for m in range(num_machines):
        for i in range(num_jobs):
            for j in range(num_jobs):
                if i != j:
                    model.addConstr(
                        start[j, m] >= c[i, m] +
                        sum(setup_matrices[m][i_, j_] * x[i_, i] * x[j_, j] for i_ in range(num_jobs) for j_ in
                            range(num_jobs)) -
                        big_M * (1 - x[i, i] * x[j, j])
                    )

    # Fonction objectif
    if objective_type == "Cmax":  # Minimise le makespan
        model.setObjective(c[num_jobs - 1, num_machines - 1], GRB.MINIMIZE)
    elif objective_type == "TFT":  # Minimise le temps total de fin
        model.setObjective(sum(c[k, num_machines - 1] for k in range(num_jobs)), GRB.MINIMIZE)
    elif objective_type  == "TT":
        # Ajout de l'objectif : minimiser TT en tenant compte des temps de préparation
        T = model.addVars(num_jobs, vtype=GRB.CONTINUOUS, name="T")  # Variables de retard

        # Ajouter les contraintes de retard (Tardiness >= C_k - d_k) et Tardiness >= 0
        for k in range(num_jobs):
            model.addConstr(T[k] >= c[k, num_machines - 1] - deadlines[k])  # Tardiness >= C_k - d_k
            model.addConstr(T[k] >= 0)  # Tardiness >= 0

        # Définir l'objectif : minimiser le total des retards (Tardiness)
        model.setObjective(sum(T[k] for k in range(num_jobs)), GRB.MINIMIZE)

    else:
        raise ValueError("Invalid value for objective_type. Choose 'Cmax', 'TFT', or 'TT'.")

    # Résolution du modèle
    model.optimize()

    if model.Status == GRB.OPTIMAL:
        # Extraire la séquence optimale
        optimal_sequence = []
        for j in range(num_jobs):
            for i in range(num_jobs):
                if x[i, j].X > 0.5:
                    optimal_sequence.append(i)

        # Extraire les temps de début
        start_times = [[start[k, m].X for m in range(num_machines)] for k in range(num_jobs)]
        objective_value = model.ObjVal

        return optimal_sequence, start_times, objective_value
    else:
        return "No optimal solution found"

