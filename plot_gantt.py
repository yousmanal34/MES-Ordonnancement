import pandas as pd
import matplotlib.pyplot as plt
import customtkinter as ctk
from tkinter import filedialog
import numpy as np


def charger_donnees():
    """Ouvre une boîte de dialogue pour charger un fichier Excel et retourne les données."""
    fichier = filedialog.askopenfilename(filetypes=[("Fichiers Excel", ".xlsx;.xls")])
    if fichier:
        excel_file = pd.ExcelFile(fichier)
        print("Feuilles disponibles :", excel_file.sheet_names)  # Affiche les feuilles disponibles
        return excel_file
    return None


def lire_feuilles(excel_file, type_machine):
    """
    Lire les feuilles nécessaires selon le type de machine.

    Args:
        excel_file (pandas.ExcelFile): Fichier Excel à lire.
        type_machine (str): Type de machine ("Homogènes", "Uniformes", "Hétérogènes").

    Returns:
        dict: Dictionnaire contenant les DataFrames extraits des feuilles Excel.
    """
    feuilles = excel_file.sheet_names
    print(f"Feuilles disponibles : {feuilles}")

    donnees = {"jobs": None, "speeds": None, "weights": None, "deadlines": None, "arrivals": None, "nb_machines": None}

    try:
        # Charger la feuille "jobs" obligatoire
        if "jobs" not in feuilles:
            raise ValueError("La feuille 'jobs' est obligatoire et manquante.")
        donnees["jobs"] = excel_file.parse("jobs")
        print("Contenu de 'jobs':")
        print(donnees["jobs"].head())

        if "nb_machines" in feuilles:
            donnees["nb_machines"] = excel_file.parse("nb_machines").iloc[0, 0]
            print(f"Nombre de machines : {donnees['nb_machines']}")

        if type_machine == "Homogènes":
            donnees["weights"] = excel_file.parse("weights", index_col="Job") if "weights" in feuilles else None
            donnees["deadlines"] = excel_file.parse("deadlines", index_col="Job") if "deadlines" in feuilles else None
            donnees["arrivals"] = excel_file.parse("arrivals", index_col="Job") if "arrivals" in feuilles else None

        elif type_machine == "Uniformes":
            if "speeds" not in feuilles:
                raise ValueError("La feuille 'speeds' est obligatoire pour les machines uniformes.")
            donnees["speeds"] = excel_file.parse("speeds")
            print("Contenu de 'speeds':")
            print(donnees["speeds"].head())

            donnees["weights"] = excel_file.parse("weights", index_col="Job") if "weights" in feuilles else None
            donnees["deadlines"] = excel_file.parse("deadlines", index_col="Job") if "deadlines" in feuilles else None
            donnees["arrivals"] = excel_file.parse("arrivals", index_col="Job") if "arrivals" in feuilles else None

        elif type_machine == "Hétérogènes":
            donnees["weights"] = excel_file.parse("weights", index_col="Job") if "weights" in feuilles else None
            donnees["deadlines"] = excel_file.parse("deadlines", index_col="Job") if "deadlines" in feuilles else None
            donnees["arrivals"] = excel_file.parse("arrivals", index_col="Job") if "arrivals" in feuilles else None

    except Exception as e:
        print(f"Erreur lors du chargement des feuilles : {e}")
        raise

    # Vérification des données chargées
    for key, df in donnees.items():
        if df is not None:
            print(f"Feuille '{key}' chargée avec succès.")
        else:
            print(f"Feuille '{key}' absente ou vide.")

    return donnees


def preparer_donnees(donnees):
    jobs = donnees["jobs"].set_index("Job")
    if donnees["weights"] is not None:
        jobs = jobs.join(donnees["weights"])
    if donnees["deadlines"] is not None:
        jobs = jobs.join(donnees["deadlines"])
    if donnees["arrivals"] is not None:
        jobs = jobs.join(donnees["arrivals"])
    # Ne pas ajouter de colonne Arrival Time par défaut
    return jobs.reset_index()


