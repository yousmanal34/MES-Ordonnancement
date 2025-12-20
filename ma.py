from pulp import *


from pulp import LpProblem, LpMinimize, LpVariable, lpSum

def create_hybrid_flowshop_milp(n, E, m, p, Q, release_times, due_dates, critere="TFT"):
    """
    Résolution du problème du flowshop hybride
    """
    # Création du problème
    prob = LpProblem("Hybrid_Flowshop", LpMinimize)

    # Variables de décision
    X = LpVariable.dicts("X",
                         ((k, j, e) for k in range(1, n + 1)
                                      for j in range(1, n + 1)
                                      for e in range(1, E + 1)),
                         cat='Binary')

    Y = LpVariable.dicts("Y",
                         ((k, e, l) for k in range(1, n + 1)
                                      for e in range(1, E + 1)
                                      for l in range(1, m[e - 1] + 1)),
                         cat='Binary')

    C = LpVariable.dicts("C",
                         ((k, e) for k in range(1, n + 1)
                                  for e in range(1, E + 1)),
                         lowBound=0)

    TT = LpVariable("TT", lowBound=0)  # Total tardiness
    TFT = LpVariable("TFT", lowBound=0)  # Total flow time
    Cmax = LpVariable("Cmax", lowBound=0)  # Makespan

    # Fonction objectif en fonction du critère choisi
    if critere == "Cmax":
        prob += Cmax
    elif critere == "TFT":
        prob += TFT
    elif critere == "TT":
        prob += TT

    else:
        raise ValueError("Critère inconnu. Choisissez entre 'Cmax', 'TFT' ou 'TT'.")

    for k in range(1, n + 1):
        prob += Cmax >= C[k, E]

    # (2) Chaque job est affecté une seule fois à chaque étage
    for k in range(1, n + 1):
        for e in range(1, E + 1):
            prob += lpSum(X[k, j, e] for j in range(1, n + 1)) == 1

    # (3) Chaque position est occupée une seule fois à chaque étage
    for j in range(1, n + 1):
        for e in range(1, E + 1):
            prob += lpSum(X[k, j, e] for k in range(1, n + 1)) == 1

    # (4) Chaque job est affecté à une seule machine par étage
    for k in range(1, n + 1):
        for e in range(1, E + 1):
            prob += lpSum(Y[k, e, l] for l in range(1, m[e - 1] + 1)) == 1

    # (5) Contrainte de temps pour le premier étage
    for k in range(1, n + 1):
        prob += C[k, 1] >= lpSum(X[k, j, 1] * p[k - 1][0] for j in range(1, n + 1))

    # (6) Contrainte de temps entre les étages
    for k in range(1, n + 1):
        for e in range(2, E + 1):
            prob += C[k, e] >= C[k, e - 1] + lpSum(X[k, j, e] * p[k - 1][e - 1] for j in range(1, n + 1))

    # (7) Contrainte de précédence entre jobs sur la même machine
    for e in range(1, E + 1):
        for l in range(1, m[e - 1] + 1):
            for j in range(1, n):
                for k in range(j + 1, n + 1):
                    prob += C[k, e] >= C[j, e] + lpSum(X[k, i, e] * p[k - 1][e - 1] for i in range(1, n + 1)) - \
                            Q * (3 - Y[j, e, l] - Y[k, e, l] - lpSum(X[k, i, e] for i in range(j + 1, n + 1)))

    # (8) Contrainte pour les release times : un job ne peut commencer qu'après son release time
    for k in range(1, n + 1):
        prob += release_times[k - 1] <= C[k, 1]

    # (9) Contrainte pour les due dates : tardiness pour chaque job
    tardiness = LpVariable.dicts("Tardiness", (k for k in range(1, n + 1)), lowBound=0)
    for k in range(1, n + 1):
        prob += tardiness[k] >= C[k, E] - due_dates[k - 1]  # Tardiness = CkE - DueDatek
        prob += tardiness[k] >= 0  # Si CkE < DueDatek, alors tardiness = 0
    # Ensure Cmax is at least as large as the completion time of every job
    for k in range(1, n + 1):
        prob += Cmax >= C[k, E]

    # Additional constraints to ensure Cmax is tight
    M = sum(max(p[i]) for i in range(n)) * n  # A sufficiently large number
    for k in range(1, n + 1):
        prob += Cmax <= C[k, E] + M * (1 - X[k, n, E])

    # Constraint for TFT (should be defined regardless of the chosen criterion)
    prob += TFT == lpSum(C[k, E] - release_times[k - 1] for k in range(1, n + 1))

    # Constraint for TT (should be defined regardless of the chosen criterion)
    prob += TT == lpSum(tardiness[k] for k in range(1, n + 1))



    # Contrainte pour le calcul du TFT
    # Contrainte pour le calcul du TFT


    return prob, X, Y, C, Cmax, TFT, TT
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_gantt_FH_MILP(schedule, makespan, TFT):
    """
    Affiche un diagramme de Gantt avec séparation entre les étages, une ligne horizontale pour Cmax,
    et les temps de début et de fin pour chaque tâche à l'intérieur des barres.

    :param schedule: Ordonnancement des tâches sous forme de dictionnaire {étage: {machine: [tâches]}}.
    :param makespan: Durée totale (Cmax).
    :param TFT: Temps de flux total (TFT).
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    # Déterminer le nombre total de jobs
    all_jobs = set()
    for stage in schedule.values():
        for machine in stage.values():
            all_jobs.update(task['job'] for task in machine)
    n = len(all_jobs)

    # Palette de couleurs, assurez-vous qu'il y a assez de couleurs pour tous les jobs
    palette = sns.color_palette("twilight_shifted", n)
    colors = np.array(palette)

    def get_text_color(bg_color):
        """Retourne la couleur du texte (blanc ou noir) selon la luminosité du fond"""
        return 'white' if np.mean(bg_color[:3]) < 0.5 else 'black'

    # Parcourir chaque étage et chaque machine pour afficher les tâches
    for stage, stage_schedule in schedule.items():
        for machine, tasks in stage_schedule.items():
            for task in tasks:
                job = task['job']
                start_time = task['start']
                end_time = task['end']
                duration = end_time - start_time

                ax.barh(
                    y=f"Étage {stage} - Machine {machine}",
                    width=duration,
                    left=start_time,
                    color=colors[job % len(colors)],
                    edgecolor="black",
                    label=f"Job {job}" if f"Job {job}" not in ax.get_legend_handles_labels()[1] else None,
                )

                # Ajouter les informations de job et les temps de début/fin à l'intérieur des barres
                ax.text(
                    x=(start_time + end_time) / 2,
                    y=f"Étage {stage} - Machine {machine}",
                    s=f"J{job}\n{start_time:.1f}-{end_time:.1f}",
                    ha='center',
                    va='center',
                    color=get_text_color(colors[job % len(colors)]),
                    fontsize=8,
                    fontweight='bold'
                )

    # Ajouter les lignes horizontales pour Cmax et TFT
    ax.axvline(makespan, color="red", linestyle="--", label=f"Cmax = {makespan:.2f}")
    ax.axvline(TFT, color="blue", linestyle="--", label=f"TFT = {TFT:.2f}")

    # Configuration des axes et du titre
    ax.set_xlabel("Temps")
    ax.set_ylabel("Étages et Machines")
    ax.set_title("Diagramme de Gantt - Flowshop Hybride")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1))

    # Ajuster les limites de l'axe x pour avoir un peu d'espace pour les étiquettes
    ax.set_xlim(0, makespan + 1)

    plt.tight_layout()
    return fig

