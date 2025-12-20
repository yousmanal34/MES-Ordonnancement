import pandas as pd
import pulp as pl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


import pulp as pl

def solve_jobshop_flexible(PROC, MACH, PRESENCE, Arrivals, deadlines, critere):
    jobs = range(1, len(PROC) + 1)  # Nombre de jobs
    machines = range(1, len(PROC[0]) + 1)  # Nombre de machines
    operations = range(1, len(PROC[0]) + 1)  # Nombre d'opérations
    if deadlines is None  and critere=="TT":
        raise ValueError("Erreur : La liste des deadlines ne peut pas être vide ou None.")

    model = pl.LpProblem("Flexible_Job_Shop", pl.LpMinimize)

    # Variables
    START = pl.LpVariable.dicts("START", [(j, o) for j in jobs for o in operations], lowBound=0, cat=pl.LpContinuous)
    X = pl.LpVariable.dicts("X", [(j1, o1, j2, o2) for j1 in jobs for o1 in operations
                                  for j2 in jobs for o2 in operations], cat=pl.LpBinary)

    CMAX = pl.LpVariable("Cmax", lowBound=0, cat=pl.LpContinuous)
    TFT = pl.LpVariable("TFT", lowBound=0, cat=pl.LpContinuous)
    TT = pl.LpVariable("TT", lowBound=0, cat=pl.LpContinuous)

    # Critère de minimisation
    if critere == "Cmax":
        model += CMAX
    elif critere == "TFT":
        model += TFT
    elif critere == "TT":
        model += TT
    else:
        raise ValueError("Critère inconnu. Utilisez 'Cmax', 'TFT', ou 'TT'.")

    # Contraintes de précédence
    for j in jobs:
        for i in range(1, len(operations)):
            model += (
                START[j, i] + PROC[j-1][i-1] * PRESENCE[j-1][i-1] <= START[j, i+1] +
                1000 * (2 - PRESENCE[j-1][i-1] - PRESENCE[j-1][i])
            )

    # Contraintes de non-chevauchement sur les machines
    for j1 in jobs:
        for j2 in jobs:
            if j1 != j2:
                for i in operations:
                    for k in operations:
                        for m in machines:
                            if MACH[j1-1][i-1] == m and MACH[j2-1][k-1] == m:
                                model += (
                                    START[j1, i] + PROC[j1-1][i-1] * PRESENCE[j1-1][i-1] <=
                                    START[j2, k] + 1000 * (1 - X[j1, i, j2, k])
                                )
                                model += (
                                    START[j2, k] + PROC[j2-1][k-1] * PRESENCE[j2-1][k-1] <=
                                    START[j1, i] + 1000 * X[j1, i, j2, k]
                                )

    # Définition de CMAX
    for j in jobs:
        for i in operations:
            model += (
                CMAX >= START[j, i] + PROC[j-1][i-1] * PRESENCE[j-1][i-1]
            )

    # Contrainte sur les heures d'arrivée
    for j in jobs:
        model += START[j, 1] >= Arrivals[j-1]

    # Définition de TFT
    model += TFT == pl.lpSum(
        START[j, i] + PROC[j-1][i-1] * PRESENCE[j-1][i-1]
        for j in jobs for i in operations
    )

    # Définition de TT
    for j in jobs:
        model += TT >= (
            START[j, len(operations)] + PROC[j-1][len(operations)-1] * PRESENCE[j-1][len(operations)-1] - deadlines[j-1]
        )
        model += TT >= 0

    # Résolution
    model.solve()

    # Récupérer les résultats des variables de démarrage
    job_operations = {j: {i: START[j, i].varValue for i in operations} for j in jobs}

    # Retourner la valeur de l'objectif
    if critere == "Cmax":
        return job_operations, CMAX.varValue
    elif critere == "TFT":
        return job_operations, TFT.varValue
    elif critere == "TT":
        return job_operations, TT.varValue


