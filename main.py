import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import matplotlib.cm as cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
from MILPS import*
from MILPCB import *
from MILPSC import *
from MILPNOIDLE import *
from MILPNOWAIT import *
from RSNI import *
from RSSC import *
from RSSETUP import *
from RSB import *
from C import *
from RSNW import *
from FH import *
from ma import *
from MILP_JS import *
from plot_gantt import *

# Configure the appearance

ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "dark-blue", "green"
ctk.set_appearance_mode("dark")
# Interface CustomTkinter

# Palette de couleurs
PRIMARY_COLOR = "#000000"  # noir
SECONDARY_COLOR = "#003366"  # bleu
ACCENT_COLOR = "#003366"  # Bleu

ctk.set_appearance_mode("dark")
method_selected1 = False
method_selected2 = False
method_selected3= False

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


def reset():
    global global_data6
    global_data6 = None  # Réinitialiser les données globales

    # Vérifier si fichier_excel est un Label ou un bouton, et mettre à jour son texte
    if isinstance(fichier_excel, ctk.CTkLabel):  # Si c'est un label
        fichier_excel.configure(text="Aucun fichier sélectionné")  # Mettre à jour le texte
    elif isinstance(fichier_excel, ctk.CTkButton):  # Si c'est un bouton
        fichier_excel.configure(text="Aucun fichier sélectionné")  # Mettre à jour le texte


def reset_fichier():
    global global_data, method_selected1, method_selected2, method_selected3
    global global_data2

    # Réinitialiser les données globales
    global_data = None
    global_data2 = None

    # Réinitialiser les sélections de méthodes
    method_selected1 = False
    method_selected2 = False
    method_selected3 = False

    # Mettre à jour le texte du bouton
    button_excel.configure(text="Aucun fichier sélectionné")

    # Met à jour le texte du label avec le chemin
    print("Les données ont été réinitialisées.")
def reset_fichier2():
    global method_selected4,method_selected5,method_selected6
    global data_ex,data_OP,data_jack
    if method_selected4:
        data_OP=None
        button_excel1.configure(text="Aucun fichier sélectionné")
    if method_selected5:
        data_jack=None
        button_excel_JACK.configure(text="Aucun fichier sélectionné")
    if method_selected6:
        data_ex=None
        button_excel_ex.configure(text="Aucun fichier sélectionné")












def get_input_from_excel():
    file_path = filedialog.askopenfilename(title="Sélectionnez votre fichier Excel",
                                           filetypes=[("Fichiers Excel", "*.xlsx")])
    if not file_path:
        print("Aucun fichier sélectionné.")
        return None, None, None, None, None

    if file_path:
        button_excel.configure(text=file_path)

    try:
        # Lecture des temps de traitement
        processing_times = pd.read_excel(file_path, sheet_name="P", header=None).values
        m, n = processing_times.shape
    except Exception as e:
        print(f"Erreur lors de la lecture de la matrice 'P' : {e}")
        return None, None, None, None, None

    # Initialiser les variables par défaut
    S = []
    release_times = np.zeros(n)  # Par défaut : [0, 0, ..., 0]
    Due_dates = None
    W = None

    # Lecture des matrices de setup (S)
    for i in range(m):
        sheet_name = f"S{i}"
        try:
            setup_matrix = pd.read_excel(file_path, sheet_name=sheet_name, header=None).values
            S.append(setup_matrix)
        except:
            S.append(None)

    # Lecture des dates d'échéance (D)
    try:
        Due_dates = pd.read_excel(file_path, sheet_name="D", header=None).values.flatten()
    except:
        Due_dates = np.zeros(n)

    # Lecture des poids (W)
    try:
        W = pd.read_excel(file_path, sheet_name="W", header=None).values.flatten()
    except:
        W = None

    # Lecture des temps de disponibilité (R)
    try:
        release_times = pd.read_excel(file_path, sheet_name="R", header=None).values.flatten()
    except:
        print("Feuille 'R' introuvable ou invalide, utilisation de la valeur par défaut [0, 0, ..., 0].")
        release_times = np.zeros(n)

    # Afficher les données lues pour débogage
    print("release_times:", release_times)

    return processing_times, S, Due_dates, W, release_times


# Fonction pour générer le diagramme de Gantt
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.patches as patches

def generer_gantt_Flowshop(DEBUT, FIN, ATTENTE, job_sequence, m, n, S, constraint, Cmax, TFT, TT):
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    # Utilisation de la palette Seaborn pour les couleurs des jobs
    palette = sns.color_palette("twilight_shifted", n_colors=n)
    colors = np.array(palette)

    gris = '#BEBEBE'  # Couleur pour les temps de préparation
    rouge_pale = '#FFCCCB'  # Couleur pour les temps de blocage
    noir='#000000'

    fig, ax = plt.subplots(figsize=(12, 8))

    for j in range(n):
        for i in range(m):
            # Afficher les jobs (barres des jobs)
            ax.barh(i, FIN[i, j] - DEBUT[i, j], left=DEBUT[i, j], height=0.6, color=colors[j],
                    label=f'Job {job_sequence[j] + 1}' if i == 0 else "")

            # Ajouter le texte indiquant le temps et le nom du job
            ax.text(DEBUT[i, j] + (FIN[i, j] - DEBUT[i, j]) / 2, i,
                    f'J{job_sequence[j] + 1}\n{int(DEBUT[i, j])}-{int(FIN[i, j])}',
                    ha='center', va='center', color='black', fontweight='bold')

            # Vérifier et afficher les temps de préparation (S) en gris
            if S is not None and all(item is not None for item in S):
                setup_matrices = np.stack(S, axis=2)  # Conversion de la liste S en une matrice 3D
                S_current = setup_matrices[:, :, i]  # Temps de préparation pour la machine i

                if j > 0:  # Temps de préparation entre jobs
                    preparation_start = FIN[i, j - 1]
                    preparation_end = preparation_start + S_current[job_sequence[j - 1], job_sequence[j]]

                    # Affichage du temps de préparation
                    ax.barh(i, preparation_end - preparation_start, left=preparation_start, height=0.6, color=gris,
                            alpha=0.5)
                    ax.text(preparation_start + (preparation_end - preparation_start) / 2, i,
                            f'S={int(S_current[job_sequence[j - 1], job_sequence[j]])}',
                            ha='center', va='bottom', color='black', fontsize=9)

                if j == 0:  # Temps de préparation initial
                    preparation_start = DEBUT[i, j] - S_current[job_sequence[j], job_sequence[j]]
                    preparation_end = preparation_start + S_current[job_sequence[j], job_sequence[j]]

                    ax.barh(i, preparation_end - preparation_start, left=preparation_start, height=0.6, color=gris,
                            alpha=0.5)
                    ax.text(preparation_start + (preparation_end - preparation_start) / 2, i,
                            f'S={int(S_current[job_sequence[j], job_sequence[j]])}',
                            ha='center', va='bottom', color='black', fontsize=9)


            if constraint == "blocking" and i < m - 1:
                        blocking_time = ATTENTE[i+1, j]  # Vérifiez que ATTENTE[i+1, j] contient bien les données
                        if blocking_time > 0:
                            blocking_start = FIN[i-1, j]  # Temps de fin de l'opération précédente sur la machine
                            blocking_end = blocking_start + blocking_time


                            # Affichage de la barre pour le temps de blocage
                            ax.barh(i, blocking_time, left=blocking_start, height=0.6, color="black", alpha=0.7,
                                    edgecolor="black", linewidth=1.2)

                            # Ajouter un texte pour indiquer le temps de blocage
                            ax.text(blocking_start + blocking_time / 2, i,
                                    f'B={int(blocking_time)}', ha='center', va='bottom', color='white', fontsize=9)

                            # Pour déboguer et vérifier si le blocage est bien calculé
                            print(f"Job {j} on Machine {i} has blocking time: {blocking_time}")

    # Ajouter les métriques (Cmax, TFT, TT) et la séquence sur une seule ligne
    if TT !=0:
        summary_text = (
            f"Sequence: {'-'.join([f'J{job + 1}' for job in job_sequence])}    |    "
            f"Cmax = {Cmax}    |    TFT = {TFT}    |    TT = {TT}"
        )
    else:   summary_text = (
        f"Sequence: {'-'.join([f'J{job + 1}' for job in job_sequence])}    |    "
        f"Cmax = {Cmax}    |    TFT = {TFT}  "
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

    ax.set_xlabel('Temps')
    ax.set_ylabel('Machines')
    ax.set_title('Diagramme de Gantt des Jobs sur les Machines')
    ax.set_yticks(range(m))
    ax.set_yticklabels([f'Machine {i + 1}' for i in range(m)])
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Légende des jobs
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    return fig

global_data = None
# Fonction pour lancer l'ordonnancement et afficher le Gantt dans Tkinter
def charger_fichier_excel():
    global global_data

    if global_data is not None:
        # Si les données sont déjà chargées, on ne redemande pas le fichier
        print("Les données sont déjà chargées depuis le fichier.")
        return global_data

    try:
        # Supposons que get_input_from_excel est une fonction pour charger les matrices du fichier
        processing_times, S, Due_dates, W, release_times = get_input_from_excel()
        if processing_times is None:
            print("Erreur : Impossible de lire la matrice 'P'.")
            return None, None, None, None, None
        # Enregistrer les données dans la variable globale
        global_data = (processing_times, S, Due_dates, W, release_times)

        return global_data
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return None, None, None, None, None
def charger_donnees_jobshop():
    import pandas as pd
    import numpy as np
    from tkinter import filedialog, messagebox

    # Demander à l'utilisateur de sélectionner un fichier Excel
    file_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx")]
    )

    if not file_path:
        messagebox.showerror("Erreur", "Aucun fichier sélectionné.")
        return None, None, None, None, None, None, None, None

    try:
        jobs = []
        sheet_names = pd.ExcelFile(file_path).sheet_names
        print("Feuilles disponibles :", sheet_names)

        arrivals_dict, deadlines_dict, weights_dict = {}, {}, {}
        has_arrivals = "Arrivals" in sheet_names
        has_deadlines = "Deadlines" in sheet_names
        has_weights = "Weights" in sheet_names

        # Charger les feuilles optionnelles si elles existent
        if has_arrivals:
            try:
                arrivals = pd.read_excel(file_path, sheet_name="Arrivals", header=None)
                arrivals_dict = dict(zip(arrivals.iloc[:, 0], arrivals.iloc[:, 1]))
                print("Données de la feuille Arrivals chargées avec succès.")
            except Exception as e:
                print(f"Erreur lors du chargement de la feuille Arrivals : {e}")

        if has_deadlines:
            try:
                deadlines = pd.read_excel(file_path, sheet_name="Deadlines", header=None)
                deadlines_dict = dict(zip(deadlines.iloc[:, 0], deadlines.iloc[:, 1]))
                print("Données de la feuille Deadlines chargées avec succès.")
            except Exception as e:
                print(f"Erreur lors du chargement de la feuille Deadlines : {e}")

        if has_weights:
            try:
                weights = pd.read_excel(file_path, sheet_name="Weights", header=None)
                weights_dict = dict(zip(weights.iloc[:, 0], weights.iloc[:, 1]))
                print("Données de la feuille Weights chargées avec succès.")
            except Exception as e:
                print(f"Erreur lors du chargement de la feuille Weights : {e}")

        max_machine = 0

        # Parcourir toutes les feuilles pour charger les jobs
        for sheet in sheet_names:
            if sheet in ["Arrivals", "Deadlines", "Weights"] or sheet.startswith("S"):
                continue

            try:
                job_data = pd.read_excel(file_path, sheet_name=sheet, header=None).values
                print(f"Données de la feuille {sheet} chargées avec succès.")
            except Exception as e:
                print(f"Erreur lors du chargement de la feuille {sheet} : {e}")
                continue

            if job_data.shape[1] < 2:
                raise ValueError(f"La feuille {sheet} n'a pas le format attendu.")

            operations = [(int(row[0]), int(row[1])) for row in job_data]
            max_machine = max(max_machine, max(op[0] for op in operations))
            job_id = len(jobs) + 1

            jobs.append({
                "job_id": job_id,
                "arrival_time": arrivals_dict.get(job_id, 0),  # Valeur par défaut : 0
                "deadline": deadlines_dict.get(job_id, float('inf')),  # Valeur par défaut : inf
                "weight": weights_dict.get(job_id, 1),  # Valeur par défaut : 1
                "operations": operations
            })

        # Charger les matrices de setup (feuilles S)
        S = []
        for i in range(max_machine):
            sheet_name = f"S{i + 1}"
            if sheet_name in sheet_names:
                try:
                    setup_matrix = pd.read_excel(file_path, sheet_name=sheet_name, header=None).values
                    if setup_matrix.shape[0] != len(jobs) or setup_matrix.shape[1] != len(jobs):
                        raise ValueError(f"La matrice {sheet_name} n'a pas les dimensions attendues.")
                    S.append(setup_matrix)
                except Exception as e:
                    print(f"Erreur lors du chargement de la feuille {sheet_name} : {e}")
                    S.append(np.zeros((len(jobs), len(jobs))))
            else:
                S.append(np.zeros((len(jobs), len(jobs))))

        return jobs, max_machine, len(jobs), np.zeros((max_machine, len(jobs))), S, has_arrivals, has_deadlines, has_weights, file_path

    except Exception as e:
        messagebox.showerror("Erreur", f"Problème lors du chargement des données : {e}")
        return None, None, None, None, None, None, None, None

