# professor_grade_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importar lógica de BBDD

def create_professor_grade_view(parent_frame, user_data, subject_id):
    """Crea la vista de tabla para ingresar/editar calificaciones."""

    professor_id = user_data['id']

    # Frame principal
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    # No pack aquí

    materia_details = db_manager.get_subject_details(subject_id)
    if not materia_details:
        ttk.Label(main_frame, text="Error: Materia no encontrada.", foreground='red', style="TLabel").pack(pady=20)
        return main_frame

    ttk.Label(main_frame, text="Calificaciones", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=(10,0), anchor='w', padx=10)
    ttk.Label(main_frame, text=f"{materia_details.get('nombre')} (ID: {subject_id})",
              font=("Helvetica", 12), style="TLabel", foreground="#007bff").pack(pady=(0, 15), anchor='w', padx=10)

    # --- Obtener Datos ---
    alumnos = db_manager.get_students_by_subject(subject_id)
    actividades_defs = db_manager.get_distinct_activities_for_subject(subject_id)
    actividad_nombres = [act[0] for act in actividades_defs]
    actividad_pesos = {act[0]: act[1] for act in actividades_defs}
    grades_data = db_manager.get_grades_for_subject(subject_id)

    # --- Crear Treeview ---
    cols = ["id_alumno", "Alumno"] + actividad_nombres
    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

    x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")

    # --- Estilo para centrar texto en celdas de calificación ---
    style = ttk.Style()
    style.configure("Centered.Treeview", anchor="center")
    # Aplicar estilo general si se desea (opcional)
    # style.configure("Treeview", rowheight=25) # Ajustar altura de fila si se ve apretado

    tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                        yscrollcommand=y_scrollbar.set,
                        xscrollcommand=x_scrollbar.set,
                        height=15)

    y_scrollbar.config(command=tree.yview)
    x_scrollbar.config(command=tree.xview)

    # Configurar Encabezados y Columnas
    tree.heading("id_alumno", text="ID Alumno")
    tree.column("id_alumno", width=0, stretch=tk.NO)
    tree.heading("Alumno", text="Alumno")
    tree.column("Alumno", width=250, anchor='w', minwidth=200)

    for act_nombre in actividad_nombres:
        tree.heading(act_nombre, text=act_nombre)
        # Centrar el texto en las columnas de calificación
        tree.column(act_nombre, width=120, anchor='center', minwidth=80)

    x_scrollbar.pack(side='bottom', fill='x')
    y_scrollbar.pack(side='right', fill='y')
    tree.pack(side='left', fill='both', expand=True)

    # --- Llenar Treeview ---
    tree_item_data = {}
    for alumno in alumnos:
        alumno_id_num = alumno['id']
        nombre_completo = f"{alumno.get('nombre_completo', '')} {alumno.get('apellidos', '')}".strip() or alumno.get('username')

        valores = [alumno_id_num, nombre_completo]
        alumno_grades = grades_data.get(alumno_id_num, {})
        grade_ids_for_item = {}

        for act_nombre in actividad_nombres:
            grade_info = alumno_grades.get(act_nombre)
            if grade_info and grade_info.get('calificacion') is not None: # Verificar que no sea None
                calif = grade_info['calificacion']
                # Mostrar 0 como "0.0" si es numérico y cero exacto
                if isinstance(calif, (int, float)) and calif == 0:
                     calif_display = "0.0"
                # Mostrar otros números con un decimal
                elif isinstance(calif, (int, float)):
                     calif_display = f"{calif:.1f}"
                else: # Si no es numérico (raro), mostrar como está
                     calif_display = calif

                valores.append(calif_display)
                grade_ids_for_item[act_nombre] = grade_info.get('id')
            else:
                valores.append("") # Dejar vacío si no hay calificación o es None
                grade_ids_for_item[act_nombre] = None

        iid = tree.insert("", "end", values=valores)
        tree_item_data[iid] = {'alumno_id': alumno_id_num, 'grades': grade_ids_for_item}

    # --- Funcionalidad de Edición ---
    def edit_cell(event):
        # Destruir cualquier Entry de edición anterior
        for widget in tree_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.destroy()

        region = tree.identify_region(event.x, event.y)
        if region != "cell": return

        column_id_str = tree.identify_column(event.x)
        column_index = int(column_id_str.replace('#', '')) - 1

        if column_index <= 1: return

        selected_iid = tree.focus()
        if not selected_iid: return

        actividad_nombre_edit = cols[column_index]

        # Obtener dimensiones y posición
        x, y, width, height = tree.bbox(selected_iid, column_id_str)

        entry_var = tk.StringVar(value="") # Iniciar vacío

        entry = ttk.Entry(tree_frame, textvariable=entry_var, justify='center')

        # --- AJUSTE PRINCIPAL AQUÍ ---
        # Usar el ancho de la columna completo (o casi) y la altura COMPLETA de la fila
        col_width = tree.column(column_id_str, option='width')
        # Probar con un ancho ligeramente menor que la columna para evitar solapamientos
        place_width = max(col_width - 4, 60)
        # Usar la altura COMPLETA reportada por bbox, asegurando un mínimo
        place_height = max(height, 28) # Asegurar al menos 22px de alto

        # Posicionar exactamente en la esquina superior izquierda de la celda (x, y)
        # (place maneja el tamaño desde esa esquina)
        place_x = x + 2 # Añadir un pequeño margen izquierdo
        place_y = y     # Empezar justo en el borde superior de la celda

        entry.place(x=place_x, y=place_y, width=place_width, height=place_height)
        entry.focus()
        # --- FIN DEL AJUSTE ---


        # (El resto de la función save_edit y los binds quedan igual)
        # --- Inicio de save_edit (sin cambios) ---
        def save_edit(event=None):
            # Verificar si el entry aún existe antes de procesar
            if not entry.winfo_exists():
                 return

            new_value_str = entry_var.get().strip()
            new_calificacion = None
            display_value = ""

            if new_value_str != "":
                try:
                    new_calificacion_float = float(new_value_str)
                    new_calificacion_float = max(0.0, min(new_calificacion_float, 100.0))
                    new_calificacion = new_calificacion_float
                    display_value = "0.0" if new_calificacion == 0 else f"{new_calificacion:.1f}"

                except ValueError:
                    messagebox.showwarning("Inválido", "Ingresa un número válido (ej. 85 o 7.5).")
                    entry.focus()
                    return

            # Actualizar Treeview
            tree.set(selected_iid, column_id_str, display_value)

            # Lógica para guardar en BBDD
            item_info = tree_item_data.get(selected_iid)
            if item_info:
                alumno_id_num = item_info['alumno_id']
                activity_grade_id = item_info['grades'].get(actividad_nombre_edit)
                peso = actividad_pesos.get(actividad_nombre_edit, 1.0)
                calificacion_a_guardar = new_calificacion if new_calificacion is not None else 0.0

                success = db_manager.add_or_update_grade(
                    id_alumno=alumno_id_num,
                    id_materia=subject_id,
                    descripcion=actividad_nombre_edit,
                    peso=peso,
                    calificacion=calificacion_a_guardar,
                    activity_id=activity_grade_id
                )
                if not success:
                     messagebox.showerror("Error DB", f"No se pudo guardar la calificación para {actividad_nombre_edit}.")
                else:
                    pass # Éxito al guardar

            # Destruir el Entry solo si la validación fue exitosa o si se dejó vacío
            if entry.winfo_exists():
                entry.destroy()
        # --- Fin de save_edit ---

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.bind("<Escape>", lambda e: entry.destroy() if entry.winfo_exists() else None)

    # El bind del Treeview queda igual
    tree.bind("<Double-1>", edit_cell)

    return main_frame # El return de create_professor_grade_view queda igual