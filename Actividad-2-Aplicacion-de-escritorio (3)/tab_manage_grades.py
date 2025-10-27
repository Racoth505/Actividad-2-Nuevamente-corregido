# tab_manage_grades.py
import tkinter as tk
from tkinter import messagebox, ttk
import db_manager

def create_manage_grades_tab(parent, user_data):
    """
    Pestaña principal del Profesor para gestionar calificaciones.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")
    profesor_id = user_data["id"]

    # --- Configuración Responsiva (Sin cambios) ---
    tab.rowconfigure(0, weight=1)
    tab.columnconfigure(0, weight=1) 
    tab.columnconfigure(1, weight=2) 

    # --- Mapas (Sin cambios) ---
    subject_map = {} 
    student_map = {} 
    activity_map = {} 

    # --- Columna Izquierda (Selección) (Sin cambios) ---
    selection_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    selection_frame.grid(row=0, column=0, sticky="nsew")
    selection_frame.rowconfigure(1, weight=1)
    selection_frame.rowconfigure(3, weight=2)
    selection_frame.columnconfigure(0, weight=1)

    ttk.Label(selection_frame, text="Mis Materias", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    subject_listbox = tk.Listbox(selection_frame, font=("Helvetica", 11), borderwidth=0, height=6, exportselection=False)
    subject_listbox.grid(row=1, column=0, sticky="nsew")

    ttk.Label(selection_frame, text="Alumnos Inscritos", font=("Helvetica", 12, "bold")).grid(row=2, column=0, pady=5, sticky="w")
    student_listbox = tk.Listbox(selection_frame, font=("Helvetica", 11), borderwidth=0, exportselection=False)
    student_listbox.grid(row=3, column=0, sticky="nsew")

    # --- Columna Derecha (Actividades y Edición) ---
    activity_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    activity_frame.grid(row=0, column=1, sticky="nsew")
    activity_frame.rowconfigure(1, weight=1)
    activity_frame.columnconfigure(0, weight=1)

    ttk.Label(activity_frame, text="Calificaciones del Alumno", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    
    activity_listbox = tk.Listbox(activity_frame, font=("Helvetica", 11), borderwidth=0)
    activity_listbox.grid(row=1, column=0, sticky="nsew")

    # --- Frame de Edición/Creación (MODIFICADO) ---
    edit_frame = ttk.Frame(activity_frame, style="Main.TFrame", padding=(0, 10))
    edit_frame.grid(row=2, column=0, sticky="ew")
    edit_frame.columnconfigure(1, weight=1)
    edit_frame.columnconfigure(3, weight=1)
    
    ttk.Label(edit_frame, text="Descripción:").grid(row=0, column=0, sticky="w", padx=5)
    entry_desc = ttk.Entry(edit_frame, width=30)
    entry_desc.grid(row=0, column=1, sticky="ew", padx=5)
    
    # --- CAMBIO (Punto 2) ---
    ttk.Label(edit_frame, text="Calificación (0-100):").grid(row=0, column=2, sticky="w", padx=5)
    entry_grade = ttk.Entry(edit_frame, width=10)
    entry_grade.grid(row=0, column=3, sticky="ew", padx=5)

    # --- CAMBIO (Punto 3) ---
    ttk.Label(edit_frame, text="Porcentaje (ej: 30):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_peso = ttk.Entry(edit_frame, width=30)
    entry_peso.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    # --- Frame de Botones (Sin cambios) ---
    btn_frame = ttk.Frame(activity_frame, style="Main.TFrame")
    btn_frame.grid(row=3, column=0, sticky="ew", pady=10)

    btn_new = ttk.Button(btn_frame, text="Agregar Nueva", command=lambda: add_new_activity())
    btn_new.pack(side=tk.LEFT, padx=5)

    btn_edit = ttk.Button(btn_frame, text="Guardar Edición", command=lambda: save_activity_edit(), style="Accent.TButton")
    btn_edit.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(btn_frame, text="Eliminar Tarea", command=lambda: delete_selected_activity(), style="Danger.TButton")
    btn_delete.pack(side=tk.RIGHT, padx=5)

    btn_clear = ttk.Button(btn_frame, text="Limpiar Campos", command=lambda: clear_fields(True))
    btn_clear.pack(side=tk.LEFT, padx=5)
    
    lbl_avg_text = tk.StringVar(value="Promedio Ponderado: N/A")
    ttk.Label(activity_frame, textvariable=lbl_avg_text, font=("Helvetica", 12, "bold")).grid(row=4, column=0, pady=10, sticky="e")

    # --- Lógica de la Pestaña ---

    def clear_fields(clear_selection=False):
        entry_desc.delete(0, tk.END)
        entry_grade.delete(0, tk.END)
        entry_peso.delete(0, tk.END)
        if clear_selection:
            activity_listbox.selection_clear(0, tk.END)

    def refresh_subjects():
        # ... (Sin cambios)
        subject_listbox.delete(0, tk.END); subject_map.clear()
        subjects = db_manager.get_subjects_by_professor(profesor_id)
        for subj in subjects:
            subject_listbox.insert(tk.END, subj["nombre"]); subject_map[subj["nombre"]] = subj["id"]
        student_listbox.delete(0, tk.END); activity_listbox.delete(0, tk.END)
        clear_fields(True); lbl_avg_text.set("Promedio Ponderado: N/A")

    def on_subject_select(event):
        # ... (Sin cambios)
        selection = subject_listbox.curselection()
        if not selection: return
        subject_name = subject_listbox.get(selection[0]); subject_id = subject_map.get(subject_name)
        student_listbox.delete(0, tk.END); student_map.clear()
        students = db_manager.get_students_by_subject(subject_id)
        for stud in students:
            student_listbox.insert(tk.END, stud["nombre_completo"]); student_map[stud["nombre_completo"]] = stud["id"]
        activity_listbox.delete(0, tk.END); clear_fields(True); lbl_avg_text.set("Promedio Ponderado: N/A")

    def on_student_select(event):
        # ... (Sin cambios)
        selection = student_listbox.curselection()
        if not selection: return
        student_name = student_listbox.get(selection[0]); student_id = student_map.get(student_name)
        subject_id = subject_map.get(subject_listbox.get(subject_listbox.curselection()[0]))
        refresh_activities(student_id, subject_id)

    def on_activity_select(event):
        # --- MODIFICADO (Punto 3) ---
        selection = activity_listbox.curselection()
        if not selection: return
        selected_text = activity_listbox.get(selection[0]); activity_id = activity_map.get(selected_text)
        
        for act in current_activities:
            if act["id"] == activity_id:
                clear_fields()
                entry_desc.insert(0, act["descripcion"])
                entry_grade.insert(0, act["calificacion"])
                # Multiplicar por 100 para mostrar como porcentaje
                entry_peso.insert(0, act["peso"] * 100)
                break

    subject_listbox.bind("<<ListboxSelect>>", on_subject_select)
    student_listbox.bind("<<ListboxSelect>>", on_student_select)
    activity_listbox.bind("<<ListboxSelect>>", on_activity_select)

    current_activities = []
    def refresh_activities(student_id, subject_id):
        # --- MODIFICADO (Punto 3) ---
        activity_listbox.delete(0, tk.END); activity_map.clear(); current_activities.clear()
        clear_fields(True)
        
        activities = db_manager.get_activities_by_student_subject(student_id, subject_id)
        current_activities.extend(activities)
        
        for act in activities:
            # Mostrar peso como porcentaje
            display_text = f"{act['descripcion']} | Cal: {act['calificacion']} | Peso: {act['peso'] * 100}%"
            activity_listbox.insert(tk.END, display_text)
            activity_map[display_text] = act["id"]
        
        avg = db_manager.get_weighted_average(student_id, subject_id)
        lbl_avg_text.set(f"Promedio Ponderado: {avg}")

    def get_current_selection():
        # ... (Sin cambios)
        subj_sel = subject_listbox.curselection(); stud_sel = student_listbox.curselection()
        if not subj_sel or not stud_sel:
            messagebox.showwarning("Sin selección", "Debes seleccionar una materia y un alumno.")
            return None, None
        subject_id = subject_map.get(subject_listbox.get(subj_sel[0]))
        student_id = student_map.get(student_listbox.get(stud_sel[0]))
        return subject_id, student_id

    def add_new_activity():
        # --- MODIFICADO (Puntos 2 y 3) ---
        subject_id, student_id = get_current_selection()
        if not student_id: return

        try:
            desc = entry_desc.get().strip()
            cal = float(entry_grade.get().strip())
            # Dividir el porcentaje entre 100 para guardarlo como peso
            peso = float(entry_peso.get().strip()) / 100.0
        except ValueError:
            messagebox.showerror("Error de formato", "Calificación y Porcentaje deben ser números.")
            return

        # --- Validación (Punto 2) ---
        if not (0 <= cal <= 100):
            messagebox.showwarning("Valor incorrecto", "La calificación debe estar entre 0 y 100.")
            return
            
        if not (0 <= peso <= 1):
             messagebox.showwarning("Valor incorrecto", "El porcentaje debe ser razonable (ej. 30 para 30%).")
             return

        if not desc:
            messagebox.showwarning("Campo vacío", "La descripción es obligatoria.")
            return
        
        if db_manager.add_activity(student_id, subject_id, cal, peso, desc):
            refresh_activities(student_id, subject_id)
        else:
            messagebox.showerror("Error", "No se pudo agregar la actividad.")

    def save_activity_edit():
        # --- MODIFICADO (Puntos 2 y 3) ---
        act_sel = activity_listbox.curselection()
        if not act_sel:
            messagebox.showwarning("Sin selección", "Selecciona una actividad de la lista para editar.")
            return
            
        activity_id = activity_map.get(activity_listbox.get(act_sel[0]))
        
        try:
            desc = entry_desc.get().strip()
            cal = float(entry_grade.get().strip())
            # Dividir el porcentaje entre 100
            peso = float(entry_peso.get().strip()) / 100.0
        except ValueError:
            messagebox.showerror("Error de formato", "Calificación y Porcentaje deben ser números.")
            return

        # --- Validación (Punto 2) ---
        if not (0 <= cal <= 100):
            messagebox.showwarning("Valor incorrecto", "La calificación debe estar entre 0 y 100.")
            return
            
        if not (0 <= peso <= 1):
             messagebox.showwarning("Valor incorrecto", "El porcentaje debe ser razonable (ej. 30 para 30%).")
             return

        if db_manager.update_activity(activity_id, desc, cal, peso):
            subject_id, student_id = get_current_selection()
            refresh_activities(student_id, subject_id)
        else:
            messagebox.showerror("Error", "No se pudo guardar la edición.")

    def delete_selected_activity():
        # ... (Sin cambios)
        act_sel = activity_listbox.curselection()
        if not act_sel:
            messagebox.showwarning("Sin selección", "Selecciona una actividad de la lista para eliminar.")
            return
        
        activity_id = activity_map.get(activity_listbox.get(act_sel[0]))
        
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta actividad?"):
            if db_manager.delete_activity(activity_id):
                subject_id, student_id = get_current_selection()
                refresh_activities(student_id, subject_id)
            else:
                messagebox.showerror("Error", "No se pudo eliminar la actividad.")

    # Carga inicial
    refresh_subjects()
    return tab