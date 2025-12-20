import customtkinter as ctk
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")
import numpy as np
from tkinter import messagebox
# Charger les données des jobs depuis un fichier Excel

import seaborn as sns
# Appliquer une règle de priorité pour ordonner les jobs
def appliquer_priorite(jobs, priorite):
    try:
        if priorite == "SPT":
            return sorted(jobs, key=lambda job: sum(op[1] for op in job["operations"]))
        elif priorite == "LPT":
            return sorted(jobs, key=lambda job: sum(op[1] for op in job["operations"]), reverse=True)
        elif priorite in ["FIFO", "LIFO"] and all("arrival_time" in job for job in jobs):
            return sorted(jobs, key=lambda job: job["arrival_time"], reverse=(priorite == "LIFO"))
        elif priorite == "EDD" and all("deadline" in job for job in jobs):
            return sorted(jobs, key=lambda job: job["deadline"])
        elif priorite == "WDD" and all("deadline" in job and "weight" in job for job in jobs):
            return sorted(jobs, key=lambda job: job["weight"] * job["deadline"], reverse=True)
        else:
            raise ValueError("Les données nécessaires pour appliquer la priorité sont manquantes.")
    except ValueError as e:
        messagebox.showerror("Erreur", str(e))
        return jobs



def generer_gantt_jobshop(DEBUT, FIN, jobs, m, setup_times, deadlines=None):
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(12, 8))

    palette = sns.color_palette("twilight_shifted", n_colors=len(jobs))
    colors = np.array(palette)

    bar_height = 0.4
    job_colors = {}  # Dictionnaire pour les couleurs des jobs
    legend_prep_added = False  # Contrôle pour la légende de préparation

    completion_times = [0] * len(jobs)  # Initialiser les temps de fin pour chaque job
    tardiness = [0] * len(jobs)  # Initialiser la tardivité (TT) pour chaque job
    TFT = 0  # Temps total d'écoulement
    deadlines = [job["deadline"] for job in jobs]

    for machine_id in range(m):
        for idx, (job_id, start) in enumerate(DEBUT[machine_id]):
            _, end = FIN[machine_id][idx]
            prep_start = setup_times[machine_id][idx][1]  # Début de la préparation
            prep_duration = start - prep_start  # Durée de la préparation

            # Associer une couleur unique à chaque job
            if job_id not in job_colors:
                job_colors[job_id] = colors[job_id]

            # Stocker le temps de fin pour chaque job
            completion_times[job_id] = max(completion_times[job_id], end)

            # Afficher la barre pour la préparation
            if prep_duration > 0:
                ax.barh(
                    machine_id,
                    prep_duration,
                    left=prep_start,
                    height=bar_height,
                    color="gray",
                    alpha=0.5,
                    edgecolor="black",
                    label="Préparation" if not legend_prep_added else None
                )
                legend_prep_added = True  # Légende ajoutée pour la préparation

                # Afficher le temps de préparation au centre de la barre
                ax.text(
                    prep_start + prep_duration / 2,
                    machine_id,
                    f"{int(prep_duration)}",  # Supprime le .0
                    ha='center',
                    va='center',
                    color="black",
                    fontsize=9,
                    fontweight="bold"
                )

            # Afficher la barre pour l'opération
            operation_duration = end - start
            ax.barh(
                machine_id,
                operation_duration,
                left=start,
                height=bar_height,
                color=job_colors[job_id],
                edgecolor="black",
                label=f"J{job_id + 1}" if job_id not in job_colors else None
            )

            # Afficher le nom du job et les dates début-fin en gras
            ax.text(
                start + operation_duration / 2,
                machine_id,
                f"J{job_id + 1}\n{int(start)}-{int(end)}",  # Supprime le .0
                ha='center',
                va='center',
                color="white",
                fontsize=9,
                fontweight="bold"
            )

    # Calculer TFT en tenant compte des arrival times
    TFT = 0
    for job in jobs:
        job_id = job["job_id"] - 1  # Indices des jobs (0-based)
        arrival_time = job["arrival_time"] if job["arrival_time"] is not None else 0
        flow_time = completion_times[job_id] - arrival_time
        TFT += flow_time

    # Calculer TT si les deadlines sont fournies
    if deadlines:
        for job in jobs:
            job_id = job["job_id"] - 1
            deadline = deadlines[job_id]
            tardiness[job_id] = max(0, completion_times[job_id] - deadline)

    # Calculer Cmax
    Cmax = max(completion_times)
    TT = sum(tardiness)

    # Débogage : afficher les temps de fin, tardivités et TFT
    print("Temps de fin des tâches (completion_times) :", completion_times)
    if deadlines:
        print("Tardivité par tâche (tardiness) :", tardiness)
    print("TFT (Total Flow Time) :", TFT)

    # Configurer l'axe Y pour les machines
    ax.set_yticks(range(m))
    ax.set_yticklabels([f"Machine {i + 1}" for i in range(m)])
    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt")
    if TT !=0:
        # Ajuster la position de TFT, TT et Cmax dans une zone compacte au-dessus
        summary_text = (
            f"TFT = {TFT}    |    Cmax = {Cmax}    |    TT = {sum(tardiness)}"
        )
    else:
        summary_text = (
            f"TFT = {TFT}    |    Cmax = {Cmax}    "
        )

    fig.text(
        0.5,
        0.95,
        summary_text,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        bbox=dict(facecolor="white", alpha=0.7),
    )

    # Ajouter une légende complète
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Supprime les duplications dans la légende
    ax.legend(by_label.values(), by_label.keys(), loc="upper right")

    plt.tight_layout()
    return fig