def load_data_from_excel():
    file_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx")]
    )
    if not file_path:
        raise ValueError("Aucun fichier sélectionné.")

    # Mettre à jour l'affichage du chemin de fichier
    button_excel_ex.configure(text=file_path)

    # Charger le fichier Excel
    excel_data = pd.ExcelFile(file_path)

    # Charger les matrices pour PROC, MACH, PRESENCE
    PROC = excel_data.parse('PROC', header=None).to_numpy()  # Si la feuille s'appelle 'PROC'
    MACH = excel_data.parse('MACH', header=None).to_numpy()  # Si la feuille s'appelle 'MACH'
    PRESENCE = excel_data.parse('PRESENCE', header=None).to_numpy()  # Si la feuille s'appelle 'PRESENCE'

    M = len(PROC[0])  # Nombre de machines
    n = len(PROC)  # Nombre d'opérations par job

    # Initialisation des variables par défaut
    Arrivals = np.zeros(n)
    deadlines = np.zeros(n)
    Weights = np.zeros(n)

    # Vérifier si les feuilles 'Arrivals', 'Deadlines' existent et les charger si disponibles
    if 'Arrivals' in excel_data.sheet_names:
        Arrivals = excel_data.parse('Arrivals', header=None).to_numpy().flatten()
    else:
        print("Feuille 'Arrivals' absente. Initialisation avec des zéros.")

    if 'Deadlines' in excel_data.sheet_names:
        deadlines = excel_data.parse('Deadlines', header=None).to_numpy().flatten()
    else:
        print("Feuille 'Deadlines' absente. Initialisation avec des zéros.")

    if 'Weights' in excel_data.sheet_names:
        Weights_df = pd.read_excel(file_path, sheet_name="Weights", header=None)
        Weights = Weights_df.to_numpy()
    else:
        print("Feuille 'Weights' absente. Initialisation avec des zéros.")

    # Charger les matrices SETUP pour chaque machine dans une matrice 3D
    SETUP = np.zeros((M, n, n), dtype=int)  # Dimensions: M machines, n jobs

    # Essayer de charger les données SETUP pour chaque machine

    for m in range(M):
        setup_sheet_name = f'Machine_{m + 1}'  # Nom de la feuille pour chaque machine

        if setup_sheet_name in excel_data.sheet_names:
            # Lecture de la matrice de la feuille Excel
            setup_data = excel_data.parse(setup_sheet_name, header=None).to_numpy()

            # Vérification de la dimension de la matrice
            if setup_data.shape == (n, n):
                SETUP[m] = setup_data
            else:
                print(
                    f"Attention: La feuille '{setup_sheet_name}' a une dimension incorrecte. Attendu ({n}, {n}), mais trouvé {setup_data.shape}.")
                SETUP[m] = np.zeros((n, n),
                                    dtype=int)  # Remplace par une matrice n*n de zéros en cas d'erreur de dimension
        else:
            print(f"Attention: La feuille '{setup_sheet_name}' n'a pas été trouvée dans le fichier.")
            SETUP[m] = np.zeros((n, n), dtype=int)  # Si la feuille n'existe pas, on initialise avec des zéros

    return PROC, MACH, PRESENCE, SETUP, Arrivals, deadlines, Weights
data_OP=None
data_jack=None
data_ex=None
def charger_donnees_jobshop_2():
    """Charger les données Excel et mettre à jour les variables globales."""
    global  data_OP, data_jack, data_ex
    global method_selected4, method_selected5, method_selected6

    # Vérification des états initiaux
    print("État des méthodes sélectionnées :")
    print(f"method_selected4 (Jobshop): {method_selected4}")
    print(f"method_selected5 (Jackson): {method_selected5}")
    print(f"method_selected6 (Setup): {method_selected6}")
    if data_OP is not None:
        return data_OP
    if data_jack is not None:
        return data_jack
    if data_ex is not None:
        return data_ex
    try:# Méthode Jobshop
        if method_selected4:
            print("Chargement des données pour Jobshop...")
            jobs, max_machine, n, T, S, has_arrivals, has_deadlines, has_weights, file_path = charger_donnees_jobshop()
            data_OP = jobs, max_machine, n, T, S, has_arrivals, has_deadlines, has_weights, file_path
            return data_OP

        # Méthode Jackson
        if method_selected5:
            print("Chargement des données pour Jackson...")
            P, O, Arrivals, Deadlines = charger_donnees_jackson()
            data_jack = P, O, Arrivals, Deadlines
            return data_jack

        # Méthode avec setup et autres paramètres
        if method_selected6:
            print("Chargement des données avec setup...")
            PROC, MACH, PRESENCE, SETUP, Arrivals, Deadlines, Weights = load_data_from_excel()
            if PROC is None or PROC.size == 0:
                raise ValueError("Les données des jobs sont invalides pour la méthode sélectionnée (method_selected6).")
            Arrivals = np.zeros(PROC.shape[0]) if Arrivals is None else Arrivals
            Deadlines = np.zeros(PROC.shape[0]) if Deadlines is None else Deadlines
            data_ex = PROC, MACH, PRESENCE, SETUP, Arrivals, Deadlines, Weights
            return data_ex
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")



fichier_excel=None
def charger_fichier_excel1():
    global fichier_excel

    # Demander à l'utilisateur de sélectionner un fichier Excel
    fichier_excel = filedialog.askopenfilename(
        title="Sélectionnez votre fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx")]
    )

    if fichier_excel:
        # Mettre à jour l'interface (par exemple un label ou un bouton)
        button_excel2.configure(text=f"Fichier sélectionné: {fichier_excel}")
        # Charger les données du fichier Excel et les stocker dans global_data6
        global global_data6
        global_data6 = charger_donnees_excel_FH()  # Charger les données globales
    else:
        messagebox.showerror("Erreur", "Aucun fichier sélectionné.")

global_data6 = None

# Fonction pour charger un fichier Excel


# Fonction pour charger les données depuis le fichier Excel
def charger_donnees_excel_FH():
    global fichier_excel  # Utilise le fichier global

    if not fichier_excel:
        messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel.")
        return None, None, None, None, None, None, None

    try:
        # Charger les données des différentes feuilles du fichier Excel
        jobs_df = pd.read_excel(fichier_excel, sheet_name='jobs', header=None)
        machines_df = pd.read_excel(fichier_excel, sheet_name='Machines par étage', header=None)
        release_times_df = pd.read_excel(fichier_excel, sheet_name='Release Times', header=None)
        due_dates_df = pd.read_excel(fichier_excel, sheet_name='Due Dates', header=None)
        weights_df = pd.read_excel(fichier_excel, sheet_name='Weights', header=None)

        # Transposer la feuille P (jobs) pour que chaque colonne représente un job
        jobs = jobs_df.to_numpy().T.tolist()
        n = jobs_df.shape[1]  # Nombre de jobs (colonnes)
        stages=jobs_df.shape[0]

        # Charger les autres données
        machines_per_stage = machines_df[0].tolist()
        release_times = release_times_df[0].to_numpy().tolist()

        # Gérer les feuilles optionnelles
        due_dates = due_dates_df[0].to_numpy().tolist() if not due_dates_df.empty else None
        weights = weights_df[0].to_numpy().tolist() if not weights_df.empty else None

        # Nombre d'étages (lignes dans la matrice initiale)


        return n, jobs, stages, machines_per_stage, release_times, due_dates, weights

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement des données : {e}")
        return None, None, None, None, None, None, None

