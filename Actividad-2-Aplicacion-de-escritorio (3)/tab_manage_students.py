# tab_manage_students.py
import tkinter as tk
from tkinter import messagebox, ttk
import db_manager # Importamos el nuevo manager

def create_manage_students_tab(parent):
    """
    Pestaña del Admin para crear alumnos e inscribirlos a materias.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")

    # --- Configuración Responsiva ---
    tab.rowconfigure(0, weight=1)
    tab.columnconfigure(0, weight=1, minsize=300) # Columna de lista
    tab.columnconfigure(1, weight=1, minsize=300) # Columna de creación

    # --- Columna Izquierda (Lista de Alumnos) ---
    list_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    list_frame.grid(row=0, column=0, sticky="nsew")
    list_frame.rowconfigure(1, weight=1)
    list_frame.columnconfigure(0, weight=1)

    ttk.Label(list_frame, text="Alumnos Existentes", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    
    listbox = tk.Listbox(list_frame, font=("Helvetica", 11), borderwidth=0)
    listbox.grid(row=1, column=0, sticky="nsew")
    
    def refresh_student_list():
        listbox.delete(0, tk.END)
        try:
            students = db_manager.get_users_by_role("alumno")
            for student in students:
                listbox.insert(tk.END, student["nombre_completo"])
        except Exception as e:
            print(f"Error al refrescar lista de alumnos: {e}")

    # --- Columna Derecha (Crear Alumno) ---
    create_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    create_frame.grid(row=0, column=1, sticky="nsew")
    create_frame.columnconfigure(1, weight=1)
    create_frame.rowconfigure(4, weight=1) # Fila de la lista de materias se expande

    ttk.Label(create_frame, text="Crear Nuevo Alumno", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

    ttk.Label(create_frame, text="Nombre Completo:").grid(row=1, column=0, sticky="w", pady=5)
    entry_name = ttk.Entry(create_frame, width=30)
    entry_name.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

    ttk.Label(create_frame, text="Usuario (Matrícula):").grid(row=2, column=0, sticky="w", pady=5)
    entry_username = ttk.Entry(create_frame, width=30)
    entry_username.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

    ttk.Label(create_frame, text="Contraseña:").grid(row=3, column=0, sticky="w", pady=5)
    entry_password = ttk.Entry(create_frame, width=30, show="*")
    entry_password.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

    # --- CAMBIO AQUÍ: De Combobox a Listbox ---
    ttk.Label(create_frame, text="Inscribir a Materias (Ctrl+Click):").grid(row=4, column=0, sticky="nw", pady=5)
    subject_listbox = tk.Listbox(create_frame, selectmode=tk.MULTIPLE, exportselection=False, borderwidth=0)
    subject_listbox.grid(row=4, column=1, sticky="nsew", pady=5, padx=5)
    
    # --- Cargar Materias en el Listbox ---
    subject_map = {} # Para mapear "Nombre de Materia" -> ID
    def refresh_subject_list():
        subject_listbox.delete(0, tk.END)
        subject_map.clear()
        try:
            subjects = db_manager.get_subjects()
            for subj in subjects:
                subject_listbox.insert(tk.END, subj["nombre"])
                subject_map[subj["nombre"]] = subj["id"]
        except Exception as e:
            print(f"Error al refrescar lista de materias: {e}")

    # --- Lógica de Creación (Actualizada) ---
    def create_new_student():
        name = entry_name.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        
        if not name or not username or not password:
            messagebox.showwarning("Campos incompletos", "Nombre, Matrícula y Contraseña son obligatorios.")
            return

        # 1. Crear el usuario
        new_user_id = db_manager.create_user(username, password, "alumno", name)
        
        if not new_user_id:
            messagebox.showerror("Error", f"La matrícula '{username}' ya existe.")
            return

        # 2. Inscribir a TODAS las materias seleccionadas
        selected_indices = subject_listbox.curselection()
        if not selected_indices:
             messagebox.showinfo("Éxito", f"Alumno '{name}' creado sin materias inscritas.")
        else:
            for i in selected_indices:
                subject_name = subject_listbox.get(i)
                subject_id = subject_map.get(subject_name)
                if subject_id:
                    db_manager.enroll_student(new_user_id, subject_id)
            messagebox.showinfo("Éxito", f"Alumno '{name}' creado e inscrito en {len(selected_indices)} materia(s).")
        
        # Limpiar campos y refrescar listas
        entry_name.delete(0, tk.END)
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        subject_listbox.selection_clear(0, tk.END)
        refresh_student_list()
        refresh_subject_list()

    btn_create = ttk.Button(create_frame, text="Crear Alumno", command=create_new_student, style="Accent.TButton")
    btn_create.grid(row=5, column=0, columnspan=2, pady=10)

    # Carga inicial
    refresh_student_list()
    refresh_subject_list()
    
    return tab