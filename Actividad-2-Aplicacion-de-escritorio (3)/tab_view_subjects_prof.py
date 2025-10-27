# tab_view_subjects_prof.py
import tkinter as tk
from tkinter import ttk
import db_manager

def create_view_subjects_prof_tab(parent, user_data):
    """
    Pestaña del Profesor para ver las materias que tiene asignadas.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")
    profesor_id = user_data["id"]

    # --- Configuración Responsiva ---
    tab.rowconfigure(1, weight=1)
    tab.columnconfigure(0, weight=1)
    
    list_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    list_frame.grid(row=1, column=0, sticky="nsew")
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)
    
    ttk.Label(tab, text="Mis Materias Asignadas", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=10)

    listbox = tk.Listbox(list_frame, font=("Helvetica", 11), borderwidth=0)
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    def refresh_list():
        listbox.delete(0, tk.END)
        subjects = db_manager.get_subjects_by_professor(profesor_id)
        for subject in subjects:
            listbox.insert(tk.END, subject["nombre"])

    btn_refresh = ttk.Button(tab, text="Actualizar Lista", command=refresh_list)
    btn_refresh.grid(row=2, column=0, pady=10)

    refresh_list()
    return tab