def lancer_ordonnancement_OP_flowshop():
    processing_times, S, D, W, release_times = charger_fichier_excel()
    c = choix_sequence.get()
    m, n = processing_times.shape
    global k
    job_sequence = list(range(n))

    # Votre code de calcul pour DEBUT et FIN selon les contraintes choisies
    if c == "LIFO":
        job_sequence = [i for i, _ in sorted(enumerate(release_times), key=lambda x: -x[1])]
    elif c == "FIFO":
        job_sequence = [i for i, _ in sorted(enumerate(release_times), key=lambda x: x[1])]
    elif c == "LPT":
        p2 = [0] * n
        for i in range(m):
            for j in range(n):
                p2[j] += processing_times[i, j]
        job_sequence = [i for i, _ in sorted(enumerate(p2), key=lambda x: -x[1])]
    elif c == "SPT":
        p2 = [0] * n
        for i in range(m):
            for j in range(n):
                p2[j] += processing_times[i, j]
        job_sequence = [i for i, _ in sorted(enumerate(p2), key=lambda x: x[1])]
    elif c == "EDD":
        job_sequence = [i for i, _ in sorted(enumerate(D), key=lambda x: x[1])]
    elif c == "WDD":
        W2 = W * D
        job_sequence = [i for i, _ in sorted(enumerate(W2), key=lambda x: -x[1])]


    elif c == "JHONSON" :
        U = []
        V = []
        U2 = []
        V2 = []
        for j in range(n):
            if processing_times[0, j] < processing_times[1, j]:
                U.append(processing_times[0, j])
                U2.append(j)
            else:
                V.append(processing_times[1, j])
                V2.append(j)

            # Trier les temps de traitement et leurs indices pour les deux groupes
        U_sorted_indices = np.argsort(U)
        V_sorted_indices = np.argsort(V)[::-1]

        # Appliquer le tri des indices pour avoir la séquence ordonnée des jobs
        U_sequence = [U2[i] for i in U_sorted_indices]
        V_sequence = [V2[i] for i in V_sorted_indices]
        job_sequence = U_sequence + V_sequence
        print(job_sequence)
    elif c == "CDS":
        U = []
        V = []
        U2 = []
        V2 = []
        p1 = np.zeros(n)
        p2 = np.zeros(n)
        for i in range(k):
            p1 += processing_times[i, :]
            p2 += processing_times[-1 - i, :]
        print(p1, p2)
        p_cds = np.vstack((p1, p2))
        for j in range(n):
            if p_cds[0, j] < p_cds[1, j]:
                U.append(p_cds[0, j])
                U2.append(j)
            else:
                V.append(p_cds[1, j])
                V2.append(j)
        U_sorted_indices = np.argsort(U)
        V_sorted_indices = np.argsort(V)[::-1]

        # Appliquer le tri des indices pour avoir la séquence ordonnée des jobs
        U_sequence = [U2[i] for i in U_sorted_indices]
        V_sequence = [V2[i] for i in V_sorted_indices]
        job_sequence = U_sequence + V_sequence
    else:
        print("Séquence invalide.")
        exit()
    return job_sequence

def lancer_ordonnancement_ME_flowshop():
    """
    Find optimal sequences for Cmax, TFT, and TT with no-wait constraint.
    """
    processing_times, S, D, W, release_times = charger_fichier_excel()
    valeur_optim=v0
    M=valeur_optim.get()
    m, n = processing_times.shape
    choix_contraintes = selection2
    if choix_contraintes.get():  # Si une valeur est sélectionnée dans `selection1`
        c = choix_contraintes.get()
    elif choix_contraintes.get():  # Sinon, si une valeur est sélectionnée dans `selection2`
        c = choix_contraintes.get()

        # Calcul des métriques en fonction de la contrainte choisie
    if c == "no idle":
        job_sequence=flowshop_scheduling_with_objective_no_idle(processing_times,release_times,D,M)
    elif c=="no wait":
        job_sequence = flowshop_scheduling_with_objective_no_wait(processing_times, release_times,D, M)
    elif c=="blocking":
        job_sequence = flowshop_scheduling_with_objective_blocking(processing_times, release_times,D, M)
    elif c=="temps de préparation":
        job_sequence = flowshop_scheduling_with_preparation(processing_times, release_times,S,D, M)
    else:job_sequence=flowshop_scheduling_with_objective(processing_times,release_times,D, M)




    return job_sequence


def lancer_ordonancement_MA_flowshop():
      processing_times, S, D, W, release_times = charger_fichier_excel()
      valeur_optim=v1
      M=valeur_optim.get()
      c = selection3.get()
      if c=="no idle":
          job_sequence=simulated_annealing_scipy_noidle(processing_times,release_times,M)
      elif c=="no wait":
          job_sequence=simulated_annealing_scipy_nowait(processing_times,release_times,M)
      elif c=="temps de préparation":
          job_sequence=simulated_annealing_scipy_with_setups(processing_times,release_times,S,M)
      else :job_sequence=simulated_annealing_scipy(processing_times,release_times,M)

      return job_sequence

global_data2=None
def Ordonancer_flowshop():
    global global_data2

    # Charger les données
    processing_times, S, D, W, release_times = charger_fichier_excel()
    m, n = processing_times.shape

    job_sequence = lancer_ordonnancement_OP_flowshop()  # Exemple : méthode OP
    c = selection1.get()  # Valeur de sélection dans le premier menu déroulant
    DEBUT = np.zeros((m, n))
    FIN = np.zeros((m, n))
    ATTENTE = np.zeros((m, n))

    # Calcul de DEBUT et FIN pour le premier job sur chaque machine
    DEBUT[0, 0] = release_times[job_sequence[0]]
    FIN[0, 0] = DEBUT[0, 0] + processing_times[0, job_sequence[0]]

    for i in range(1, m):
        DEBUT[i, 0] = FIN[i - 1, 0]
        FIN[i, 0] = DEBUT[i, 0] + processing_times[i, job_sequence[0]]

    # Calcul de DEBUT et FIN pour les autres jobs sur chaque machine
    for j in range(1, n):
        DEBUT[0, j] = max(release_times[job_sequence[j]], FIN[0, j - 1])
        FIN[0, j] = DEBUT[0, j] + processing_times[0, job_sequence[j]]
        for i in range(1, m):
            DEBUT[i, j] = max(FIN[i - 1, j], FIN[i, j - 1])
            FIN[i, j] = DEBUT[i, j] + processing_times[i, job_sequence[j]]
            if DEBUT[i, j] > FIN[i - 1, j]:
                ATTENTE[i, j] = DEBUT[i, j] - FIN[i - 1, j]

    # Calcul des arrêts (arret_total) pour chaque machine
    arret_total = np.zeros(m)
    for i in range(m):
        arret = 0
        for j in range(1, n):
            if DEBUT[i, j] > FIN[i, j - 1]:
                arret += DEBUT[i, j] - FIN[i, j - 1]
        arret_total[i] = arret

    # Appliquer les contraintes
    if c == "no idle":
        DEBUT[0, 0] = release_times[job_sequence[0]] + arret_total[0]
        FIN[0, 0] = DEBUT[0, 0] + processing_times[0, job_sequence[0]]

        for i in range(1, m):
            DEBUT[i, 0] = FIN[i - 1, 0] + arret_total[i]
            FIN[i, 0] = DEBUT[i, 0] + processing_times[i, job_sequence[0]]

        for j in range(1, n):
            for i in range(1, m):
                DEBUT[i, j] = FIN[i, j - 1]
                FIN[i, j] = DEBUT[i, j] + processing_times[i, job_sequence[j]]

    elif c == "no wait":
        DEBUT[0, 0] = release_times[job_sequence[0]]
        FIN[0, 0] = DEBUT[0, 0] + processing_times[0, job_sequence[0]]

        for i in range(1, m):
            DEBUT[i, 0] = FIN[i - 1, 0]
            FIN[i, 0] = DEBUT[i, 0] + processing_times[i, job_sequence[0]]

        for j in range(1, n):
            DEBUT[0, j] = max(release_times[job_sequence[j]], FIN[0, j - 1]) + ATTENTE[1, job_sequence[j]]
            FIN[0, j] = DEBUT[0, j] + processing_times[0, job_sequence[j]]
            for i in range(1, m):
                DEBUT[i, j] = FIN[i - 1, j]
                FIN[i, j] = DEBUT[i, j] + processing_times[i, job_sequence[j]]


    elif c == "blocking":

        # Initialisation du premier job sur la première machine

        DEBUT[0, 0] = release_times[job_sequence[0]]

        FIN[0, 0] = DEBUT[0, 0] + processing_times[0, job_sequence[0]]

        # Calcul pour les machines suivantes du premier job

        for i in range(1, m):
            DEBUT[i, 0] = max(FIN[i - 1, 0], FIN[i, 0] if i > 0 else 0)

            FIN[i, 0] = DEBUT[i, 0] + processing_times[i, job_sequence[0]]

        # Calcul pour les autres jobs

        for j in range(1, n):

            # Calcul pour la première machine

            DEBUT[0, j] = max(release_times[job_sequence[j]], FIN[0, j - 1])

            FIN[0, j] = DEBUT[0, j] + processing_times[0, job_sequence[j]]

            # Calcul pour les autres machines

            for i in range(1, m):

                # Prendre en compte la contrainte de blocking

                DEBUT[i, j] = max(FIN[i - 1, j], FIN[i, j - 1])

                if i < m - 1:  # Si ce n'est pas la dernière machine

                    DEBUT[i, j] = max(DEBUT[i, j], FIN[i, j - 1])

                FIN[i, j] = DEBUT[i, j] + processing_times[i, job_sequence[j]]

                # Calcul du temps d'attente pour le blocking

                if i < m - 1:  # Si ce n'est pas la dernière machine

                    ATTENTE[i, j] = max(0, FIN[i, j] - DEBUT[i + 1, j])

                else:

                    ATTENTE[i, j] = 0

    elif S is not None and all(item is not None for item in S):
        S0 = S[0]
        setup_matrices = np.stack(S, axis=2)

        DEBUT[0, 0] = release_times[job_sequence[0]] + S0[job_sequence[0], job_sequence[0]]
        FIN[0, 0] = DEBUT[0, 0] + processing_times[0, job_sequence[0]]

        for i in range(1, m):
            S_current = setup_matrices[:, :, i]
            DEBUT[i, 0] = max(FIN[i - 1, 0], S_current[job_sequence[0], job_sequence[0]])
            FIN[i, 0] = DEBUT[i, 0] + processing_times[i, job_sequence[0]]

        for j in range(1, n):
            DEBUT[0, j] = max(release_times[job_sequence[j]], FIN[0, j - 1]) + S0[job_sequence[j - 1], job_sequence[j]]
            FIN[0, j] = DEBUT[0, j] + processing_times[0, job_sequence[j]]
            for i in range(1, m):
                S_current = setup_matrices[:, :, i]
                DEBUT[i, j] = max(FIN[i - 1, j], FIN[i, j - 1] + S_current[job_sequence[j - 1], job_sequence[j]])
                FIN[i, j] = DEBUT[i, j] + processing_times[i, job_sequence[j]]

    # Calcul des indicateurs de performance
    Cmax = np.max(FIN)  # Temps total (makespan)
    TFT =calculate_total_flow_time(FIN,job_sequence)
    TT =calculate_total_tardiness(FIN,D,job_sequence)

    # Génération du diagramme de Gantt avec les indicateurs
    global fig
    fig = generer_gantt_Flowshop(DEBUT, FIN, ATTENTE, job_sequence, m, n, S, c,Cmax,TFT,TT)

    global_data2 = (FIN, job_sequence)
    return global_data2


