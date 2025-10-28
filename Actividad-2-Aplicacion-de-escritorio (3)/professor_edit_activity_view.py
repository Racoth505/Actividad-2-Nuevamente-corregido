# professor_edit_activity_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager  # Importar lógica de BBDD

def create_professor_edit_activity_view(parent_frame, user_data):
    """Crea la vista para editar la definición de una actividad existente."""

    professor_id = user_data['id']

    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    # No pack aún

    # --- CORRECCIÓN 1: Centrar el título ---
    ttk.Label(main_frame, text="Editar Actividad", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10, anchor='w', padx=10)

    selection_frame = ttk.Frame(main_frame, style="Main.TFrame")
    # --- CORRECCIÓN 2: Centrar el frame de selección (quitar fill='x') ---
    selection_frame.pack(pady=10, padx=20, anchor='n')

    # Variables
    materia_seleccionada_var = tk.StringVar()
    actividad_seleccionada_var = tk.StringVar()  # Guardará la descripción original

    # --- Selección Materia y Actividad ---
    ttk.Label(selection_frame, text="Materia:", style="TLabel").grid(row=0, column=0, sticky='w')

    materias_profesor = db_manager.get_subjects_by_professor(professor_id)
    materia_options = {m['nombre']: m['id'] for m in materias_profesor}

    combo_materias = ttk.Combobox(
        selection_frame,
        textvariable=materia_seleccionada_var,
        values=list(materia_options.keys()),
        state='readonly',
        width=30
    )
    combo_materias.grid(row=1, column=0, padx=(0, 20), pady=5)

    ttk.Label(selection_frame, text="Actividad a Editar:", style="TLabel").grid(row=0, column=1, sticky='w')
    combo_actividades = ttk.Combobox(
        selection_frame,
        textvariable=actividad_seleccionada_var,
        state='disabled',
        width=30
    )
    combo_actividades.grid(row=1, column=1, pady=5)

    # Frame para el formulario de edición (se llena al seleccionar)
    form_frame = ttk.Frame(main_frame, style="Main.TFrame")
    # No pack aún

    # Variables del formulario (se llenarán al cargar)
    tipo_actividad_var = tk.StringVar()
    descripcion_var = tk.StringVar()
    peso_var = tk.StringVar()
    fecha_inicio_var = tk.StringVar()
    hora_inicio_var = tk.StringVar()
    fecha_fin_var = tk.StringVar()
    hora_fin_var = tk.StringVar()

    def cargar_actividades(*args):
        """Carga las descripciones de actividades para la materia seleccionada."""
        materia_nombre = materia_seleccionada_var.get()
        materia_id = materia_options.get(materia_nombre)

        # Limpiar formulario y combo de actividades
        for widget in form_frame.winfo_children(): 
            widget.destroy()
        form_frame.pack_forget()
        combo_actividades['values'] = []
        combo_actividades.set('')
        combo_actividades.config(state='disabled')
        actividad_seleccionada_var.set('')  # Limpiar selección

        if not materia_id: 
            return

        actividades_defs = db_manager.get_distinct_activities_for_subject(materia_id)
        actividad_descripciones = [act[0] for act in actividades_defs]

        combo_actividades['values'] = actividad_descripciones
        if actividad_descripciones:
            combo_actividades.config(state='readonly')
            combo_actividades.current(0)
            cargar_datos_actividad()  # Cargar datos de la primera
        else:
            ttk.Label(form_frame, text="No hay actividades definidas para esta materia.", style="TLabel").pack(pady=10)
            # --- CORRECCIÓN 3.1: Centrar mensaje (quitar fill='x') ---
            form_frame.pack(pady=10, padx=20, anchor='n')

    def cargar_datos_actividad(*args):
        """Carga los detalles de la actividad seleccionada en el formulario."""
        descripcion_original = actividad_seleccionada_var.get()
        materia_id = materia_options.get(materia_seleccionada_var.get())

        for widget in form_frame.winfo_children(): 
            widget.destroy()  # Limpiar form

        if not descripcion_original or not materia_id:
            form_frame.pack_forget()
            return

        # Obtener detalles de la BBDD
        act_details = db_manager.get_activity_definition(materia_id, descripcion_original)

        if not act_details:
            ttk.Label(form_frame, text="Error al cargar detalles de la actividad.", foreground='red', style="TLabel").pack(pady=10)
            # --- CORRECCIÓN 3.2: Centrar mensaje de error (quitar fill='x') ---
            form_frame.pack(pady=10, padx=20, anchor='n')
            return

        # Llenar variables del formulario
        tipo_actividad_var.set(act_details.get('tipo_actividad', ''))
        descripcion_var.set(descripcion_original)  # Mostrar descripción original
        peso_var.set(str(act_details.get('peso', '')))
        fecha_inicio_var.set(act_details.get('fecha_inicio', '') or '')
        hora_inicio_var.set(act_details.get('hora_inicio', '') or '')
        fecha_fin_var.set(act_details.get('fecha_fin', '') or '')
        hora_fin_var.set(act_details.get('hora_fin', '') or '')

        # --- Re-crear el formulario ---
        campos_labels = [
            "Tipo de Actividad", "Nueva Descripción (si cambia)", "Peso (Decimal 0.0-1.0)",
            "Fecha Inicio", "Hora Inicio", "Fecha Fin", "Hora Fin"
        ]
        campos_vars = [
            tipo_actividad_var, descripcion_var, peso_var,
            fecha_inicio_var, hora_inicio_var, fecha_fin_var, hora_fin_var
        ]

        for i, (label_text, var) in enumerate(zip(campos_labels, campos_vars)):
            ttk.Label(form_frame, text=label_text, style="TLabel").grid(row=i, column=0, sticky='w', padx=5, pady=5)
            ttk.Entry(form_frame, textvariable=var, width=40).grid(row=i, column=1, sticky='we', padx=5, pady=5)

        final_row = len(campos_labels)

        # --- Botón Guardar Cambios ---
        def guardar_cambios_actividad():
            materia_id_guardar = materia_options.get(materia_seleccionada_var.get())
            descripcion_original_guardar = actividad_seleccionada_var.get()  # La que se seleccionó

            nuevo_tipo = tipo_actividad_var.get().strip() or "Actividad"
            nueva_descripcion = descripcion_var.get().strip()
            nuevo_peso_str = peso_var.get().strip()
            nuevo_f_inicio = fecha_inicio_var.get().strip() or None
            nuevo_h_inicio = hora_inicio_var.get().strip() or None
            nuevo_f_fin = fecha_fin_var.get().strip() or None
            nuevo_h_fin = hora_fin_var.get().strip() or None
            nuevo_peso = None

            if not nueva_descripcion or not nuevo_peso_str:
                messagebox.showwarning("Falta Información", "La Descripción y el Peso son obligatorios.")
                return
            try:
                nuevo_peso = float(nuevo_peso_str)
                if not (0.0 <= nuevo_peso <= 1.0):
                    messagebox.showwarning("Inválido", "El Peso debe ser decimal entre 0.0 y 1.0.")
                    return
            except ValueError:
                messagebox.showwarning("Inválido", "El Peso debe ser numérico (ej: 0.25).")
                return

            # Verificar si la nueva descripción ya existe (y no es la original)
            if nueva_descripcion.lower() != descripcion_original_guardar.lower():
                existing_defs = db_manager.get_distinct_activities_for_subject(materia_id_guardar)
                if any(desc[0].lower() == nueva_descripcion.lower() for desc in existing_defs):
                    messagebox.showerror("Error", f"Ya existe otra actividad con la descripción '{nueva_descripcion}' en esta materia.")
                    return

            # --- Lógica BBDD ---
            success = db_manager.update_activity_definition(
                id_materia=materia_id_guardar,
                old_descripcion=descripcion_original_guardar,
                new_tipo=nuevo_tipo,
                new_descripcion=nueva_descripcion,
                new_peso=nuevo_peso,
                new_fecha_inicio=nuevo_f_inicio,
                new_hora_inicio=nuevo_h_inicio,
                new_fecha_fin=nuevo_f_fin,
                new_hora_fin=nuevo_h_fin
            )

            if success:
                messagebox.showinfo("Éxito", f"Definición de actividad '{nueva_descripcion}' actualizada.")
                # Recargar lista desplegable por si cambió la descripción
                cargar_actividades()
                # Seleccionar la nueva descripción si cambió
                if nueva_descripcion != descripcion_original_guardar:
                    try:
                        new_index = combo_actividades['values'].index(nueva_descripcion)
                        combo_actividades.current(new_index)
                    except ValueError:
                        pass  # Si no se encuentra, no hacer nada
                else:
                    cargar_datos_actividad()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la definición de la actividad.")

        ttk.Button(form_frame, text="Guardar Cambios", command=guardar_cambios_actividad,
                   style="Green.TButton", width=20).grid(row=final_row, column=0, columnspan=2, pady=20)

        # --- CORRECCIÓN 3.3: Centrar el formulario (quitar fill='x') ---
        form_frame.pack(pady=10, padx=20, anchor='n')  # Mostrar el form

    # Bindings para actualizar
    materia_seleccionada_var.trace_add("write", cargar_actividades)
    actividad_seleccionada_var.trace_add("write", cargar_datos_actividad)

    # Carga inicial si hay materias
    if materia_options:
        combo_materias.current(0)
        cargar_actividades()

    return main_frame
