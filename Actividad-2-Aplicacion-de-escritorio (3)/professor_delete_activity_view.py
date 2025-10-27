# professor_delete_activity_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importar lógica de BBDD

def create_professor_delete_activity_view(parent_frame, user_data):
    """Crea la vista para eliminar la definición de una actividad de una materia."""
    
    professor_id = user_data['id']
    
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    # No pack

    ttk.Label(main_frame, text="🗑️ Eliminar Actividad", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10, anchor='w', padx=10)

    delete_frame = ttk.Frame(main_frame, style="Main.TFrame")
    delete_frame.pack(pady=10, padx=20, anchor='n')

    # Variables
    materia_seleccionada_var = tk.StringVar()
    actividad_seleccionada_var = tk.StringVar() # Guardará la descripción a eliminar
    
    # --- Selección Materia y Actividad ---
    ttk.Label(delete_frame, text="Materia:", style="TLabel").grid(row=0, column=0, sticky='w', pady=5, padx=5)
    
    materias_profesor = db_manager.get_subjects_by_professor(professor_id)
    materia_options = {m['nombre']: m['id'] for m in materias_profesor}
    
    combo_materias = ttk.Combobox(delete_frame, textvariable=materia_seleccionada_var, 
                                  values=list(materia_options.keys()), state='readonly', width=40)
    combo_materias.grid(row=1, column=0, pady=(0, 15), padx=5)
    
    ttk.Label(delete_frame, text="Actividad a eliminar:", style="TLabel").grid(row=2, column=0, sticky='w', pady=5, padx=5)
    combo_actividades = ttk.Combobox(delete_frame, textvariable=actividad_seleccionada_var, 
                                     state='disabled', width=40)
    combo_actividades.grid(row=3, column=0, pady=(0, 20), padx=5)

    def cargar_actividades_eliminar(*args):
        """Carga las descripciones de actividades para la materia seleccionada."""
        materia_nombre = materia_seleccionada_var.get()
        materia_id = materia_options.get(materia_nombre)
        
        combo_actividades['values'] = []
        combo_actividades.set('')
        combo_actividades.config(state='disabled')
        actividad_seleccionada_var.set('')

        if not materia_id: return

        actividades_defs = db_manager.get_distinct_activities_for_subject(materia_id)
        actividad_descripciones = [act[0] for act in actividades_defs]
        
        combo_actividades['values'] = actividad_descripciones
        if actividad_descripciones:
            combo_actividades.config(state='readonly')
            combo_actividades.current(0)

    materia_seleccionada_var.trace_add("write", cargar_actividades_eliminar)

    # --- Botón Eliminar ---
    def eliminar_actividad_seleccionada():
        materia_nombre = materia_seleccionada_var.get()
        actividad_descripcion = actividad_seleccionada_var.get()
        materia_id = materia_options.get(materia_nombre)

        if not materia_id or not actividad_descripcion:
            messagebox.showwarning("Selección Requerida", "Debes seleccionar una materia y una actividad.")
            return

        confirmar = messagebox.askyesno("Confirmar Eliminación", 
             f"¿Estás seguro de eliminar TODAS las entradas para la actividad '{actividad_descripcion}' "
             f"en la materia '{materia_nombre}'?\n\n"
             f"¡Esto borrará las calificaciones de TODOS los alumnos para esta actividad y no se puede deshacer!"
        )
        
        if confirmar:
            # --- Lógica BBDD ---
            success = db_manager.delete_activity_definition(materia_id, actividad_descripcion)

            if success:
                messagebox.showinfo("Eliminado", f"Actividad '{actividad_descripcion}' eliminada correctamente.")
                # Recargar lista de actividades
                cargar_actividades_eliminar()
            else:
                messagebox.showerror("Error", f"No se encontró la actividad '{actividad_descripcion}' o hubo un error al eliminar.")

    # Usar estilo "Danger.TButton" (rojo)
    ttk.Button(delete_frame, text="Eliminar Actividad", command=eliminar_actividad_seleccionada, 
               style="Danger.TButton").grid(row=4, column=0, pady=20, padx=5, sticky='ew')

    # Carga inicial si hay materias
    if materia_options:
        combo_materias.current(0)

    return main_frame