import matplotlib.pyplot as plt
def appliquer_algorithme_jackson(P, O):
    """Applique l'algorithme de Jackson pour générer les séquences des machines."""
    n = len(P[0])

    # Initialisation des listes pour les jobs
    C1, C2, C12, C21 = [], [], [], []
    U12, V12, U21, V21 = [], [], [], []

    # Classification des jobs selon les matrices O
    for i in range(n):
        if O[0, i] == 1 and O[1, i] == 0:
            C1.append(i)
        elif O[0, i] == 2 and O[1, i] == 0:
            C2.append(i)
        elif O[0, i] == 1 and O[1, i] == 2:
            C12.append(i)
        elif O[0, i] == 2 and O[1, i] == 1:
            C21.append(i)

    # Traitement de C12
    a = len(C12)
    P_C12 = P[:, C12]

    for i in range(a):
        if P_C12[1, i] > P_C12[0, i]:
            U12.append(i)
        else:
            V12.append(i)

    U12.sort(key=lambda x: P_C12[0, x])
    V12.sort(key=lambda x: P_C12[1, x], reverse=True)

    C12ordre = U12 + V12
    C12_sorted = [C12[i] for i in C12ordre]

    # Traitement de C21
    b = len(C21)
    P_C21 = P[:, C21]

    for i in range(b):
        if P_C21[1, i] > P_C21[0, i]:
            V21.append(i)
        else:
            U21.append(i)

    U21.sort(key=lambda x: P_C21[0, x])
    V21.sort(key=lambda x: P_C21[1, x], reverse=True)

    C21ordre = U21 + V21
    C21_sorted = [C21[i] for i in C21ordre]

    # Construction des séquences des machines
    Machine1seq = C12_sorted + C1 + C21_sorted
    Machine2seq = C21_sorted + C2 + C12_sorted

    return Machine1seq, Machine2seq

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generer_gantt_jackson(P, Machine1seq, Machine2seq):
    """Génère un diagramme de Gantt pour les séquences des machines, avec affichage des temps et du Cmax."""
    plt.close('all')
    n = len(P[0])
    m1 = len(Machine1seq)
    m2 = len(Machine2seq)

    # Initialisation des vecteurs de début et de fin
    DEBUTM1 = [0] * (n + 1)
    FINM1 = [0] * (n + 1)
    DEBUTM2 = [0] * (n + 1)
    FINM2 = [0] * (n + 1)

    # Calculer le début et la fin pour chaque job dans Machine 1
    DEBUTM1[Machine1seq[0]] = 0
    FINM1[Machine1seq[0]] = P[0, Machine1seq[0]]
    for j in range(1, m1):
        DEBUTM1[Machine1seq[j]] = FINM1[Machine1seq[j - 1]]
        FINM1[Machine1seq[j]] = DEBUTM1[Machine1seq[j]] + P[0, Machine1seq[j]]

    # Calculer le début et la fin pour chaque job dans Machine 2
    DEBUTM2[Machine2seq[0]] = 0
    FINM2[Machine2seq[0]] = P[1, Machine2seq[0]]
    for z in range(1, m2):
        DEBUTM2[Machine2seq[z]] = FINM2[Machine2seq[z - 1]]
        FINM2[Machine2seq[z]] = DEBUTM2[Machine2seq[z]] + P[1, Machine2seq[z]]

    # Calcul du Cmax (temps total d'achèvement)
    Cmax = max(max(FINM1), max(FINM2))

    # Diagramme de Gantt
    fig, ax = plt.subplots(figsize=(15, 8))

    # Générer une liste de couleurs uniques pour les jobs
    palette = sns.color_palette("twilight_shifted", n_colors=n)
    colors = np.array(palette)

    # Afficher le diagramme de Gantt pour Machine 1
    for i, job_idx in enumerate(Machine1seq):
        color = colors[job_idx % len(colors)]
        ax.barh('Machine 1', FINM1[job_idx] - DEBUTM1[job_idx], left=DEBUTM1[job_idx], color=color, edgecolor='black')
        # Affichage du numéro du job au centre de la barre
        ax.text((DEBUTM1[job_idx] + FINM1[job_idx]) / 2, 0, f'Job {job_idx + 1}\n {DEBUTM1[job_idx]} - {FINM1[job_idx]}', ha='center', va='center', color='black')

    # Afficher le diagramme de Gantt pour Machine 2
    for i, job_idx in enumerate(Machine2seq):
        color = colors[job_idx % len(colors)]
        ax.barh('Machine 2', FINM2[job_idx] - DEBUTM2[job_idx], left=DEBUTM2[job_idx], color=color, edgecolor='black')
        # Affichage du numéro du job au centre de la barre
        ax.text((DEBUTM2[job_idx] + FINM2[job_idx]) / 2, 1, f'Job {job_idx + 1}\n{DEBUTM2[job_idx]} - {FINM2[job_idx]}', ha='center', va='center', color='black')
        # Affichage des temps début et fin sous le nom du job

    # Ajouter une ligne verticale pour indiquer le Cmax
    ax.axvline(Cmax, color='red', linestyle='--', label=f'Cmax = {Cmax}')
    ax.text(Cmax, 1.5, f'Cmax = {Cmax}', color='red', fontsize=12, ha='center', va='bottom')

    # Ajouter des étiquettes et un titre
    ax.set_xlabel('Temps')
    ax.set_title('Diagramme de Gantt des machines')
    ax.grid(True)
    ax.legend(loc='upper right')

    return fig

