# admin_edit_users_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db_manager

def create_edit_users_view(parent_frame):
    """Vista para editar usuarios existentes, centrada y con ancho fijo."""

    view_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    view_frame.columnconfigure(0, weight=1)
    
    # --- CORRECCIÓN 1 ---
    # La fila 2 ya NO se expande. La fila 3 (vacía) SÍ lo hará.
    view_frame.rowconfigure(3, weight=1) 

    current_user_id = None

    # --- Título ---
    title_frame = ttk.Frame(view_frame, style="Main.TFrame")
    title_frame.grid(row=0, column=0, sticky="n", pady=(0,20))
    ttk.Label(title_frame, text="Editar Usuarios", font=("Helvetica", 18, "bold"), style="TLabel") \
        .pack()

    # --- Frame de búsqueda ---
    search_frame = ttk.Frame(view_frame, style="Main.TFrame")
    search_frame.grid(row=1, column=0, pady=(0,10))
    
    ttk.Label(search_frame, text="Matrícula (username) a editar:", style="TLabel") \
        .grid(row=0, column=0, sticky='e', padx=5, pady=5)
    matricula_search_var = tk.StringVar()
    entry_search = ttk.Entry(search_frame, textvariable=matricula_search_var, width=40)
    entry_search.grid(row=0, column=1, padx=5, pady=5, ipady=4)
    ttk.Button(search_frame, text="Buscar", command=lambda: cargar_usuario(), style="Accent.TButton") \
        .grid(row=0, column=2, padx=5)

    # --- Frame de edición ---
    edit_frame = ttk.Frame(view_frame, style="Main.TFrame")
    
    # --- CORRECCIÓN 2 ---
    # Añadimos sticky='n' para que el frame se pegue arriba y no se centre.
    edit_frame.grid(row=2, column=0, pady=(0,10), sticky='n') 

    # Variables
    nombres_var = tk.StringVar()
    apellidos_var = tk.StringVar()
    telefono_var = tk.StringVar()
    direccion_var = tk.StringVar()

    def get_user_by_username(username):
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user: return dict(user)
        return None

    # --- Funciones de acción ---
    def guardar_cambios():
        if current_user_id is None:
            messagebox.showerror("Error", "No hay ningún usuario cargado.")
            return
        success = db_manager.update_user_profile_details(
            user_id=current_user_id,
            nombre_completo=nombres_var.get().strip(),
            apellidos=apellidos_var.get().strip(),
            telefono=telefono_var.get().strip() or None,
            direccion=direccion_var.get().strip() or None
        )
        if success:
            messagebox.showinfo("Éxito", f"Datos de '{matricula_search_var.get().strip()}' actualizados.")
            cargar_usuario()
        else:
            messagebox.showerror("Error", "No se pudieron guardar los cambios.")

    def reset_password():
        if current_user_id is None: return
        new_pass = simpledialog.askstring(
            "Resetear Contraseña",
            f"Ingrese la nueva contraseña para {matricula_search_var.get().strip()}:",
            show='*'
        )
        if new_pass:
            db_manager.update_user_password(current_user_id, new_pass)
            messagebox.showinfo("Éxito", "Contraseña actualizada.")

    def delete_user():
        if current_user_id is None: return
        username = matricula_search_var.get().strip()
        if messagebox.askyesno(
            "Confirmar",
            f"¿Seguro que quieres eliminar a {username}?\nEsta acción es irreversible y borrará sus asignaciones y calificaciones."
        ):
            if db_manager.delete_user(current_user_id):
                messagebox.showinfo("Eliminado", f"Usuario {username} ha sido eliminado.")
                matricula_search_var.set("")
                for w in edit_frame.winfo_children(): w.destroy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar al usuario.")

    # --- Función para cargar usuario ---
    def cargar_usuario():
        nonlocal current_user_id
        username = matricula_search_var.get().strip()
        user_data = get_user_by_username(username)

        # Limpiar frame
        for widget in edit_frame.winfo_children():
            widget.destroy()

        if not user_data:
            ttk.Label(edit_frame, text=f"Usuario '{username}' no encontrado.", foreground='red', style="TLabel") \
                .pack(pady=2)
            current_user_id = None
            return

        current_user_id = user_data['id']

        # Título del usuario cargado
        ttk.Label(edit_frame, text=f"Editando: {user_data.get('username')} ({user_data.get('role')})",
                  font=("Helvetica", 14, "bold"), style="TLabel") \
            .pack(pady=(0,10)) 

        nombres_var.set(user_data.get('nombre_completo', ''))
        apellidos_var.set(user_data.get('apellidos', ''))
        telefono_var.set(user_data.get('telefono', ''))
        direccion_var.set(user_data.get('direccion', ''))

        campos = [("Nombre(s)", nombres_var), ("Apellidos", apellidos_var),
                  ("Teléfono", telefono_var), ("Dirección", direccion_var)]

        # --- Frame para los campos de entrada ---
        # Usar un grid dentro de un frame para alinear labels y entries
        fields_container = ttk.Frame(edit_frame, style="Main.TFrame")
        fields_container.pack(pady=5)
        
        for i, (label_text, var) in enumerate(campos):
            ttk.Label(fields_container, text=label_text, style="TLabel") \
                .grid(row=i, column=0, sticky='e', padx=5, pady=3)
            ttk.Entry(fields_container, textvariable=var, width=40) \
                .grid(row=i, column=1, sticky='w', padx=5, pady=3, ipady=4)

        # Botones de acción centrados
        btn_frame = ttk.Frame(edit_frame, style="Main.TFrame")
        btn_frame.pack(pady=10) 
        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios, style="Green.TButton") \
            .pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Resetear Contraseña", command=reset_password, style="Accent.TButton") \
            .pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar Usuario", command=delete_user, style="Danger.TButton") \
            .pack(side="left", padx=5)

    entry_search.bind("<Return>", lambda event: cargar_usuario())

    return view_frame