def appliquer_regle(jobs, regle):
    # Check if it's heterogeneous or homogeneous machines
    is_heterogene = any(col.startswith("Processing Time Machine") for col in jobs.columns)

    if is_heterogene:
        if regle == "SPT":
            jobs["Min Processing Time"] = jobs.filter(regex="^Processing Time Machine").min(axis=1)
            return jobs.sort_values(by="Min Processing Time")
        elif regle == "LPT":
            jobs["Max Processing Time"] = jobs.filter(regex="^Processing Time Machine").max(axis=1)
            return jobs.sort_values(by="Max Processing Time", ascending=False)
        elif regle == "EDD":
            if "Deadline" not in jobs.columns:
                raise ValueError("La colonne 'Deadline' est manquante pour la règle EDD.")
            return jobs.sort_values(by="Deadline")
        elif regle == "WDD":
            if "Deadline" not in jobs.columns:
                raise ValueError("La colonne 'Deadline' est manquante pour la règle WDD.")
            if "Weight" not in jobs.columns:
                raise ValueError("La colonne 'Weight' est manquante pour la règle WDD.")
            jobs["Weighted Due Date"] = jobs["Weight"] * jobs["Deadline"]
            return jobs.sort_values(by="Weighted Due Date", ascending=False)
        elif regle == "FIFO" or regle == "LIFO":
            if "Arrival" not in jobs.columns:
                raise ValueError("La colonne 'Arrival' est manquante pour les règles FIFO/LIFO.")
            return jobs.sort_values(by="Arrival", ascending=(regle == "FIFO"))
        else:
            raise ValueError(f"Règle '{regle}' non prise en charge pour les machines hétérogènes.")
    else:
        # Case for homogeneous machines
        if "Processing Time" in jobs.columns:
            if regle == "SPT":
                return jobs.sort_values(by="Processing Time")
            elif regle == "LPT":
                return jobs.sort_values(by="Processing Time", ascending=False)
            elif regle == "EDD":
                if "Deadline" not in jobs.columns:
                    raise ValueError("La colonne 'Deadline' est manquante pour la règle EDD.")
                return jobs.sort_values(by="Deadline")
            elif regle == "WDD":
                if "Deadline" not in jobs.columns:
                    raise ValueError("La colonne 'Deadline' est manquante pour la règle WDD.")
                if "Weight" not in jobs.columns:
                    raise ValueError("La colonne 'Weight' est manquante pour la règle WDD.")
                jobs["Weighted Due Date"] = jobs["Weight"] * jobs["Deadline"]
                return jobs.sort_values(by="Weighted Due Date", ascending=False)
            elif regle == "FIFO" or regle == "LIFO":
                if "Arrival" not in jobs.columns:
                    raise ValueError("La colonne 'Arrival' est manquante pour les règles FIFO/LIFO.")
                return jobs.sort_values(by="Arrival", ascending=(regle == "FIFO"))
            else:
                raise ValueError(f"Règle '{regle}' non prise en charge pour les machines homogènes.")
        else:
            raise KeyError("Colonne 'Processing Time' manquante pour les machines homogènes.")


def assigner_taches_homogenes(jobs, nb_machines):
    """Assigner les tâches aux machines pour des machines homogènes en tenant compte des dates d'arrivée."""
    machines = [[] for _ in range(nb_machines)]
    temps_machines = [0] * nb_machines  # Temps de fin de chaque machine

    for _, row in jobs.iterrows():
        machine_idx = temps_machines.index(min(temps_machines))  # Choisir la machine la plus libre
        temps_debut = max(temps_machines[machine_idx],
                          row.get("Arrival", 0))  # Utiliser 0 si Arrival Time n'existe pas
        temps_fin = temps_debut + row["Processing Time"]  # Calculer le temps de fin pour cette tâche

        machines[machine_idx].append({
            'Job': row['Job'],
            'Temps début': temps_debut,
            'Temps fin': temps_fin
        })

        temps_machines[machine_idx] = temps_fin  # Mettre à jour le temps de fin de la machine

    return machines


def assigner_taches_uniformes(jobs, speeds):
    """Assigner les tâches aux machines pour des machines uniformes en tenant compte des vitesses, de la séquence de priorité et des dates d'arrivée."""
    nb_machines = len(speeds)
    machines = [None] * nb_machines  # Initialisation des machines avec None
    temps_machines = [0] * nb_machines  # Temps de fin de chaque machine

    # Créer un dictionnaire des vitesses des machines
    speeds_dict = dict(zip(speeds['Machine'], speeds['Speeds']))
    print("Dictionnaire des vitesses des machines :", speeds_dict)

    # Affecter chaque job en fonction de la séquence et des vitesses des machines
    for _, row in jobs.iterrows():
        print(f"Traitement de la tâche Job {row['Job']} avec temps de traitement {row['Processing Time']}")

        try:
            # Vérification des données avant d'effectuer les calculs
            if pd.isnull(row["Processing Time"]) or pd.isnull(row["Job"]):
                print(f"Erreur : Données manquantes pour le job {row['Job']} (temps de traitement ou job)")
                continue

            temps_min = float('inf')
            machine_choisie = -1
            # Calcul du temps de fin pour chaque machine en tenant compte de la vitesse et du temps de fin précédent
            for i in range(nb_machines):
                vitesse_machine = speeds_dict.get(speeds.iloc[i]['Machine'], 1)  # Valeur par défaut si vitesse est absente
                temps_debut_estime = max(temps_machines[i], row.get("Arrival", 0))
                temps_fin_estime = temps_debut_estime + row["Processing Time"] / vitesse_machine
                if temps_fin_estime < temps_min:
                    temps_min = temps_fin_estime
                    machine_choisie = i

            # Calcul du temps de début et de fin pour la tâche
            temps_debut = max(temps_machines[machine_choisie], row.get("Arrival", 0))
            temps_fin = temps_debut + row["Processing Time"] / speeds_dict[speeds.iloc[machine_choisie]['Machine']]

            # Ajouter la tâche à la machine choisie
            if machines[machine_choisie] is None:
                machines[machine_choisie] = []  # Créer une liste pour cette machine si elle n'existe pas encore

            machines[machine_choisie].append({
                'Job': row['Job'],
                'Temps début': temps_debut,
                'Temps fin': temps_fin
            })

            # Mettre à jour le temps de fin de la machine
            temps_machines[machine_choisie] = temps_fin

        except Exception as e:
            print(f"Erreur lors de l'assignation des tâches : {e}")
            break

    return machines

