import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import matplotlib.cm as cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import simpledialog
import customtkinter as ctk

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
def charger_donnees_jobshop_2():
    """Charger les données Excel et mettre à jour les variables globales.

    Cette fonction charge les données nécessaires pour les différents scénarios d'ordonnancement
    (Jobshop, Jackson, ou avec setup) en fonction de la méthode sélectionnée.

    :return: Les données chargées en fonction de la méthode sélectionnée.
    """
    global global_data5,data_OP,data_jack,data_ex, method_selected4, method_selected5, method_selected6

    # Vérifier si les données sont déjà chargées
    if global_data5 is not None:
        print("Les données sont déjà chargées depuis le fichier.")
        return global_data5

    # Méthode Jobshop
    if method_selected4:
        jobs, max_machine, n, T, S, has_arrivals, has_deadlines, has_weights, file_path = charger_donnees_jobshop()

        data_OP = jobs, max_machine, n, T, S, has_arrivals, has_deadlines, has_weights, file_path
        return data_OP
    # Méthode Jackson
    if method_selected5:
        P, O, Arrivals, Deadlines = charger_donnees_jackson()
        data_jack = P, O, Arrivals, Deadlines
        return data_jack

    # Méthode avec setup et autres paramètres
    if method_selected6:
        PROC, MACH, PRESENCE, SETUP, Arrivals, Deadlines, Weights = load_data_from_excel()
        if PROC is None or PROC.size == 0:
            raise ValueError("Les données des jobs sont invalides pour la méthode sélectionnée (method_selected6).")

        # Remplir les valeurs manquantes pour Arrivals et Deadlines si nécessaire
        Arrivals = np.zeros(PROC.shape[0]) if Arrivals is None else Arrivals
        Deadlines = np.zeros(PROC.shape[0]) if Deadlines is None else Deadlines

        data_ex = PROC, MACH, PRESENCE, SETUP, Arrivals, Deadlines, Weights
        return data_ex

    # Si aucune méthode valide n'est sélectionnée
    raise ValueError("Aucune méthode valide n'a été sélectionnée pour charger les données.")


import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np

# Couleur d'accent
ACCENT_COLOR = "#3B82F6"

# Initialisation de la fenêtre principale
root = ctk.CTk()
root.title("Tester les scénarios d'ordonnancement")
root.geometry("800x600")

# Variables globales
method_selected4 = False
method_selected5 = False
method_selected6 = False
global_data5 = None

# Fonctions de navigation
current_frame = None
def show_page(frame):
    global current_frame
    if current_frame is not None:
        current_frame.pack_forget()
    current_frame = frame
    frame.pack(fill="both", expand=True)

# Fonctions des boutons de méthodes
def on_button_click4():
    global method_selected4
    method_selected4 = True
    print("Méthode OP sélectionnée")

def boutton_methode4():
    on_button_click4()
    show_page(OP_JS)

def on_button_click5():
    global method_selected5
    method_selected5 = True
    print("Méthode JACKSON sélectionnée")

def boutton_methode5():
    on_button_click5()
    show_page(Jackson_JS)

def on_button_click6():
    global method_selected6
    method_selected6 = True
    print("Méthode MILP sélectionnée")

def boutton_methode6():
    on_button_click6()
    show_page(exacte_JS)

# Fonctions principales
# (Les fonctions charger_donnees_jobshop, charger_donnees_jackson, etc. doivent être définies avant l'utilisation)
def reset_fichier2():
    global global_data5
    global_data5 = None
    messagebox.showinfo("Réinitialisation", "Les données ont été réinitialisées.")

def lancer_jobshop():
    messagebox.showinfo("Exécution", "Lancement du Jobshop en cours...")

def lancer_jackson():
    messagebox.showinfo("Exécution", "Lancement du Jackson en cours...")

def lancer_jobshop_milp(metric):
    messagebox.showinfo("Exécution", f"Lancement du Jobshop MILP avec la métrique {metric}...")

# Pages de l'interface
OP_JS = ctk.CTkFrame(root)
button_excel1 = ctk.CTkButton(
    OP_JS,
    text="Sélectionner le fichier Excel",
    command=lambda: charger_donnees_jobshop_2(),
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel1.pack(pady=20)

label_priorite = ctk.CTkLabel(OP_JS, text="Choisissez une priorité :", font=("Arial", 12))
priorite_var = ctk.StringVar(value="SPT")
menu_priorite = ctk.CTkOptionMenu(OP_JS, variable=priorite_var, values=["SPT", "LPT", "FIFO", "LIFO", "EDD", "WDD"])

button_display_gantt = ctk.CTkButton(
    OP_JS, text="Afficher le diagramme de Gantt", command=lancer_jobshop,
    width=250, corner_radius=10
)

button_reset1 = ctk.CTkButton(OP_JS, text="Réinitialiser les données", command=reset_fichier2, width=120,
                             corner_radius=20)

label_priorite.pack(pady=20)
menu_priorite.pack(pady=20)
button_display_gantt.pack(pady=20)
button_reset1.pack(pady=20)

Jackson_JS = ctk.CTkFrame(root)
button_excel_JACK = ctk.CTkButton(
    Jackson_JS,
    text="Sélectionner le fichier Excel",
    command=lambda: charger_donnees_jobshop_2(),
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel_JACK.pack(pady=20)

button_display_gantt_JACK = ctk.CTkButton(Jackson_JS, text="Afficher le diagramme de Gantt", command=lancer_jackson,
                                         width=250, corner_radius=10)
button_display_gantt_JACK.pack(pady=20)

button_reset2 = ctk.CTkButton(Jackson_JS, text="Réinitialiser les données", command=reset_fichier2, width=120,
                             corner_radius=20)
button_reset2.pack(pady=20)

exacte_JS = ctk.CTkFrame(root)
button_excel_ex = ctk.CTkButton(
    exacte_JS,
    text="Sélectionner le fichier Excel",
    command=lambda: charger_donnees_jobshop_2(),
    fg_color=ACCENT_COLOR,
    width=250,
    corner_radius=10
)
button_excel_ex.pack(pady=20)

metric_var = ctk.StringVar(value="Cmax")
metric_menu = ctk.CTkOptionMenu(exacte_JS, variable=metric_var, values=["Cmax", "TT"])
metric_menu.pack(pady=40)

button_display_gantt_MILP = ctk.CTkButton(
    exacte_JS, text="Afficher le diagramme de Gantt", command=lambda: lancer_jobshop_milp(metric_var.get()),
    width=250, corner_radius=10
)
button_display_gantt_MILP.pack(pady=40)

button_reset3 = ctk.CTkButton(exacte_JS, text="Réinitialiser les données", command=reset_fichier2, width=120,
                             corner_radius=20)
button_reset3.pack(pady=20)

# Page d'accueil
Home = ctk.CTkFrame(root)
label_home = ctk.CTkLabel(Home, text="Bienvenue dans l'application d'ordonnancement", font=("Arial", 16))
label_home.pack(pady=20)

button_op = ctk.CTkButton(Home, text="Méthode OP", command=boutton_methode4, width=200, corner_radius=10)
button_op.pack(pady=10)

button_jackson = ctk.CTkButton(Home, text="Méthode Jackson", command=boutton_methode5, width=200, corner_radius=10)
button_jackson.pack(pady=10)

button_exacte = ctk.CTkButton(Home, text="Méthode MILP", command=boutton_methode6, width=200, corner_radius=10)
button_exacte.pack(pady=10)

# Afficher la page d'accueil
show_page(Home)

# Lancer l'application
root.mainloop()
