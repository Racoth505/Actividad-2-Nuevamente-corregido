# tab_view_grades_student.py
import tkinter as tk
from tkinter import messagebox, ttk
import db_manager

def create_view_grades_student_tab(parent, user_data):
    """
    Pestaña del Alumno para ver sus materias y calificaciones.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")
    student_id = user_data["id"]

    # --- Configuración Responsiva ---
    tab.rowconfigure(0, weight=1)
    tab.columnconfigure(0, weight=1, minsize=200) # Columna de materias
    tab.columnconfigure(1, weight=2) # Columna de calificaciones

    # --- Mapas ---
    subject_map = {} # "Nombre Materia" -> id

    # --- Columna Izquierda (Materias) ---
    subject_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    subject_frame.grid(row=0, column=0, sticky="nsew")
    subject_frame.rowconfigure(1, weight=1)
    subject_frame.columnconfigure(0, weight=1)

    ttk.Label(subject_frame, text="Mis Materias Inscritas", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    subject_listbox = tk.Listbox(subject_frame, font=("Helvetica", 11), borderwidth=0, height=6, exportselection=False)
    subject_listbox.grid(row=1, column=0, sticky="nsew")
    
    # --- Columna Derecha (Calificaciones) ---
    grades_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    grades_frame.grid(row=0, column=1, sticky="nsew")
    grades_frame.rowconfigure(1, weight=1)
    grades_frame.columnconfigure(0, weight=1)

    ttk.Label(grades_frame, text="Mis Calificaciones", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    
    grades_listbox = tk.Listbox(grades_frame, font=("Helvetica", 11), borderwidth=0)
    grades_listbox.grid(row=1, column=0, sticky="nsew")

    # --- Label de Promedio ---
    lbl_avg_text = tk.StringVar(value="Promedio Ponderado: N/A")
    ttk.Label(grades_frame, textvariable=lbl_avg_text, font=("Helvetica", 12, "bold")).grid(row=2, column=0, pady=10, sticky="e")

    # --- Lógica de la Pestaña ---

    def refresh_subjects():
        subject_listbox.delete(0, tk.END)
        subject_map.clear()
        subjects = db_manager.get_subjects_by_student(student_id)
        for subj in subjects:
            subject_listbox.insert(tk.END, subj["nombre"])
            subject_map[subj["nombre"]] = subj["id"]
        # Limpiar listas dependientes
        grades_listbox.delete(0, tk.END)
        lbl_avg_text.set("Promedio Ponderado: N/A")

    def on_subject_select(event):
        selection = subject_listbox.curselection()
        if not selection: return
        
        subject_name = subject_listbox.get(selection[0])
        subject_id = subject_map.get(subject_name)
        
        refresh_activities(subject_id)

    subject_listbox.bind("<<ListboxSelect>>", on_subject_select)

    def refresh_activities(subject_id):
        grades_listbox.delete(0, tk.END)
        
        activities = db_manager.get_activities_by_student_subject(student_id, subject_id)
        
        for act in activities:
            display_text = f"{act['descripcion']} | Cal: {act['calificacion']} | Peso: {act['peso']}"
            grades_listbox.insert(tk.END, display_text)
        
        # Calcular promedio ponderado
        avg = db_manager.get_weighted_average(student_id, subject_id)
        lbl_avg_text.set(f"Promedio Ponderado: {avg}")

    # Carga inicial
    refresh_subjects()
    return tab