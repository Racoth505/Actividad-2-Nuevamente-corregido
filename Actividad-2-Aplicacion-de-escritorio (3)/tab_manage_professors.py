# tab_manage_professors.py
import tkinter as tk
from tkinter import messagebox, ttk
import db_manager

def create_manage_professors_tab(parent):
    """
    Pestaña del Admin para crear profesores y asignarles materias.
    """
    tab = ttk.Frame(parent, style="Main.TFrame")

    # --- Configuración Responsiva ---
    tab.rowconfigure(0, weight=1)
    tab.columnconfigure(0, weight=1, minsize=300)
    tab.columnconfigure(1, weight=1, minsize=300)

    # --- Columna Izquierda (Lista de Profesores) ---
    list_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    list_frame.grid(row=0, column=0, sticky="nsew")
    list_frame.rowconfigure(1, weight=1)
    list_frame.columnconfigure(0, weight=1)

    ttk.Label(list_frame, text="Profesores Existentes", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")
    
    prof_listbox = tk.Listbox(list_frame, font=("Helvetica", 11), borderwidth=0)
    prof_listbox.grid(row=1, column=0, sticky="nsew")

    def refresh_prof_list():
        prof_listbox.delete(0, tk.END)
        try:
            professors = db_manager.get_users_by_role("profesor")
            for prof in professors:
                prof_listbox.insert(tk.END, prof["nombre_completo"])
        except Exception as e:
            print(f"Error al refrescar lista de profesores: {e}")

    # --- Columna Derecha (Crear Profesor) ---
    create_frame = ttk.Frame(tab, style="Main.TFrame", padding=10)
    create_frame.grid(row=0, column=1, sticky="nsew")
    create_frame.columnconfigure(1, weight=1)
    create_frame.rowconfigure(4, weight=1) # Fila de la lista de materias

    ttk.Label(create_frame, text="Crear Nuevo Profesor", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

    ttk.Label(create_frame, text="Nombre Completo:").grid(row=1, column=0, sticky="w", pady=5)
    entry_name = ttk.Entry(create_frame, width=30)
    entry_name.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

    ttk.Label(create_frame, text="Usuario (Matrícula):").grid(row=2, column=0, sticky="w", pady=5)
    entry_username = ttk.Entry(create_frame, width=30)
    entry_username.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

    ttk.Label(create_frame, text="Contraseña:").grid(row=3, column=0, sticky="w", pady=5)
    entry_password = ttk.Entry(create_frame, width=30, show="*")
    entry_password.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

    ttk.Label(create_frame, text="Asignar Materias (Ctrl+Click):").grid(row=4, column=0, sticky="nw", pady=5)
    
    subject_listbox = tk.Listbox(create_frame, selectmode=tk.MULTIPLE, exportselection=False, borderwidth=0)
    subject_listbox.grid(row=4, column=1, sticky="nsew", pady=5, padx=5)

    subject_map = {}
    def refresh_subject_list():
        subject_listbox.delete(0, tk.END)
        subject_map.clear()
        try:
            subjects = db_manager.get_subjects()
            for subj in subjects:
                subject_listbox.insert(tk.END, subj["nombre"])
                subject_map[subj["nombre"]] = subj["id"]
        except Exception as e:
            print(f"Error al refrescar materias: {e}")

    # --- Lógica de Creación ---
    def create_new_professor():
        name = entry_name.get().strip()
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        
        if not name or not username or not password:
            messagebox.showwarning("Campos incompletos", "Nombre, Matrícula y Contraseña son obligatorios.")
            return

        new_prof_id = db_manager.create_user(username, password, "profesor", name)
        
        if not new_prof_id:
            messagebox.showerror("Error", f"La matrícula '{username}' ya existe.")
            return

        # Asignar materias seleccionadas
        selected_indices = subject_listbox.curselection()
        for i in selected_indices:
            subject_name = subject_listbox.get(i)
            subject_id = subject_map.get(subject_name)
            if subject_id:
                db_manager.assign_subject_to_prof(new_prof_id, subject_id)
        
        messagebox.showinfo("Éxito", f"Profesor '{name}' creado exitosamente.")
        
        entry_name.delete(0, tk.END)
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        subject_listbox.selection_clear(0, tk.END)
        refresh_prof_list()
        refresh_subject_list()

    btn_create = ttk.Button(create_frame, text="Crear Profesor", command=create_new_professor, style="Accent.TButton")
    btn_create.grid(row=5, column=0, columnspan=2, pady=10)

    # Carga inicial
    refresh_prof_list()
    refresh_subject_list()
    
    return tab