# admin_edit_subjects_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importa la lógica de la BBDD

# --- Helper function: Get user by USERNAME ---
def get_user_by_username(username):
    """Función helper para buscar un usuario por su username."""
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user: return dict(user)
    return None

def create_edit_subjects_view(parent_frame):
    """Crea la vista para editar materias existentes (Layout igual a Edit Users)."""

    # --- Frame Principal (view_frame) ---
    view_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    view_frame.columnconfigure(0, weight=1)
    view_frame.rowconfigure(3, weight=1) # Fila 3 se expande para empujar contenido arriba

    current_subject_id = None # Guardar el ID (int) de la materia cargada

    # --- Título ---
    title_frame = ttk.Frame(view_frame, style="Main.TFrame")
    title_frame.grid(row=0, column=0, sticky="n", pady=(0,20))
    ttk.Label(title_frame, text="Editar Materias", font=("Helvetica", 18, "bold"), style="TLabel") \
        .pack()

    # --- Frame de búsqueda ---
    search_frame = ttk.Frame(view_frame, style="Main.TFrame")
    search_frame.grid(row=1, column=0, pady=(0,10))

    ttk.Label(search_frame, text="ID de la Materia a editar:", style="TLabel") \
        .grid(row=0, column=0, sticky='e', padx=5, pady=5)
    materia_id_search_var = tk.StringVar()
    entry_search = ttk.Entry(search_frame, textvariable=materia_id_search_var, width=40)
    entry_search.grid(row=0, column=1, padx=5, pady=5, ipady=4)

    # --- Frame de edición ---
    edit_frame = ttk.Frame(view_frame, style="Main.TFrame")
    edit_frame.grid(row=2, column=0, pady=(0,10), sticky='n') # Pegado arriba

    # --- Variables ---
    nombre_var = tk.StringVar()
    profesor_id_var = tk.StringVar() # Guardará el ID numérico como string
    horas_var = tk.StringVar()
    salon_var = tk.StringVar()
    fecha_inicio_var = tk.StringVar()
    fecha_fin_var = tk.StringVar()

    # Definir el Label fuera de cargar_materia
    # Sigue siendo hijo de 'edit_frame' temporalmente, será destruido.
    nombre_profesor_display = ttk.Label(edit_frame, text="", style="TLabel", foreground='gray')

    def actualizar_nombre_profesor_edit(*args):
        profesor_id_str = profesor_id_var.get().strip()
        
        # Necesitamos encontrar la instancia 'real' del label
        # Buscamos por el frame de edición, ya que el 'nombre_profesor_display' global
        # puede estar destruido.
        try:
            # Buscar el fields_container
            fields_container = edit_frame.nametowidget('fields_container')
            # Buscar el label dentro de él
            real_display_label = fields_container.nametowidget('prof_display_label')
        except KeyError:
            return # El widget aún no existe, no hacer nada

        if not profesor_id_str:
            real_display_label.config(text="", foreground='gray') # Limpiar si está vacío
            return

        try:
            prof_id = int(profesor_id_str)
            user = db_manager.get_user_by_id(prof_id) 

            if user and user['role'] == 'profesor':
                nombre = user.get('nombre_completo', '')
                ap = user.get('apellidos', '')
                real_display_label.config(text=f"✓ {nombre} {ap}".strip(), foreground='green')
            else:
                 real_display_label.config(text="✗ ID no es de un profesor válido", foreground='red')

        except ValueError:
            real_display_label.config(text="✗ ID debe ser numérico", foreground='red')
        except Exception as e:
            print(f"Error validando ID de profesor {profesor_id_str}: {e}")
            real_display_label.config(text="Error", foreground='red')

    profesor_id_var.trace_add("write", actualizar_nombre_profesor_edit)

    def cargar_materia():
        nonlocal current_subject_id
        materia_id_str = materia_id_search_var.get().strip()

        for widget in edit_frame.winfo_children():
            widget.destroy() # Esto destruye el 'nombre_profesor_display' temporal

        if not materia_id_str.isdigit():
             ttk.Label(edit_frame, text="ID de la materia debe ser numérico.", foreground='red', style="TLabel").pack(pady=2)
             current_subject_id = None
             return

        try:
            mat_id = int(materia_id_str)
            materia_data = db_manager.get_subject_details(mat_id)
        except ValueError:
             ttk.Label(edit_frame, text="ID de la materia debe ser numérico.", foreground='red', style="TLabel").pack(pady=2)
             current_subject_id = None
             return

        if not materia_data:
            ttk.Label(edit_frame, text=f"Materia con ID '{mat_id}' no encontrada.", foreground='red', style="TLabel").pack(pady=2)
            current_subject_id = None
            return

        current_subject_id = materia_data['id'] # Guardar ID

        # Título del usuario cargado
        ttk.Label(edit_frame, text=f"Editando: {materia_data.get('nombre', '')} (ID: {materia_data.get('id')})",
                  font=("Helvetica", 14, "bold"), style="TLabel") \
            .pack(pady=(0,10))

        # Cargar datos en las variables
        nombre_var.set(materia_data.get('nombre', ''))
        prof_id_principal = materia_data.get('id_profesor_principal')
        profesor_id_var.set(str(prof_id_principal) if prof_id_principal is not None else "") 
        horas_val = materia_data.get('horas_semanales')
        horas_var.set(str(horas_val) if horas_val is not None else "")
        salon_var.set(materia_data.get('salon', '') or "") 
        fecha_inicio_var.set(materia_data.get('fecha_inicio', '') or "") 
        fecha_fin_var.set(materia_data.get('fecha_fin', '') or "") 

        campos = [
            ("Nombre de la Materia", nombre_var),
            ("ID Profesor Principal", profesor_id_var),
            ("Horas Semanales", horas_var),
            ("Salón", salon_var),
            ("Fecha Inicio (YYYY-MM-DD)", fecha_inicio_var),
            ("Fecha Fin (YYYY-MM-DD)", fecha_fin_var)
        ]

        # --- Frame para los campos de entrada (alineados) ---
        # Le damos un nombre para poder encontrarlo
        fields_container = ttk.Frame(edit_frame, style="Main.TFrame", name='fields_container')
        fields_container.pack(pady=5)
        
        # --- INICIO DE LA CORRECCIÓN ---
        # 1. Crear el label de feedback como hijo de fields_container
        #    y darle un nombre único.
        nombre_profesor_display = ttk.Label(fields_container, text="", style="TLabel", 
                                            foreground='gray', name='prof_display_label')
        # --- FIN DE LA CORRECCIÓN ---


        for i, (label_text, var) in enumerate(campos):
            ttk.Label(fields_container, text=label_text, style="TLabel") \
                .grid(row=i, column=0, sticky='e', padx=5, pady=3)
            entry = ttk.Entry(fields_container, textvariable=var, width=40)
            
            if var == nombre_var:
                entry.config(state='disabled')

            entry.grid(row=i, column=1, sticky='w', padx=5, pady=3, ipady=4)
            
            if var == profesor_id_var:
                # 2. Ahora esto es legal, porque 'nombre_profesor_display'
                #    es hijo de 'fields_container', que usa grid().
                nombre_profesor_display.grid(row=i, column=2, sticky='w', padx=10)
                actualizar_nombre_profesor_edit() # Actualizarlo con los datos cargados


        # --- Lógica de guardar ---
        def guardar_cambios_materia():
            if current_subject_id is None: return
            profesor_id_str = profesor_id_var.get().strip()
            horas_str = horas_var.get().strip()
            prof_id = None
            horas = None

            if profesor_id_str:
                if not profesor_id_str.isdigit():
                    messagebox.showerror("Error", "ID de Profesor debe ser un número.")
                    return
                prof_id = int(profesor_id_str)
                user = db_manager.get_user_by_id(prof_id)
                if not (user and user['role'] == 'profesor'):
                    messagebox.showerror("Error", "ID de Profesor no es válido.")
                    return
            
            if horas_str:
                if not horas_str.isdigit():
                    messagebox.showerror("Error", "Horas Semanales debe ser un número.")
                    return
                horas = int(horas_str)

            success = db_manager.update_subject_details(
                subject_id=current_subject_id,
                nombre=nombre_var.get().strip(), 
                id_profesor=prof_id,
                horas=horas,
                salon=salon_var.get().strip() or None,
                inicio=fecha_inicio_var.get().strip() or None,
                fin=fecha_fin_var.get().strip() or None
            )
            if success:
                messagebox.showinfo("Éxito", f"Materia '{nombre_var.get()}' actualizada.")
                cargar_materia() 
            else:
                 messagebox.showerror("Error", "No se pudo actualizar la materia.")

        def delete_materia():
            if current_subject_id is None: return
            if messagebox.askyesno(
                "Confirmar",
                f"¿Seguro que quieres eliminar la materia (ID: {current_subject_id})?\n"
                "Esto borrará todas las inscripciones y calificaciones asociadas."
            ):
                if db_manager.delete_subject(current_subject_id):
                    messagebox.showinfo("Eliminado", "Materia eliminada.")
                    materia_id_search_var.set("")
                    for w in edit_frame.winfo_children(): w.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la materia.")

        # Botones de acción centrados
        btn_frame = ttk.Frame(edit_frame, style="Main.TFrame")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios_materia, style="Green.TButton") \
            .pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar Materia", command=delete_materia, style="Danger.TButton") \
            .pack(side="left", padx=5)


    ttk.Button(search_frame, text="Buscar", command=cargar_materia, style="Accent.TButton") \
        .grid(row=0, column=2, padx=5)
    entry_search.bind("<Return>", lambda event: cargar_materia())

    return view_frame # Devolver solo el frame principal