def simulate_order(jobs, schedule, deadlines=None, arrivals=None):
    """
    Simule un ordre de travail donné et calcule les métriques Cmax, TFT, et TT.
    """
    n_jobs = len(jobs)
    machine_avail = [0] * (max(op[0] for job in jobs for op in job) + 1)
    job_completion = [0] * n_jobs  # Date de fin de chaque job

    # Mettre à jour les dates de fin pour chaque tâche
    for job_idx, machine, start, end in schedule:
        machine_avail[machine] = end
        job_completion[job_idx] = max(job_completion[job_idx], end)  # La date de fin est la dernière fin du job

    # Calcul des métriques
    cmax = max(machine_avail)
    tft = sum(job_completion[j] - arrivals.get(j, 0) for j in range(n_jobs)) if arrivals else sum(job_completion)
    tt = sum(max(0, job_completion[j] - deadlines.get(j, float('inf'))) for j in range(n_jobs)) if deadlines else 0

    return cmax, tft, tt
def calculer_TFT(DEBUT, FIN, n_jobs, n_machines):
    """
    Calcule le Total Flow Time (TFT) à partir des horaires de début et de fin.
    """
    TFT = 0
    for machine_id in range(n_machines):
        for job_id, fin_time in FIN[machine_id]:
            TFT += fin_time  # Somme des temps de fin de chaque job
    return TFT
def calculer_TT(DEBUT, FIN, n_jobs, deadlines, n_machines):
    """
    Calcule le Total Tardiness (TT) à partir des horaires de début et de fin, ainsi que des deadlines des jobs.
    """
    TT = 0
    for machine_id in range(n_machines):
        for job_id, fin_time in FIN[machine_id]:
            deadline = deadlines[job_id]
            tardiness = max(0, fin_time - deadline)  # Si le job est en retard, on l'ajoute au TT
            TT += tardiness
    return TT
