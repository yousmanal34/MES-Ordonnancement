import numpy as np


def sort_jobs_lpt(jobs, release_times):
    return sorted(enumerate(jobs), key=lambda x: (sum(x[1]), -release_times[x[0]]), reverse=True)


def sort_jobs_spt(jobs, release_times):
    return sorted(enumerate(jobs), key=lambda x: (sum(x[1]), release_times[x[0]]))


def sort_jobs_edd(jobs, release_times, due_dates):
    return sorted(enumerate(jobs), key=lambda x: (due_dates[x[0]], release_times[x[0]]))


def sort_jobs_wdd(jobs, release_times, due_dates, weights):
    return sorted(enumerate(jobs),
                  key=lambda x: ((due_dates[x[0]] - release_times[x[0]]) / weights[x[0]], release_times[x[0]]))


def sort_jobs_fifo(jobs, release_times):
    return sorted(enumerate(jobs), key=lambda x: release_times[x[0]])


def sort_jobs_lifo(jobs, release_times):
    return sorted(enumerate(jobs), key=lambda x: release_times[x[0]], reverse=True)

import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_gantt_FH(schedule, makespan):
    """
    Affiche un diagramme de Gantt avec séparation entre les étages, une ligne horizontale pour Cmax,
    et les temps de début et de fin pour chaque tâche à l'intérieur des barres.

    :param schedule: Ordonnancement des tâches.
    :param makespan: Durée totale (Cmax).
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    n = len(schedule)

    palette = sns.color_palette("twilight_shifted", n_colors=n)
    colors = np.array(palette)

    # Parcourir chaque étage
    for stage, stage_schedule in enumerate(schedule):
        for job, machine, start, end in stage_schedule:
            duration = end - start
            ax.barh(
                y=f"Étage {stage + 1} - Machine {machine + 1}",
                width=duration,
                left=start,
                color=colors[job % len(colors)],
                edgecolor="black",
                label=f"Job {job + 1}" if f"Job {job + 1}" not in ax.get_legend_handles_labels()[1] else None,
            )

            # Ajouter les temps de début et de fin à l'intérieur des barres
            ax.text(start + duration / 2, f"Étage {stage + 1} - Machine {machine + 1}",
                    f"J{job+1}\n{start}-{end}",
                    va='center', ha='center', fontsize=8, fontweight='bold',
                    color='white' if np.mean(colors[job % len(colors)]) < 0.5 else 'black')

    # Ajouter la ligne horizontale pour Cmax
    ax.axvline(makespan, color="red", linestyle="--", label=f"Cmax = {makespan}")

    # Configuration des axes
    ax.set_xlabel("Temps")
    ax.set_ylabel("Étages et Machines")
    ax.set_title("Diagramme de Gantt - Flowshop Hybride")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1))

    # Ajuster les limites de l'axe x pour avoir un peu d'espace pour les étiquettes
    ax.set_xlim(0, makespan)

    plt.tight_layout()
    return fig