import numpy as np


def calculate_total_tardiness(FIN, deadlines, job_sequence):
    """
    Calcule le Total Tardiness (TT).

    :param FIN: Tableau 2D numpy des temps de fin par machine (n_machines x n_jobs).
    :param deadlines: Liste des dates limites pour chaque job.
    :param job_sequence: Liste représentant l'ordre des jobs dans la séquence.
    :return: Total Tardiness (TT).
    """
    n_jobs = len(deadlines)
    if np.all(deadlines == 0):
        TT = 0
    else:
        TT=0
        # Parcourir les jobs dans la séquence donnée
        for j in range(n_jobs):
            job_id = job_sequence[j]  # Identifier le job dans la séquence
            finish_time = FIN[-1, j]  # Temps de fin pour ce job
            deadline = deadlines[job_id]  # Deadline correspondante

            # Calculer le retard et l'ajouter à TT
            tardiness = max(0, finish_time - deadline)
            TT += tardiness


    return TT
import numpy as np

def calculate_total_flow_time(FIN, job_sequence):
    """
    Calcule le Total Flow Time (TFT).

    :param FIN: Tableau 2D numpy des temps de fin par machine (n_machines x n_jobs).
    :param job_sequence: Liste représentant l'ordre des jobs dans la séquence.
    :return: Total Flow Time (TFT).
    """
    n_jobs = len(job_sequence)
    TFT = 0

    # Parcourir les jobs dans la séquence donnée
    for j in range(n_jobs):
        job_id = job_sequence[j]  # Identifier le job dans la séquence
        finish_time = FIN[-1, j]  # Temps de fin pour ce job sur la dernière machine
        TFT += finish_time

    return TFT


def Ordonancer_ME_MA():
    global method_selected2, method_selected3, fig

    # Charger les données depuis Excel
    processing_times, S, D, W, release_times = charger_fichier_excel()

    # Vérification des méthodes sélectionnées
    if method_selected2 and not method_selected3:
        # Appel pour la méthode 2
        job_sequence = lancer_ordonnancement_ME_flowshop()
        fig = plot_gantt_chart(job_sequence[0], job_sequence[1], S)

    elif method_selected3 and not method_selected2:
        # Appel pour la méthode 3
        job_sequence = lancer_ordonancement_MA_flowshop()
        fig = plot_gantt_chart(job_sequence[0], job_sequence[1], S)

    else:
        # Gérer le cas où aucune méthode ou les deux sont sélectionnées
        raise ValueError("Veuillez sélectionner une seule méthode : ME ou MA.")

def calculate_blocking_time(end, next_start, tolerance=1e-6):
    if next_start > end + tolerance:
        return end, next_start
    return None
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_gantt_chart(sequence, start_times, setup_matrices=None):
    """
    Plot a Gantt chart for the flowshop schedule with various constraints.

    Args:
    sequence (List[int]): Optimal sequence of jobs (0-based index).
    start_times (List[List[float]]): Start times for each job on each machine.
    setup_matrices (List[List[List[int]]], optional): Setup times between jobs for each machine.
    """
    processing_times, S, D, W, release_times = charger_fichier_excel()
    constraint = get_constraint()

    num_machines, num_jobs = processing_times.shape
    n = len(sequence)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = get_color_palette(sequence)

    FIN = np.zeros((num_machines, n))

    if constraint == "temps de préparation":
        plot_with_setup_times(ax, sequence, start_times, processing_times, setup_matrices, colors, FIN)
    elif constraint == "blocking":
        plot_with_blocking(ax, sequence, start_times, processing_times, colors, FIN)
    else:
        plot_without_constraint(ax, sequence, start_times, processing_times, colors, FIN)

    set_chart_properties(ax, num_machines, constraint)
    add_summary(fig, sequence, FIN, D)

    plt.tight_layout()
    return fig


def get_constraint():
    global method_selected3, method_selected2
    if method_selected2:
        return selection2.get()
    else:
        return selection3.get()


def get_color_palette(sequence):
    palette = sns.color_palette("twilight_shifted", len(sequence))
    return np.array(palette)


def plot_with_setup_times(ax, sequence, start_times, processing_times, setup_matrices, colors, FIN):
    for m in range(len(processing_times)):
        for j_idx, job in enumerate(sequence):
            start_time = start_times[j_idx][m]
            processing_time = processing_times[m][job]
            end_time = start_time + processing_time
            FIN[m, j_idx] = end_time

            setup_time = get_setup_time(setup_matrices, m, sequence, j_idx, job)
            if setup_time > 0:
                plot_setup_bar(ax, m, start_time, setup_time, j_idx)

            plot_processing_bar(ax, m, start_time, processing_time, colors[job % len(colors)], job, j_idx)
            add_job_text(ax, m, start_time, end_time, processing_time, job)


def get_setup_time(setup_matrices, m, sequence, j_idx, job):
    if j_idx > 0:
        prev_job = sequence[j_idx - 1]
        return setup_matrices[m][prev_job, job]
    return setup_matrices[m][job, job]


def plot_setup_bar(ax, m, start_time, setup_time, j_idx):
    ax.barh(y=m, width=setup_time, left=start_time - setup_time, height=0.4,
            color="gray", edgecolor="black", label="Setup" if m == 0 and j_idx == 1 else None)
    ax.text(x=start_time - setup_time / 2, y=m, s=f"\n{setup_time:.1f}",
            ha="center", va="center", color="black", fontsize=8)


def plot_processing_bar(ax, m, start_time, processing_time, color, job, j_idx):
    ax.barh(y=m, width=processing_time, left=start_time, height=0.4,
            color=color, edgecolor="black",
            label=f"Job {job + 1}" if m == 0 and j_idx == 0 else None)




def add_job_text(ax, m, start_time, end_time, processing_time, job):
    ax.text(x=start_time + processing_time / 2, y=m,
            s=f"J{job + 1}\n{start_time:.1f}-{end_time:.1f}",
            ha="center", va="center", color="white", fontsize=9, fontweight="bold")


def plot_with_blocking(ax, sequence, start_times, processing_times, colors, FIN):
    for i, job in enumerate(sequence):
        for machine in range(len(processing_times)):
            start = start_times[i][machine]
            duration = processing_times[machine][job]
            end = start + duration
            FIN[machine, i] = end

            ax.broken_barh([(start, duration)], (machine - 0.4, 0.8),
                           facecolors=colors[i % len(sequence)], edgecolor="black", linewidth=1.2)
            ax.text(start + duration / 2, machine, f"J{job + 1}\n{start:.1f}-{end:.1f}",
                    ha='center', va='center', color='white', fontsize=9)

            if machine < len(processing_times) - 1:
                next_start = start_times[i][machine + 1]
                blocking_time = calculate_blocking_time(end, next_start)
                if blocking_time:
                    plot_blocking_time(ax, machine, blocking_time)


def plot_blocking_time(ax, machine, blocking_time):
    block_start, block_end = blocking_time
    block_duration = block_end - block_start
    if block_duration > 1e-6:
        ax.broken_barh([(block_start, block_duration)], (machine - 0.4, 0.8),
                       facecolors="black", edgecolor="black", alpha=0.7)
        ax.text(block_start + block_duration / 2, machine - 0.2,
                f"{block_start:.1f}-{block_end:.1f}", color="white", ha="center", va="center", fontsize=8)


def plot_without_constraint(ax, sequence, start_times, processing_times, colors, FIN):
    for i, job in enumerate(sequence):
        for machine in range(len(processing_times)):
            start = start_times[i][machine]
            duration = processing_times[machine][job]
            end = start + duration
            FIN[machine, i] = end

            ax.barh(machine, duration, left=start, height=0.5, align='center',
                    color=colors[i % len(sequence)], alpha=0.8)
            ax.text(start + duration / 2, machine, f'J{job + 1}\n{start:.1f}-{end:.1f}',
                    va='center', ha='center', fontweight='bold', color="white")


def set_chart_properties(ax, num_machines, constraint):
    ax.set_ylim(-0.5, num_machines - 0.5)
    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f'M{i + 1}' for i in range(num_machines)])
    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_title(f'Flowshop Schedule Gantt Chart ({constraint if constraint else "No Constraint"})')
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1), fontsize=8)


def add_summary(fig, sequence, FIN, D):
    Cmax = np.max(FIN)
    TFT = calculate_total_flow_time(FIN, sequence)
    TT = calculate_total_tardiness(FIN, D, sequence)
    if TT==0:
        summary_text = (
            f"Sequence: {'-'.join([f'J{job + 1}' for job in sequence])}  Cmax={Cmax}   |  TFT = {TFT}    "
        )
    else:  summary_text = (
        f"Sequence: {'-'.join([f'J{job + 1}' for job in sequence])}  Cmax={Cmax}   |  TFT = {TFT}    |    TT = {TT}"
    )

    fig.text(0.5, 0.95, summary_text, ha="center", va="center", fontsize=12, fontweight="bold",
             bbox=dict(facecolor="white", alpha=0.7))






