# professor_add_activity_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importar lógica de BBDD

def create_professor_add_activity_view(parent_frame, user_data):
    """Crea la vista para agregar (definir) una nueva actividad a una materia."""
    
    professor_id = user_data['id']
    
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    # No pack aquí

    ttk.Label(main_frame, text="➕ Agregar Actividad", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10, anchor='w', padx=10)

    form_frame = ttk.Frame(main_frame, style="Main.TFrame")
    form_frame.pack(pady=10, padx=20, anchor='n')

    # Variables
    materia_seleccionada_var = tk.StringVar()
    tipo_actividad_var = tk.StringVar(value="Tarea") # Valor inicial
    descripcion_var = tk.StringVar() # Este será el nombre/descripción único
    peso_var = tk.StringVar() # Peso como decimal (ej: 0.3 para 30%)
    fecha_inicio_var = tk.StringVar()
    fecha_fin_var = tk.StringVar()
    hora_inicio_var = tk.StringVar()
    hora_fin_var = tk.StringVar()

    # --- Selección de Materia ---
    ttk.Label(form_frame, text="Materia:", style="TLabel").grid(row=0, column=0, sticky='w', pady=(0,5), padx=5)
    
    materias_profesor = db_manager.get_subjects_by_professor(professor_id)
    materia_options = {m['nombre']: m['id'] for m in materias_profesor} # {Nombre: ID}
    
    if not materia_options:
         ttk.Label(form_frame, text="Primero debes tener materias asignadas.", foreground='red', style="TLabel").grid(row=1, column=0, columnspan=2)
         return main_frame

    combo_materias = ttk.Combobox(form_frame, textvariable=materia_seleccionada_var, 
                                  values=list(materia_options.keys()), state='readonly', width=58)
    combo_materias.grid(row=1, column=0, columnspan=2, sticky='we', pady=(0, 15), padx=5)
    if materia_options:
        combo_materias.current(0)

    # --- Layout de Formulario ---
    campos_labels = [
        "Tipo de Actividad (Tarea, Examen, etc.)",
        "Descripción ÚNICA (Ej: Tarea 1, Examen Parcial 2)", 
        "Peso (Decimal 0.0 a 1.0, Ej: 0.3 para 30%)", 
        "Fecha de Inicio (YYYY-MM-DD)", "Hora de Inicio (HH:MM)", 
        "Fecha de Fin (YYYY-MM-DD)", "Hora de Fin (HH:MM)"
    ]
    campos_vars = [
        tipo_actividad_var, descripcion_var, peso_var,
        fecha_inicio_var, hora_inicio_var, fecha_fin_var, hora_fin_var
    ]
    
    current_row = 2
    for i, (label_text, var) in enumerate(zip(campos_labels, campos_vars)):
        ttk.Label(form_frame, text=label_text, style="TLabel").grid(row=current_row + i, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=var, width=40).grid(row=current_row + i, column=1, sticky='we', padx=5, pady=5)
        
    final_row = current_row + len(campos_labels)
    
    # --- Botón Guardar ---
    def guardar_actividad():
        materia_nombre = materia_seleccionada_var.get()
        if not materia_nombre:
            messagebox.showwarning("Falta Información", "Selecciona una materia.")
            return
        materia_id = materia_options.get(materia_nombre)
        
        tipo = tipo_actividad_var.get().strip() or "Actividad" # Default si se deja vacío
        descripcion = descripcion_var.get().strip()
        peso_str = peso_var.get().strip()
        f_inicio = fecha_inicio_var.get().strip() or None
        f_fin = fecha_fin_var.get().strip() or None
        h_inicio = hora_inicio_var.get().strip() or None
        h_fin = hora_fin_var.get().strip() or None
        peso = None

        if not descripcion or not peso_str:
            messagebox.showwarning("Falta Información", "La Descripción y el Peso son obligatorios.")
            return

        try:
            peso = float(peso_str)
            if not (0.0 <= peso <= 1.0):
                 messagebox.showwarning("Inválido", "El Peso debe ser un número decimal entre 0.0 y 1.0.")
                 return
        except ValueError:
            messagebox.showwarning("Inválido", "El Peso debe ser un número decimal (ej. 0.3).")
            return

        # --- Lógica BBDD ---
        # Verificar si ya existe una actividad con esa descripción en esa materia
        existing_defs = db_manager.get_distinct_activities_for_subject(materia_id)
        if any(desc[0].lower() == descripcion.lower() for desc in existing_defs):
             messagebox.showerror("Error", f"Ya existe una actividad con la descripción '{descripcion}' en esta materia.")
             return

        # Llamar a db_manager para añadir la definición (y crear entradas para alumnos)
        success = db_manager.add_activity_definition(
            id_materia=materia_id,
            tipo_actividad=tipo,
            descripcion=descripcion,
            peso=peso,
            fecha_inicio=f_inicio,
            hora_inicio=h_inicio,
            fecha_fin=f_fin,
            hora_fin=h_fin
        )

        if success:
            messagebox.showinfo("Éxito", f"Actividad '{descripcion}' definida para '{materia_nombre}'.\nSe crearon entradas de calificación para los alumnos inscritos.")
            # Limpiar formulario
            tipo_actividad_var.set("Tarea"); descripcion_var.set(""); peso_var.set("")
            fecha_inicio_var.set(""); fecha_fin_var.set(""); hora_inicio_var.set(""); hora_fin_var.set("")
        else:
            # Podría fallar si no hay alumnos inscritos o por error de BBDD
             messagebox.showerror("Error", "No se pudo definir la actividad. ¿Hay alumnos inscritos en la materia?")

    ttk.Button(form_frame, text="Definir Actividad", command=guardar_actividad, 
              style="Green.TButton", width=20).grid(row=final_row, column=0, columnspan=2, pady=20)

    return main_frame