def solve_jobshop_prepa(PROC, MACH, PRESENCE, SETUP, Arrivals, deadlines, critere="Cmax"):
    jobs = range(1, len(PROC) + 1)  # Nombre de jobs
    machines = range(1, len(PROC[0]) + 1)  # Nombre de machines
    operations = range(1, len(PROC[0]) + 1)
    if deadlines is None and critere=="TT":
        raise ValueError("Erreur : La liste des deadlines ne peut pas être vide ou None.")

    model = pl.LpProblem("Flexible_Job_Shop", pl.LpMinimize)

    # Variables
    START = pl.LpVariable.dicts("START", [(j, o) for j in jobs for o in operations], lowBound=0, cat=pl.LpContinuous)
    X = pl.LpVariable.dicts("X", [(j1, o1, j2, o2) for j1 in jobs for o1 in operations
                                  for j2 in jobs for o2 in operations], cat=pl.LpBinary)

    CMAX = pl.LpVariable("Cmax", lowBound=0, cat=pl.LpContinuous)
    TFT = pl.LpVariable("TFT", lowBound=0, cat=pl.LpContinuous)
    TT = pl.LpVariable("TT", lowBound=0, cat=pl.LpContinuous)

    # Critère de minimisation
    if critere == "Cmax":
        model += CMAX  # Minimiser le makespan (temps total)
    elif critere == "TFT":
        model += TFT  # Minimiser le temps total de traitement
    elif critere == "TT":
        model += TT  # Minimiser la somme des retards
    else:
        raise ValueError("Critère inconnu. Utilisez 'CMAX', 'TFT', ou 'TT'.")

    # Contraintes de précédence
    for j in jobs:
        for i in operations[:-1]:
            model += (
                    START[j, i] + PROC[j - 1, i - 1] * PRESENCE[j - 1, i - 1] <= START[j, i + 1] + 1000 * (
                    2 - PRESENCE[j - 1, i - 1] - PRESENCE[j - 1, i])
            )

    # Contraintes de non-chevauchement sur les machines avec temps de préparation
    for j1 in jobs:
        for j2 in jobs:
            if j1 != j2:
                for i in operations:
                    for k in operations:
                        for m in machines:
                            if MACH[j1 - 1, i - 1] == m and MACH[j2 - 1, k - 1] == m:
                                # Contrôler l'ordonnancement pour éviter les chevauchements
                                model += (
                                        START[j1, i] + PROC[j1 - 1, i - 1] * PRESENCE[j1 - 1, i - 1] + SETUP[
                                    m - 1, j1 - 1, j2 - 1]
                                        <= START[j2, k] + 1000 * (1 - X[j1, i, j2, k])
                                )
                                model += (
                                        START[j2, k] + PROC[j2 - 1, k - 1] * PRESENCE[j2 - 1, k - 1] + SETUP[
                                    m - 1, j2 - 1, j1 - 1]
                                        <= START[j1, i] + 1000 * X[j1, i, j2, k]
                                )

    # Définition de CMAX
    if critere == "Cmax":
        for j in jobs:
            for i in operations:
                model += (
                        CMAX >= START[j, i] + PROC[j - 1, i - 1] + SETUP[MACH[j - 1, i - 1] - 1, j - 1, j - 1] *
                        PRESENCE[j - 1, i - 1]
                )

    # Contrainte sur les heures d'arrivée
    for j in jobs:
        for i in operations:
            model += (
                    START[j, i] >= Arrivals[j - 1]  # Le job ne peut commencer avant son arrivée
            )


    # Définition de TFT
    if critere == "TFT":
        model += TFT == pl.lpSum(
            START[j, i] + PROC[j - 1, i - 1] * PRESENCE[j - 1, i - 1] for j in jobs for i in operations)

    # Définition de TT
    if critere == "TT":
        # Calculer le retard (tardiness) pour chaque job et opération
        for j in jobs:
            for i in operations:
                model += TT >= (START[j, i] + PROC[j - 1, i - 1] * PRESENCE[j - 1, i - 1]) - deadlines[j - 1]
                model += TT >= 0  # Assurer que la tardiness est positive

    # Contraintes de non-négativité
    for j in jobs:
        for i in operations:
            model += START[j, i] >= 0

    # Résolution
    model.solve()
    # Récupérer les résultats
    job_operations = {}
    for j in jobs:
        job_operations[j] = {}
        for i in operations:
            job_operations[j][i] = START[j, i].varValue if START[j, i].varValue is not None else 0

    if critere == "Cmax":
        return job_operations, CMAX.varValue
    elif critere == "TFT":
        return job_operations, TFT.varValue
    elif critere == "TT":
        return job_operations, TT.varValue


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def generer_gantt_Jobshop_MILP(job_operations, PROC, MACH, SETUP, deadlines):

    # Vérification des entrées
    if not job_operations or not PROC.size or not MACH.size or not SETUP.size:
        raise ValueError("Les données d'entrée sont invalides ou vides.")
    if deadlines is not None and not deadlines.size:
        raise ValueError("La liste des deadlines est vide ou invalide.")

    # Utilisation de la palette Seaborn pour les couleurs des jobs
    num_jobs = len(job_operations)
    palette = sns.color_palette("twilight_shifted", n_colors=num_jobs)
    colors = np.array(palette)
    color_map = {job: colors[job - 1] for job in job_operations.keys()}

    gris = '#BEBEBE'  # Couleur pour les temps de préparation
    rouge_pale = '#FFCCCB'  # Couleur pour les temps d'attente ou blocage

    fig, ax = plt.subplots(figsize=(12, 8))

    n_machines = int(np.max(MACH))  # Nombre de machines

    # Initialisation des variables pour Cmax, TFT et TT
    Cmax = 0
    TFT = 0
    TT = 0 if deadlines is not None else None  # TT initialisé uniquement si deadlines est fourni

    # Dictionnaire pour suivre le dernier job sur chaque machine
    last_job_on_machine = {m: None for m in range(1, n_machines + 1)}

    for job, operations in job_operations.items():
        for op, start_time in operations.items():
            try:
                machine = (MACH[job - 1, op - 1])  # Machine pour cette opération
                duration = (PROC[job - 1, op - 1])  # Durée de l'opération
                end_time = start_time + duration

                # Mise à jour des métriques
                Cmax = max(Cmax, end_time)
                TFT += end_time
                if deadlines is not None and op == len(operations):
                    TT += max(0, end_time - (deadlines[job - 1]))

                # Calcul du temps de préparation
                setup_time = 0
                if last_job_on_machine[machine] is None:
                    # Premier job sur la machine
                    setup_time = (SETUP[machine - 1][job - 1, job - 1])
                else:
                    # Temps de préparation entre le dernier job sur cette machine et le job actuel
                    prev_job = last_job_on_machine[machine]
                    setup_time = (SETUP[machine - 1][prev_job - 1, job - 1])

                # Affichage du temps de préparation si > 0
                if setup_time > 0:
                    preparation_start = start_time - setup_time
                    ax.barh(machine - 1, setup_time, left=preparation_start, height=0.6,
                            color=gris, alpha=0.5)
                    ax.text(preparation_start + setup_time / 2, machine - 1,
                            f'{setup_time:.1f}', ha='center', va='center',
                            color='black', fontsize=9)

                # Affichage de l'opération
                if duration > 0:
                    ax.barh(machine - 1, duration, left=start_time, height=0.6,
                            color=color_map[job])
                    ax.text(start_time + duration / 2, machine - 1,
                            f'J{job}\n{start_time:.1f}-{end_time:.1f}',
                            ha='center', va='center', color='black', fontweight='bold')

                # Mise à jour du dernier job sur la machine
                last_job_on_machine[machine] = job

            except Exception as e:
                print(f"Erreur lors du traitement du job {job}, opération {op}: {str(e)}")
                continue

    # Ajouter les métriques et la légende
    summary_text = f"Cmax = {Cmax:.1f}    |    TFT = {TFT:.1f}"
    if TT is not None:
        summary_text += f"    |    TT = {TT:.1f}"

    fig.text(0.5, 0.95, summary_text, ha="center", va="center",
             fontsize=12, fontweight="bold",
             bbox=dict(facecolor="white", alpha=0.7))

    # Configuration du graphique
    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Job Shop")
    ax.set_yticks(range(n_machines))
    ax.set_yticklabels([f"Machine {m + 1}" for m in range(n_machines)])
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Supprimer les labels dupliqués dans la légende
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),
               loc='center left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    return fig