import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def calcul():
    processing_times, S, D, W, release_times = charger_fichier_excel()
    global method_selected3, method_selected2, method_selected1

    # Lancer l'ordonnancement selon la méthode sélectionnée
    if method_selected1:
        FIN, job_sequence = Ordonancer_flowshop()
        Cmax = np.max(FIN)
    elif method_selected2:
        job_sequence, START, O = lancer_ordonnancement_ME_flowshop()
        Cmax=O
    elif method_selected3:
        job_sequence, START, O = lancer_ordonancement_MA_flowshop()
        Cmax=O

    m, n = processing_times.shape  # Nombre de machines (m) et d'opérations (n)
      # Cmax est la durée maximale des tâches
    TFR1 = []
    TFR2 = []
    TAR1 = []
    TAR2 = []

    # Vérifier si S est valide (pas None et non vide)
    if S is not None and all(item is not None for item in S):
        setup_matrices = np.stack(S, axis=2)  # Assurez-vous que S a une forme valide
        for i in range(m):
            S_current = setup_matrices[:, :, i]
            T1 = 0
            T2 = 0
            for j in range(n):
                T1 += processing_times[i, j]
                if j == job_sequence[0]:
                    T2 += processing_times[i, j] + S_current[job_sequence[0], job_sequence[0]]
                else:
                    T2 += processing_times[i, j] + S_current[j - 1, j]
            TFR1.append(T1)
            TFR2.append(T2)
    else:  # Si S est vide ou None, calculer uniquement TFR1
        for i in range(m):
            T1 = sum(processing_times[i, j] for j in range(n))
            TFR1.append(T1)

    # Normalisation des TFR et calcul des TAR
    TFR1 = np.array(TFR1) / Cmax * 100
    TAR1 = 100 - TFR1
    if S is not None and all(item is not None for item in S):
        TFR2 = np.array(TFR2) / Cmax * 100
        TAR2 = 100 - TFR2

    # Générer les indices des machines
    machines = np.arange(m)  # Indices des machines
    bar_width = 0.35  # Largeur des barres
    fig, ax = plt.subplots(figsize=(12, 7))

    # Tracer les barres pour TFR1 et TFR2 avec TAR1 et TAR2 si applicable
    if S is not None and all(item is not None for item in S):  # Cas avec TFR2 et TAR2
        bars1 = ax.bar(machines - bar_width / 2, TFR1, width=bar_width, label='TFR1', color='purple', alpha=0.7)
        bars2 = ax.bar(machines + bar_width / 2, TFR2, width=bar_width, label='TFR2', color='blue', alpha=0.7)
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 1, f'{height:.1f}%', ha='center', va='bottom',
                    fontsize=10)

    else:  # Cas uniquement TFR1
        bars1 = ax.bar(machines, TFR1, width=bar_width, label='TFR1', color='purple', alpha=0.7)
    # Ajouter les pourcentages au-dessus des barres pour TFR1
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=10)


    # Personnalisation du graphique
    ax.set_xlabel('Machines')
    ax.set_ylabel('TFR (%)')
    ax.set_title('TFR')
    ax.set_xticks(machines)
    ax.set_xticklabels([f'Machine {i + 1}' for i in range(m)])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Affichage dans une nouvelle fenêtre Tkinter
    new_window = tk.Toplevel(root)  # Créer une nouvelle fenêtre
    new_window.title("Diagramme de TFR et TAR")  # Définir le titre de la fenêtre
    new_window.geometry("1000x700")  # Définir la taille de la fenêtre

    # Canvas pour afficher le graphique
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Afficher le canevas dans la nouvelle fenêtre

# Assurez-vous d'avoir un objet `root` Tkinter existant pour que ce code fonctionne


def afficher_gantt():
    global method_selected1,method_selected2,method_selected3
    if 'fig' not in globals():
        tk.messagebox.showinfo("Erreur", "manque de données")
        return

    # Récupérer les choix de séquence et des contraintes
    c = choix_sequence.get()
    choix_Contraintes_1 = selection1.get()  # Valeur de sélection dans le premier menu déroulant
    choix_Contraintes_2 = selection2.get()  # Valeur de sélection dans le deuxième menu déroulant
    choix_Contraintes_3=selection3.get()
    valeur_optim1=v0
    valeur_optim2=v1
    if method_selected1:
        cc=choix_Contraintes_1

    if method_selected2:
        v=valeur_optim1.get()
        cc=choix_Contraintes_2
    if method_selected3:
        v=valeur_optim2.get()
        cc=choix_Contraintes_3
    global k
    # Créer un titre dynamique pour la fenêtre
    if method_selected1:
        titre = f"Diagramme de Gantt de la séquence '{c}'"
        if c=="CDS":
            titre += f" pour k ={k}"
    elif method_selected2:
        titre = f"Diagramme de Gantt de la séquence '{v}'"
    elif method_selected3:
        titre = f"Diagramme de Gantt de la séquence '{v}'"

    # Ajouter les contraintes au titre si elles sont activées
    if cc == "no idle":
        titre += " avec contrainte de non-idle"
    elif cc == "no wait":
        titre += " avec contrainte de non-attente"
    elif cc=="blocking":
        titre += " avec contrainte de blocking"
    elif cc=="sans contraintes":
        titre += " sans contraintes"
    elif cc=="temps de préparation":
        titre += " avec temps de préparation"

    # Créer une nouvelle fenêtre (Toplevel)
    new_window = tk.Toplevel(root)  # Créer une nouvelle fenêtre
    new_window.title(titre)  # Définir le titre dynamique de la fenêtre
    new_window.geometry("1000x700")  # Définir la taille de la nouvelle fenêtre

    # Canvas pour afficher le diagramme de Gantt dans la nouvelle fenêtre
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Afficher le canevas dans la nouvelle fenêtre


def executer_actions():
    if method_selected1 :
        Ordonancer_flowshop()
        afficher_gantt()
    elif method_selected2 or method_selected3 :
        Ordonancer_ME_MA()
        afficher_gantt()



def show_page(page):
    pages = [acceuil, instructions,choix_job,hybride1, excel_FS,methodes_flowshop,OP_flowshop,FS_exacte,FS_app,methodes_JS,OP_JS,exacte_JS,Jackson_JS,page_FH1,page_FH2,excel_FH,page_MP]
    for p in (pages):
        p.pack_forget()
    page.pack(fill="both", expand=True)

def on_button_click1():
    global method_selected1,method_selected2,method_selected3
    method_selected1 = True
    method_selected2=False
    method_selected3=False
    print("Méthode OP sélectionnée")
def on_button_click2():
    global method_selected2,method_selected3,method_selected1
    method_selected2 = True
    method_selected3=False
    method_selected1=False
    print("Méthode exacte sélectionnée")
def on_button_click3():
    global method_selected3,method_selected2,method_selected1
    method_selected3 = True
    method_selected1=False
    method_selected2=False
    print("Méthode Approchée sélectionnée")
def boutton_methode1():
   on_button_click1()
   show_page(OP_flowshop)

def boutton_methode2():
    on_button_click2()
    show_page(FS_exacte)
def boutton_methode3():
    on_button_click3()
    show_page(FS_app)

def créer_boutons_communs(parent):
    # Définir une variable pour suivre la sélection
    choix_contraintes = ctk.StringVar(value="contraintes")

    # Liste des valeurs possibles
    contraintes = ["no wait", "no idle", "blocking", "sans contraintes", "temps de préparation"]

    def on_contraintes_change(choice):
        # Supposons que `global_data` soit défini globalement
        try:
            processing_times, S, D, W, release_dates = global_data
        except NameError:
            messagebox.showerror("Erreur", "Les données globales (global_data) ne sont pas définies.")
            return

        if S is not None and all(item is not None for item in S):
            if choice in ["no wait", "no idle", "blocking"]:
                messagebox.showerror(
                    "Erreur de contrainte",
                    "Le fichier Excel contient 'S'. Les contraintes 'no wait', 'no idle', et 'blocking' ne sont pas permises."
                )
                # Réinitialiser la sélection
                choix_contraintes.set("temps de préparation")
                dropdown_contraintes.set("temps de préparation")  # Mettre à jour le menu déroulant visuellement

    # Créer le menu déroulant
    dropdown_contraintes = ctk.CTkOptionMenu(
        parent,
        variable=choix_contraintes,
        values=contraintes,
        width=250,
        corner_radius=10,
        command=on_contraintes_change  # Appeler la fonction lorsqu'un choix est effectué
    )

    # Positionner le menu déroulant
    dropdown_contraintes.pack(pady=40)

    # Bouton pour afficher le diagramme de Gantt
    button_display_gantt = ctk.CTkButton(
        parent, text="Afficher le diagramme de Gantt",
        command=executer_actions,
        width=250,
        corner_radius=10
    )
    button_display_gantt.pack(pady=40)

    # Bouton pour calculer le TFT
    button_display_tft = ctk.CTkButton(
        parent, text="Calcul de TFR",
        command=calcul,
        width=250,
        corner_radius=10
    )
    button_display_tft.pack(pady=40)

    return choix_contraintes

def créer_bouttons_communs_ME_MA(parent):
    choix_VO = ctk.StringVar(value="valeur à optimiser")
    global method_selected3,method_selected2
    if method_selected2:VO = ["Cmax", "TFT", "TT"]
    else:VO = ["Cmax", "TFT"]

    dropdown_VO = ctk.CTkOptionMenu(
        parent,
        variable=choix_VO,
        values=VO,
        width=250,
        corner_radius=10

    )
    dropdown_VO.pack(pady=40)
    return choix_VO



k=None
# Initialize the root window
root = ctk.CTk()
root.resizable(False, False)
# Function to keep the file loading safe
root.title("Application d'Ordonnancement")
root.geometry("900x500")

root.configure()
acceuil = ctk.CTkFrame(root)
# Ajouter un Label avec l'image en arrière-plan
bg_lbl = ctk.CTkLabel(acceuil, text="")
bg_lbl.place(x=0,y=0)

try:
    logo_image =  Image.open("AP/logoENsam.png")
    logo_image = logo_image.resize((200, 100))  # Resize the image
    logo_tk = ImageTk.PhotoImage(logo_image)
    logo_label = ctk.CTkLabel(acceuil, image=logo_tk, text="")
    logo_label.image = logo_tk  # Keep a reference to prevent garbage collection
    logo_label.place(x=360, y=20)  # Place logo at the top center
except FileNotFoundError:
    print("Logo introuvable ! Assurez-vous que 'ensam_logo.png' est dans le bon dossier.")

# Define font style
font_large = ("Helvetica", 16, "bold")
font_medium = ("Roboto", 14)
txt="Bienvenue dans l'application d'ordonnancement !"
count=0
text=""
label_welcome = ctk.CTkLabel(
    acceuil,
    text="Bienvenue dans l'application d'ordonnancement !",
    font=font_large,
    text_color="white",
    corner_radius=10
)
label_welcome.place(x=250, y=200)  # Position initiale en dehors de l'écran
button_commencer = ctk.CTkButton(acceuil, text="commencer", command=lambda: show_page(instructions), fg_color=ACCENT_COLOR)
button_commencer.place(x=370,y=250)

def slider():
    global count,text
    if count>=len(txt):
        count=-1
        text=""
        label_welcome.configure(text=text)
    else:
        text=text+txt[count]
        label_welcome.configure(text=text)
    count+=1
    label_welcome.after(100,slider)
slider()
label_credits_acceuil = ctk.CTkLabel(
    acceuil,
    text="Réalisé par :",
    font=("Arial", 8),
    text_color="black",
)
# Page 2 : Instructions
instructions = ctk.CTkFrame(root)

label_title = ctk.CTkLabel(
    instructions,
    text="Instructions",
    font=("Arial", 24, "bold"),
    text_color="#286F71"
)
label_title.pack(pady=40)

label_instructions = ctk.CTkLabel(
    instructions,
    text=(
        "Bienvenue dans l'application !\n\n"
        "1. Veuillez lire attentivement les instructions concernant le remplissage des fichiers Excel disponibles dans le dossier avant de les importer..\n"
        "2. Naviguez entre les pages avec les boutons Suivant ou Précédent.\n"
        "3. Sélectionnez le type d'atelier et configurez les paramètres.\n\n"
        "Appuyez sur Suivant pour continuer."
    ),
    font=("Arial", 16),
    wraplength=600,  # Limite la largeur du texte
    justify="left"
)
label_instructions.pack(pady=40)