def assigner_taches_heterogenes(jobs):
    """Assigner les tâches aux machines pour des machines hétérogènes en tenant compte des dates d'arrivée."""
    # Identify the processing time columns
    processing_time_cols = [col for col in jobs.columns if col.startswith("Processing Time Machine")]

    if not processing_time_cols:
        raise ValueError("Aucune colonne 'Processing Time Machine' trouvée pour les machines hétérogènes.")

    nb_machines = len(processing_time_cols)
    machines = [[] for _ in range(nb_machines)]
    temps_machines = [0] * nb_machines

    # Iterate through the sorted jobs
    for _, job in jobs.iterrows():
        min_completion_time = float('inf')
        best_machine = -1

        # Find the machine that will complete the job the earliest
        for i in range(nb_machines):
            start_time = max(temps_machines[i], job.get("Arrival", 0))
            completion_time = start_time + job[processing_time_cols[i]]
            if completion_time < min_completion_time:
                min_completion_time = completion_time
                best_machine = i

        # Assign the job to the best machine
        start_time = max(temps_machines[best_machine], job.get("Arrival", 0))
        machines[best_machine].append({
            'Job': job['Job'],
            'Temps début': start_time,
            'Temps fin': min_completion_time
        })

        # Update the completion time for the chosen machine
        temps_machines[best_machine] = min_completion_time

    # Afficher les machines et les tâches affectées
    print(f"Machines après assignation: {machines}")

    return machines


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def tracer_gantt(machines, jobs):
    """Tracer un diagramme de Gantt pour des machines parallèles avec une palette de couleurs 'twilight_shifted'."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Calculer le nombre de jobs (n)
    n = len(jobs)  # jobs doit être un DataFrame ou un objet compatible avec len()

    # Générer la palette de couleurs
    palette = sns.color_palette("twilight_shifted", n_colors=n)
    colors = np.array(palette)  # Convertir la palette en tableau NumPy

    # Associer une couleur à chaque job
    job_colors = {job.Job: colors[i] for i, job in enumerate(jobs.itertuples())}

    # Tracer les tâches pour chaque machine
    for i, machine in enumerate(machines):
        # Vérifier si la machine est vide (None)
        if machine is None:
            # Tracer une barre vide pour la machine sans tâche
            ax.barh(y=f"Machine {i + 1}", width=0, left=0,
                    align='center', color='lightgray', edgecolor='black', linewidth=0.5)
           
            continue

        # Tracer les tâches assignées à la machine
        for tache in machine:
            if isinstance(tache, dict):
                job_id = tache['Job']
                debut = tache['Temps début']
                fin = tache['Temps fin']
            elif isinstance(tache, list):
                job_id, debut, fin = tache
            else:
                print(f"Format de tâche non reconnu: {tache}")
                continue

            # Récupérer la couleur associée au job
            couleur = job_colors[job_id]

            # Tracer la barre horizontale pour le job
            ax.barh(y=f"Machine {i + 1}", width=fin - debut, left=debut,
                    align='center', color=couleur, edgecolor='black', linewidth=0.5)

            # Ajouter le numéro du job et les temps de début et fin au centre de la barre
            ax.text(debut + (fin - debut) / 2, i, f"Job {job_id}\n{debut:.1f}-{fin:.1f}",
                    ha='center', va='center', color='black', fontsize=8, fontweight='bold')

    # Configuration des axes et titre
    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Machines Parallèles")
    plt.tight_layout()
    return fig