button_next = ctk.CTkButton(
    instructions,
    text="Suivant",
    command=lambda: show_page(choix_job),  # S'assurer que `choix_job` existe
    fg_color="#286F71",
    text_color="white",
    corner_radius=10
)
button_next.pack(pady=40)










def go_to_next_page(parent,page):
    """
    Change la page actuelle pour la page suivante.
    """
    parent.pack(fill="both", expand=True)
    show_page(page)


# Création de la page de choix de job
choix_job = ctk.CTkFrame(root)

# Création des pages spécifiques
excel_FS = ctk.CTkFrame(root)



excel_FH = ctk.CTkFrame(root)

button_excel = None
button_excel = ctk.CTkButton(
    excel_FS,
    text="Sélectionner le fichier Excel",
    command=charger_fichier_excel,
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel.pack(pady=40)
# Ajout des boutons dans chaque page
# Bouton pour passer à la page suivante
next_button = ctk.CTkButton(
    excel_FS,
    text="Next step",
    command=lambda: go_to_next_page(excel_FS,methodes_flowshop),
    fg_color=ACCENT_COLOR
)
next_button.pack(pady=40)
button_reset1 = ctk.CTkButton( excel_FS, text="rénitisaliser les données", command=reset_fichier, width=120,
                             corner_radius=20)
button_reset1.pack(pady=40)  # Aligner à gauche avec un petit espacement




button_excel2= ctk.CTkButton(
    excel_FH,
    text="Sélectionner le fichier Excel",
    command=charger_fichier_excel1,
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
next_button2 = ctk.CTkButton(
    excel_FH,
    text="Next step",
    command=lambda: go_to_next_page(excel_FH,hybride1),
    fg_color=ACCENT_COLOR
)
button_excel2.pack(pady=40)
next_button2.pack(pady=40)

button_reset2 = ctk.CTkButton( excel_FH, text="rénitisaliser les données", command=reset, width=120,
                             corner_radius=20)
button_reset2.pack(pady=40)  # Aligner à gauche avec un petit espacement

# Boutons sur la page de choix
button_flowshop = ctk.CTkButton(
    choix_job,
    text="Flowshop",
    command=lambda:show_page(excel_FS),
    fg_color=ACCENT_COLOR
)
button_flowshop.pack(pady=40)
button_jobshop = ctk.CTkButton(
    choix_job,
    text="Jobshop",
    command=lambda:show_page(methodes_JS),
    fg_color=ACCENT_COLOR
)
button_jobshop.pack(pady=40)
button_MP = ctk.CTkButton(
    choix_job,
    text="Machines parallèles",
    command=lambda:show_page(page_MP),
    fg_color=ACCENT_COLOR
)
button_MP.pack(pady=40)

button_FH = ctk.CTkButton(
    choix_job,
    text="Flowshop hybride",
    command=lambda:show_page(excel_FH),
    fg_color=ACCENT_COLOR
)
button_FH.pack(pady=40)






methodes_flowshop = ctk.CTkFrame(root)
button_ordre_priorite=ctk.CTkButton(methodes_flowshop, text="OP",command=boutton_methode1,width=250,corner_radius=10,fg_color=ACCENT_COLOR)
button_ordre_priorite.pack(pady=40)
button_methode_exacte=ctk.CTkButton(methodes_flowshop, text="méthode exacte", command=boutton_methode2, width=250,corner_radius=10,fg_color=ACCENT_COLOR)
button_methode_exacte.pack(pady=40)
buton_methode_approximative=ctk.CTkButton(methodes_flowshop, text="méthode appro", width=250,command=boutton_methode3,corner_radius=10,fg_color=ACCENT_COLOR)
buton_methode_approximative.pack(pady=40)
methodes_flowshop.pack(expand=True, anchor="center")
# Page 5 : ORDRE DE PRIORITe
OP_flowshop = ctk.CTkFrame(root)


choix_sequence = ctk.StringVar(value="Choissisez votre séquence")
sequences = ["LIFO", "FIFO", "LPT", "SPT", "WDD", "EDD","JHONSON","CDS"]

def on_sequence_change(choice):
    """
    Fonction appelée lorsqu'un choix d'algorithme d'ordonnancement est modifié.

    :param choice: Le choix de l'utilisateur parmi les algorithmes disponibles.
    """
    global k
    try:
        # Extraction des données globales
        processing_times, S, D, W, release_dates = global_data
        m, n = processing_times.shape  # Nombre de machines (m) et de tâches (n)

        # Vérification des contraintes pour chaque algorithme
        if choice == "JHONSON" and m > 2:
            tk.messagebox.showinfo("Erreur", "L'algorithme de Johnson est limité à 2 machines.")
            return
        if choice in ["FIFO", "LIFO"] and np.array_equal(release_dates, np.zeros(n)):
            tk.messagebox.showinfo("Erreur", "Dates d'arrivées non fournies.")
            return
        if choice in ["EDD", "WDD"] and D is None:
            tk.messagebox.showinfo("Erreur", "Délais non fournis.")
            return
        if choice == "WDD" and W is None:
            tk.messagebox.showinfo("Erreur", "Poids non fournis.")
            return
        if choice == "CDS":
            # Demander une valeur pour k
            k = simpledialog.askinteger("Saisie de k", "Entrez la valeur de k :", minvalue=1, maxvalue=m-1)
            if k is None:
                tk.messagebox.showinfo("Erreur", "Vous devez saisir une valeur pour k.")
                return
            print(f"Valeur de k saisie : {k}")
    except Exception as e:
        tk.messagebox.showinfo("Erreur", f"Problème avec les données globales : {str(e)}")




dropdown_sequence = ctk.CTkOptionMenu(
    OP_flowshop,
    variable=choix_sequence,
    values=sequences,
    command=on_sequence_change,
    width=250,
    corner_radius = 10


)
dropdown_sequence.pack(pady=40)
selection1=créer_boutons_communs(OP_flowshop)
# Page 6 : Sélection d'approche de méthode
FS_exacte=ctk.CTkFrame(root)

v0=créer_bouttons_communs_ME_MA(FS_exacte)
selection2=créer_boutons_communs(FS_exacte)
FS_app=ctk.CTkFrame(root)

v1=créer_bouttons_communs_ME_MA(FS_app)
selection3=créer_boutons_communs(FS_app)
is_milp=False

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import customtkinter as ctk
import numpy as np

hybride1=ctk.CTkFrame(root)
button_OP_FH= ctk.CTkButton(
    hybride1,
    text="OP",
    command=lambda: show_page(page_FH1),  # S'assurer que `excel_FS` existe
    fg_color=ACCENT_COLOR
)
button_OP_FH.place(x=350, y=200)

button_MILP_FH = ctk.CTkButton(
    hybride1,
    text="MILP",
    command=lambda:show_page(page_FH2),  # S'assurer que `excel_FS` existe
    fg_color=ACCENT_COLOR
)
button_MILP_FH.place(x=350, y=300)

page_FH1 = ctk.CTkFrame(root)

choix_sequence2 = ctk.StringVar(value="Choisissez votre séquence")
sequences2 = ["LIFO", "FIFO", "LPT", "SPT", "WDD", "EDD"]




# Fonction pour gérer le changement de séquence
def on_sequence_change2(choice):
    try:
        # Extraction des données globales
        n,jobs, stages, machines_per_stage, release_times, due_dates, weights = global_data6

        if choice in ["EDD", "WDD"] and due_dates is None:
            tk.messagebox.showinfo("Erreur", "Délais non fournis.")
            return
        if choice == "WDD" and weights is None:
            tk.messagebox.showinfo("Erreur", "Poids non fournis.")
            return

    except Exception as e:
        tk.messagebox.showinfo("Erreur", f"Problème avec les données globales : {str(e)}")

# Bouton pour charger le fichier Excel


# Option menu pour choisir la séquence
dropdown_sequence2 = ctk.CTkOptionMenu(
    page_FH1,
    variable=choix_sequence2,
    values=sequences2,
    command=on_sequence_change2,
    width=250,
    corner_radius=10
)
dropdown_sequence2.pack(pady=40)
# Fonction pour exécuter l'ordonnancement flowshop hybride
def flowshop_hybride():
    global global_data6

    # Vérifiez si les données sont chargées
    if global_data6 is None:
        messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel.")
        return

    n,jobs, stages, machines_per_stage, release_times, due_dates, weights = global_data6
    sort_criterion = choix_sequence2.get()

    try:
        # Sélectionner la fonction de tri appropriée
        sort_functions = {
            'LPT': sort_jobs_lpt,
            'SPT': sort_jobs_spt,
            'EDD': sort_jobs_edd,
            'WDD': sort_jobs_wdd,
            'FIFO': sort_jobs_fifo,
            'LIFO': sort_jobs_lifo
        }

        sort_func = sort_functions.get(sort_criterion)
        if not sort_func:
            raise ValueError(f"Critère de tri non valide: {sort_criterion}")

        # Trier les jobs selon le critère choisi
        if sort_criterion in ['EDD', 'WDD']:
            if due_dates is None:
                raise ValueError("Les dates d'échéance sont requises pour EDD et WDD")
            if sort_criterion == 'WDD' and weights is None:
                raise ValueError("Les poids sont requis pour WDD")
            sorted_jobs = sort_func(jobs, release_times, due_dates) if sort_criterion == 'EDD' else sort_func(jobs,
                                                                                                              release_times,
                                                                                                              due_dates,
                                                                                                              weights)
        else:
            sorted_jobs = sort_func(jobs, release_times)

        # Initialiser les temps de fin pour chaque job à chaque étage
        completion_times = np.zeros((len(jobs), stages))

        # Initialiser les temps de disponibilité des machines à chaque étage
        machine_available_times = [np.zeros(m) for m in machines_per_stage]

        # Ordonnancement
        schedule = [[] for _ in range(stages)]

        # Pour chaque job
        for job_index, job in sorted_jobs:
            # Pour chaque étage
            for stage in range(stages):
                # Trouver la machine disponible le plus tôt
                machine = np.argmin(machine_available_times[stage])

                # Calculer le temps de début en tenant compte du release time
                if stage == 0:
                    start_time = max(release_times[job_index], machine_available_times[stage][machine])
                else:
                    start_time = max(completion_times[job_index][stage - 1],
                                     machine_available_times[stage][machine])

                # Calculer le temps de fin
                end_time = start_time + job[stage]

                # Mettre à jour les temps
                completion_times[job_index][stage] = end_time
                machine_available_times[stage][machine] = end_time

                # Ajouter à l'ordonnancement
                schedule[stage].append((job_index, machine, start_time, end_time))

        # Calculer le makespan
        makespan = max(completion_times[:, -1])
        fig = plot_gantt_FH(schedule, makespan)
        gantt_window = ctk.CTkToplevel(root)
        gantt_window.title("Diagramme de Gantt")
        gantt_window.geometry("1000x700")
        gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
        gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

        canvas = FigureCanvasTkAgg(fig, gantt_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Bouton pour afficher le diagramme de Gantt
button_display_gantt_FH = ctk.CTkButton(page_FH1, text="Afficher le diagramme de Gantt", command=flowshop_hybride,
                                         width=250, corner_radius=10)
button_display_gantt_FH.pack(pady=40)

page_FH2 = ctk.CTkFrame(root)

choix_CR = ctk.StringVar(value="Choisissez votre critère")
CR = ["Cmax","TFT","TT"]
dropdown_CR = ctk.CTkOptionMenu(
    page_FH2,
    variable=choix_CR,
    values=CR,
    width=250,
    corner_radius=10
)
dropdown_CR.pack(pady=40)
from pulp import PULP_CBC_CMD, LpStatus
from tkinter import messagebox
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def solve_hybrid_flowshop():
    """
    Résout le problème du flowshop hybride
    """
    global global_data6

    # Vérifiez si les données sont chargées
    if global_data6 is None or len(global_data6) != 7:
        messagebox.showerror("Erreur", "Veuillez d'abord charger un fichier Excel valide.")
        return

    n, p, E, m, release_times, due_dates, weights = global_data6
    critere = choix_CR.get()
    # Calcul de Q (Big-M)
    Q = sum(sum(p_i) for p_i in p) * n * 2  # Multiplié par 2 pour plus de sécurité

    try:
        # Création et résolution du modèle
        prob, X, Y, C, Cmax, TFT, TT = create_hybrid_flowshop_milp(n, E, m, p, Q, release_times, due_dates, critere)

        # Résolution avec un solveur plus robuste
        solver = PULP_CBC_CMD(msg=0, timeLimit=300)  # Limite de temps de 300 secondes
        prob.solve(solver)

        # Extraction des résultats
        if LpStatus[prob.status] == 'Optimal':
            sequence = {}
            schedule = {}
            for e in range(1, E + 1):
                sequence[e] = {}
                schedule[e] = {}
                machine_end_times = [0] * m[e - 1]  # Temps de fin pour chaque machine à l'étage e

                # Trier les jobs par leur temps de fin à cet étage
                jobs_at_stage = sorted([(k, value(C[k, e])) for k in range(1, n + 1)], key=lambda x: x[1])

                for k, end_time in jobs_at_stage:
                    # Trouver la machine disponible la plus tôt
                    machine = min(range(m[e - 1]), key=lambda i: machine_end_times[i])

                    if e == 1:
                        start_time = machine_end_times[machine]
                    else:
                        start_time = max(machine_end_times[machine], value(C[k, e - 1]))

                    machine_end_times[machine] = end_time

                    if machine + 1 not in sequence[e]:
                        sequence[e][machine + 1] = []
                        schedule[e][machine + 1] = []

                    sequence[e][machine + 1].append(k)
                    schedule[e][machine + 1].append({
                        'job': k,
                        'machine': machine + 1,  # Corriger le +1 ici
                        'start': start_time,
                        'end': end_time
                    })

            # Création du diagramme de Gantt
            print(global_data6)
            print(schedule)
            fig = plot_gantt_FH_MILP(schedule, value(Cmax),value(TFT))
            gantt_window = ctk.CTkToplevel(root)
            gantt_window.title("Diagramme de Gantt")
            gantt_window.geometry("1000x700")
            gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
            gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

            canvas = FigureCanvasTkAgg(fig, gantt_window)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()

        else:
            messagebox.showerror("Erreur", "La solution n'est pas optimale.")
            return

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")



button_display_gantt_FH = ctk.CTkButton(page_FH2, text="Afficher le diagramme de Gantt", command=solve_hybrid_flowshop,
                                         width=250, corner_radius=10)
button_display_gantt_FH.pack(pady=40)




def charger_donnees_jackson():
    """Charge les matrices P, O, Arrivals et Deadlines depuis un fichier Excel."""
    file_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier Excel",
        filetypes=[("Fichiers Excel", "*.xlsx")]
    )
    if not file_path:  # Vérifier si un fichier a été sélectionné
        raise ValueError("Aucun fichier sélectionné.")

    try:
        P_df = pd.read_excel(file_path, sheet_name="P", header=None)
        O_df = pd.read_excel(file_path, sheet_name="O", header=None)
        P = P_df.to_numpy()
        O = O_df.to_numpy()
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement des feuilles 'P' ou 'O': {str(e)}")

    # Charger les feuilles optionnelles
    Arrivals, Deadlines = None, None
    try:
        Arrivals_df = pd.read_excel(file_path, sheet_name="Arrivals", header=None)
        Arrivals = Arrivals_df.to_numpy()
    except Exception:
        print("Feuille 'Arrivals' absente. Continuation sans cette feuille.")

    try:
        Deadlines_df = pd.read_excel(file_path, sheet_name="Deadlines", header=None)
        Deadlines = Deadlines_df.to_numpy()
    except Exception:
        print("Feuille 'Deadlines' absente. Continuation sans cette feuille.")

    return P, O, Arrivals, Deadlines




global donnees, label_status
donnees = None

def charger_et_afficher():

    global donnees
    fichier_excel = charger_donnees()
    if fichier_excel is not None:
        type_mach = type_machine.get()
        donnees = lire_feuilles(fichier_excel, type_mach)



def appliquer_et_tracer():
    if donnees is not None:
        regle = regle_var.get()
        type_mach = type_machine.get()
        jobs = preparer_donnees(donnees)
        print(jobs)

        if jobs is not None and not jobs.empty:
            print("Jobs avant application de la règle:", jobs.head())
            try:
                # Vérification préalable pour FIFO et LIFO
                if regle in ["FIFO", "LIFO"]:
                    if "Arrival" not in jobs.columns:
                        raise ValueError("La colonne 'Arrival' est manquante pour les règles FIFO/LIFO.")

                jobs = appliquer_regle(jobs, regle)
                print("Jobs triés selon la règle :", jobs.head())

                nb_machines = donnees.get("nb_machines")
                if nb_machines is None:
                    if type_mach == "Hétérogènes":
                        nb_machines = len(
                            [col for col in jobs.columns if col.startswith("Processing Time Machine")])
                    else:
                        nb_machines = 3
                print(f"Nombre de machines : {nb_machines}")

                if type_mach == "Homogènes":
                    machines = assigner_taches_homogenes(jobs, nb_machines=nb_machines)
                elif type_mach == "Uniformes":
                    speeds = donnees.get("speeds")
                    if speeds is None or speeds.empty:
                        raise ValueError("Les données des vitesses ('speeds') sont manquantes ou vides.")
                    print("Speeds :", speeds.head())
                    machines = assigner_taches_uniformes(jobs, speeds)
                elif type_mach == "Hétérogènes":
                    machines = assigner_taches_heterogenes(jobs)
                else:
                    raise ValueError("Type de machine non pris en charge.")

                # Si nous arrivons ici sans exception, nous pouvons tracer le diagramme de Gantt
                fig=tracer_gantt(machines, jobs)
                gantt_window = ctk.CTkToplevel(root)
                gantt_window.title("Diagramme de Gantt")
                gantt_window.geometry("1000x700")
                gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
                gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

                canvas = FigureCanvasTkAgg(fig, gantt_window)
                canvas.get_tk_widget().pack(fill="both", expand=True)
                canvas.draw()

                label_status.configure(text="Ordonnancement et tracé réussis.")
            except ValueError as e:
                error_message = str(e)
                print(f"Erreur : {error_message}")
            except Exception as e:
                error_message = f"Erreur inattendue lors de l'assignation des tâches : {e}"
                print(f"Erreur détaillée : {error_message}")
        else:
            label_status.configure(text="Les données des tâches sont manquantes ou vides.")
            print("Erreur : La feuille 'jobs' est vide ou manquante.")
    else:
        label_status.configure(text="Veuillez charger des données d'abord.")
        print("Erreur : Les données ne sont pas chargées.")

page_MP=ctk.CTkFrame(root)

type_machine = ctk.StringVar(value="Homogènes")
menu_type_machine = ctk.CTkOptionMenu(page_MP, variable=type_machine, values=["Homogènes", "Hétérogènes", "Uniformes"], width=250,
    corner_radius=10)
menu_type_machine.pack(pady=40)
bouton_charger = ctk.CTkButton(page_MP, text="séléctionnez fichier excel", command=charger_et_afficher,fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10)
bouton_charger.pack(pady=40)
    # Menu pour choisir la règle de priorité
regle_var = ctk.StringVar(value="SPT")


menu_regle = ctk.CTkOptionMenu(page_MP, variable=regle_var, values=["SPT", "LPT", "EDD", "WDD", "FIFO", "LIFO"], width=250,
    corner_radius=10)
menu_regle.pack(pady=40)

    # Bouton pour appliquer la règle et tracer le Gantt
bouton_appliquer = ctk.CTkButton(page_MP, text="Appliquer règle et tracer Gantt", command=appliquer_et_tracer, width=250,
    corner_radius=10)
bouton_appliquer.pack(pady=40)

def ordonnancement_job_shop(jobs, n, m, priorite, S):
    DEBUT = [[] for _ in range(m)]
    FIN = [[] for _ in range(m)]
    setup_times = [[] for _ in range(m)]
    machine_availability = np.zeros(m)  # Disponibilité des machines
    job_availability = np.zeros(n)  # Disponibilité des jobs
    last_job_on_machine = [-1] * m  # Dernier job exécuté sur chaque machine
    # Ordonnancer les premières opérations selon la règle choisie
    sequence_globale = appliquer_priorite(jobs,priorite)


    while any(len(job["operations"]) > 0 for job in sequence_globale):
        # Réorganiser les jobs selon la fin des opérations précédentes
        sequence_globale = sorted(
            sequence_globale,
            key=lambda job: job_availability[job["job_id"] - 1] if len(job["operations"]) > 0 else float('inf')
        )

        # Traitement des jobs dans la séquence triée
        for job in sequence_globale:
            job_id = job["job_id"] - 1  # Alignement des indices
            if len(job["operations"]) > 0:
                machine, duration = job["operations"].pop(0)  # Récupérer la prochaine opération
                machine_index = machine - 1  # Alignement des indices

                # Temps de préparation
                if last_job_on_machine[machine_index] == -1:
                    setup_time = S[machine_index][job_id, job_id]  # Diagonale
                else:
                    prev_job = last_job_on_machine[machine_index]
                    setup_time = S[machine_index][prev_job, job_id]

                # Calculer le début et la fin de l'opération (avec temps de préparation)
                release_date = job.get("arrival_time", 0)  # Par défaut, 0 si pas de date d'arrivée définie
                preparation_start = max(machine_availability[machine_index], job_availability[job_id] - setup_time,
                                        release_date- setup_time)
                preparation_end = preparation_start + setup_time
                operation_start = preparation_end
                operation_end = operation_start + duration

                # Ajouter les temps de début, fin et préparation dans les matrices
                DEBUT[machine_index].append((job_id, operation_start))
                FIN[machine_index].append((job_id, operation_end))
                setup_times[machine_index].append((job_id, preparation_start))

                # Mettre à jour les disponibilités
                machine_availability[machine_index] = operation_end
                job_availability[job_id] = operation_end

                # Mettre à jour le dernier job sur la machine
                last_job_on_machine[machine_index] = job_id

    return DEBUT, FIN, setup_times







def lancer_jobshop():

    jobs, m, n, _, S, has_arrivals, has_deadlines, has_weights, _ = charger_donnees_jobshop_2()
    priorite = priorite_var.get()
    if jobs is None:
        messagebox.showerror("Erreur", "Les données des jobs ne sont pas valides.")
        return

    if priorite in ["FIFO", "LIFO"] and not has_arrivals:
            messagebox.showerror("Erreur", "Les arrivées sont nécessaires pour cette priorité.")
            return
    if priorite == "WDD" and not has_weights:
            messagebox.showerror("Erreur", "Les poids sont nécessaires pour la priorité SPT.")
            return

    if priorite == "EDD" and not has_deadlines:
            messagebox.showerror("Erreur", "Les délais sont nécessaires pour la priorité EDD.")
            return
    try:
        DEBUT, FIN, setup_times = ordonnancement_job_shop(jobs, n, m, priorite, S)
        fig = generer_gantt_jobshop(DEBUT, FIN, jobs, m, setup_times)

        gantt_window = ctk.CTkToplevel(root)
        gantt_window.title("Diagramme de Gantt")
        gantt_window.geometry("1000x700")
        gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
        gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

        canvas = FigureCanvasTkAgg(fig, gantt_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()


    except Exception as e:
        messagebox.showerror("Erreur", str(e))


def lancer_jackson():
    """Lance l'algorithme de Jackson pour un problème à 2 machines."""
    try:
        # Charger les données
        P, O, Arrivals, Deadlines = charger_donnees_jobshop_2()

        # Vérifier que P et O sont valides
        if P is None or O is None:
            messagebox.showerror("Erreur", "Les matrices P et O sont nécessaires.")
            return


        # Vérifier que le problème concerne exactement 2 machines
        if O.shape[0] != 2:
            messagebox.showerror("Erreur", "Les données doivent correspondre à un problème à 2 machines.")
            return

        # Appliquer l'algorithme de Jackson
        Machine1seq, Machine2seq = appliquer_algorithme_jackson(P, O)

        # Générer le diagramme de Gantt
        fig=generer_gantt_jackson(P, Machine1seq, Machine2seq)
        gantt_window = ctk.CTkToplevel(root)
        gantt_window.title("Diagramme de Gantt")
        gantt_window.geometry("1000x700")
        gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
        gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

        canvas = FigureCanvasTkAgg(fig, gantt_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    except ValueError as ve:
        messagebox.showerror("Erreur de validation", str(ve))
    except Exception as e:
        messagebox.showerror("Erreur inattendue", str(e))

def lancer_jobshop_milp(selected_metric):
    PROC, MACH, PRESENCE, SETUP, Arrivals, deadlines,Weights = charger_donnees_jobshop_2()
    if PROC is None:
        messagebox.showerror("Erreur", "Les données des jobs ne sont pas valides.")
        return
    try:
        if SETUP is not None and all(item is not None for item in SETUP):
            job_operations,objective=solve_jobshop_prepa(PROC, MACH, PRESENCE, SETUP, Arrivals, deadlines,selected_metric)

        else:job_operations,objective=solve_jobshop_flexible(PROC, MACH, PRESENCE, Arrivals, deadlines, selected_metric)
        fig=generer_gantt_Jobshop_MILP(job_operations, PROC, MACH, SETUP,deadlines)

        gantt_window = ctk.CTkToplevel(root)
        gantt_window.title("Diagramme de Gantt")
        gantt_window.geometry("1000x700")
        gantt_window.attributes("-topmost", True)  # Force la fenêtre au premier plan
        gantt_window.after(100, lambda: gantt_window.attributes("-topmost", False))  # Désactive après 100ms

        canvas = FigureCanvasTkAgg(fig, gantt_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

method_selected4 = False
method_selected5 = False
method_selected6= False

def on_button_click4():
    global method_selected4,method_selected5,method_selected6,data_jack,data_ex
    method_selected4 = True
    method_selected5 = False
    method_selected6 = False
    data_jack=None
    data_ex=None

    print("Méthode OP sélectionnée")
def boutton_methode4():
   on_button_click4()
   show_page(OP_JS)
def on_button_click5():
    global method_selected5,method_selected4,method_selected6,data_OP,data_ex
    method_selected5 = True
    method_selected6 = False
    method_selected4 = False
    data_OP=None
    data_ex=None

    print("Méthode JACKSON sélectionnée")
def boutton_methode5():
   on_button_click5()
   show_page(Jackson_JS)
def on_button_click6():
    global method_selected6,method_selected4,method_selected5,data_OP,data_jack
    method_selected6 = True
    method_selected4 = False
    method_selected5 = False
    data_OP=None
    data_jack=None
    print("Méthode MILP sélectionnée")
def boutton_methode6():
   on_button_click6()
   show_page(exacte_JS)


 # Met à jour le texte du label avec le chemin

methodes_JS= ctk.CTkFrame(root)
button_ordre_priorite=ctk.CTkButton(methodes_JS, text="OP",command=boutton_methode4,width=250,corner_radius=10,fg_color=ACCENT_COLOR)
button_ordre_priorite.pack(pady=40)
buton_methode_Jackson=ctk.CTkButton(methodes_JS, text="méthode JACKSON", width=250,command=boutton_methode5,corner_radius=10,fg_color=ACCENT_COLOR)
buton_methode_Jackson.pack(pady=40)
button_methode_exacte=ctk.CTkButton(methodes_JS, text="méthode exacte", command=boutton_methode6, width=250,corner_radius=10,fg_color=ACCENT_COLOR)
button_methode_exacte.pack(pady=40)

OP_JS= ctk.CTkFrame(root)

button_excel1 = ctk.CTkButton(
    OP_JS,
    text="Sélectionner le fichier Excel",
    command=charger_donnees_jobshop_2,
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel1.pack(pady=20)

label_priorite = ctk.CTkLabel(OP_JS, text="Choisissez une priorité :", font=("Arial", 12))
priorite_var = ctk.StringVar(value="SPT")
menu_priorite = ctk.CTkOptionMenu(OP_JS, variable=priorite_var, values=["SPT", "LPT", "FIFO", "LIFO", "EDD", "WDD"])
button_display_gantt = ctk.CTkButton(OP_JS, text="Afficher le diagramme de Gantt", command=lancer_jobshop,
                                         width=250, corner_radius=10)

button_reset1 = ctk.CTkButton(OP_JS, text="rénitisaliser les données", command=reset_fichier2, width=120,
                             corner_radius=20)
  # Aligner à gauche avec un petit espacement
label_priorite.pack(pady=40)
menu_priorite.pack(pady=40)
button_display_gantt.pack(pady=40)
button_reset1.pack(pady=40)


Jackson_JS= ctk.CTkFrame(root)
button_excel_JACK = ctk.CTkButton(
    Jackson_JS,
    text="Sélectionner le fichier Excel",
    command=charger_donnees_jobshop_2,
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel_JACK.pack(pady=40)
button_display_gantt = ctk.CTkButton(Jackson_JS, text="Afficher le diagramme de Gantt", command=lancer_jackson,
                                         width=250, corner_radius=10)
button_display_gantt.pack(pady=40)
button_reset1 = ctk.CTkButton(Jackson_JS, text="rénitisaliser les données", command=reset_fichier2, width=120,
                             corner_radius=20)
button_reset1.pack(pady=40)


exacte_JS= ctk.CTkFrame(root)
button_excel_ex = ctk.CTkButton(
    exacte_JS,
    text="Sélectionner le fichier Excel",
    command=charger_donnees_jobshop_2,
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel_ex.pack(pady=40)
metric_var = ctk.StringVar(value="Cmax")
metric_menu = ctk.CTkOptionMenu(exacte_JS, variable=metric_var, values=["Cmax", "TT"])
metric_menu.pack(pady=40)
button_display_gantt = ctk.CTkButton(exacte_JS, text="Afficher le diagramme de Gantt", command=lambda :lancer_jobshop_milp(metric_var.get()),
                                         width=250, corner_radius=10)
button_display_gantt.pack(pady=40)
button_reset1 = ctk.CTkButton(exacte_JS, text="rénitisaliser les données", command=reset_fichier2, width=120,
                             corner_radius=20)
button_reset1.pack(pady=40)



pages = [acceuil, instructions, choix_job, hybride1, excel_FS, methodes_flowshop, OP_flowshop, FS_exacte, FS_app, methodes_JS, OP_JS, Jackson_JS, exacte_JS, page_FH2, page_FH1,excel_FH,page_MP]

for i, page in enumerate(pages):
    # Déterminer la page précédente en fonction de la page actuelle
    if page == acceuil:
        previous_page = None  # Pas de page précédente pour la première page
    elif page == methodes_flowshop:
        previous_page = excel_FS  # Page 4 (excel_FS) sera la précédente pour ces pages
    elif page in [excel_FS,methodes_JS,excel_FH,page_MP,]:
        previous_page=choix_job
    elif page in [page_FH2, page_FH1]:
        previous_page = hybride1  # La page précédente pour page_FH2 et page_FH1 est page 12 (page_FH2)
    elif page in [OP_JS, exacte_JS, Jackson_JS]:
        previous_page = methodes_JS  # Page 8 (FS_exacte) sera la précédente pour ces pages
    elif page in [OP_flowshop,FS_exacte,FS_app]:
        previous_page = methodes_flowshop
    elif page == hybride1:
        previous_page = excel_FH




    else:
        previous_page = pages[i - 1]  # Sinon, la page précédente est simplement l'index précédent dans la liste

    if previous_page:  # Ne pas ajouter de bouton "Previous" pour la première page
        # Utiliser une capture correcte de previous_page dans le lambda
        button_previous = ctk.CTkButton(
            page,
            text="<",
            command=lambda p=previous_page: show_page(p),  # Capturer `previous_page` à ce moment précis
            fg_color=SECONDARY_COLOR,
            width=20,
            corner_radius=0
        )
        button_previous.place(x=0, y=0)




show_page(acceuil)
# Start the application
root.mainloop()
