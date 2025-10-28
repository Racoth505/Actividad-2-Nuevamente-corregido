# admin_main_view.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import platform
import db_manager
import sys # <--- AÑADIDO: Importar sys para resource_path

# --- Importar VISTAS del Admin ---
from admin_add_user_view import create_admin_add_user_view
from admin_users_view import create_admin_users_tab
from admin_manage_subjects_view import create_manage_subjects_view
from admin_edit_subjects_view import create_edit_subjects_view
from admin_edit_users_view import create_edit_users_view
from admin_assign_subject_view import create_assign_subject_view

# --- FUNCIÓN DE RUTA DE RECURSOS ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para script y para app congelada. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)
# ------------------------------------

# Placeholders globales
_logout_func = None
admin_lbl_photo_header = None # Referencia al label de foto en el header (placeholder)
_icon_images = {} # Guardar referencias a las imágenes de íconos
_nav_buttons = {} # Guardar referencias a los botones de navegación

def load_icon(filename, size=(20, 20)):
    """Carga, redimensiona y guarda una imagen de ícono, usando resource_path."""
    try:
        # --- CORREGIDO: Usando resource_path para la ruta del ícono ---
        path = resource_path(os.path.join("assets", filename))
        
        if not os.path.exists(path):
            print(f"Advertencia: Archivo de icono no encontrado en {path}")
            # Puedes usar una imagen de placeholder aquí si lo deseas
            # return ImageTk.PhotoImage(Image.new('RGB', size, color='grey'))
            return None
            
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _icon_images[filename] = photo # Guardar referencia
        return photo
    except Exception as e:
        print(f"Error cargando icono {filename}: {e}")
        return None

def show_admin_view(content_frame, user_data, view_name):
    """Limpia el frame y muestra la vista de admin seleccionada."""
    # Desmarcar botón previo (visual feedback)
    for btn in _nav_buttons.values():
        btn.state(['!selected']) # Remove 'selected' state

    # Marcar botón actual como seleccionado
    if view_name in _nav_buttons:
        _nav_buttons[view_name].state(['selected']) # Add 'selected' state

    # Limpiar el área de contenido
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Cargar la vista correspondiente
    view = None # Initialize view variable
    if view_name == "add_user":
        # --- CORREGIDO: create_admin_add_user_view ya no usa user_data ---
        view = create_admin_add_user_view(content_frame)
    elif view_name == "manage_subjects":
         view = create_manage_subjects_view(content_frame)
    elif view_name == "edit_subjects":
         view = create_edit_subjects_view(content_frame)
    elif view_name == "edit_users":
         view = create_edit_users_view(content_frame)
    elif view_name == "assign_subject":
         view = create_assign_subject_view(content_frame)
    elif view_name == "users":
         view = create_admin_users_tab(content_frame)


    # If a view was created, pack it into the content frame
    if view:
        view.pack(fill=tk.BOTH, expand=True)
    else:
        # Fallback if view name is unknown
        ttk.Label(content_frame, text=f"Vista '{view_name}' no encontrada o en construcción.").pack(expand=True)


def create_admin_main_view(root, user_data, logout_func):
    """Crea el dashboard principal del Admin con la nueva sidebar."""
    global _logout_func, admin_lbl_photo_header, _icon_images, _nav_buttons
    _logout_func = logout_func
    _icon_images = {} # Limpiar íconos previos
    _nav_buttons = {} # Limpiar referencias a botones

    style = ttk.Style()
    if platform.system() == "Darwin":  # macOS
        style.theme_use("aqua")
    else:  # Windows u otros
        style.theme_use("clam")  # Tema compatible con personalización de colores

    # Configurar grid de la ventana raíz
    sidebar_width = 230 # Ancho ajustado
    root.columnconfigure(0, weight=0, minsize=sidebar_width) # Sidebar fija
    root.columnconfigure(1, weight=1) # Contenido expande
    root.rowconfigure(0, weight=1)

    # --- Sidebar (Verde) ---
    sidebar_frame = tk.Frame(root, bg="#28a745", width=sidebar_width)
    sidebar_frame.grid(row=0, column=0, sticky="nsew")
    sidebar_frame.rowconfigure(1, weight=1) # Fila del medio expande para empujar Salir abajo
    sidebar_frame.pack_propagate(False)

    # Banner
    try:
        # --- CORREGIDO: Usando resource_path para la ruta del banner ---
        banner_img_path = resource_path("assets/banner.png")
        original_img = Image.open(banner_img_path)
        
        banner_width = sidebar_width - 20
        img_w, img_h = original_img.size
        ratio = banner_width / img_w
        banner_height = int(img_h * ratio)
        banner_img = original_img.resize((banner_width, banner_height), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)

        lbl_banner = tk.Label(sidebar_frame, image=banner_photo, bg="#28a745")
        lbl_banner.image = banner_photo
        lbl_banner.grid(row=0, column=0, pady=20, padx=10, sticky="ew")
    except Exception as e:
        print(f"Error cargando banner.png: {e}")
        # Placeholder text if banner fails
        ttk.Label(sidebar_frame, text="[BANNER]", background="#28a745", foreground="white", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=20, padx=10)


    # --- Frame para botones de navegación ---
    nav_frame = tk.Frame(sidebar_frame, bg="#28a745")
    nav_frame.grid(row=1, column=0, sticky="new", pady=10, padx=10) # Pegado arriba
    nav_frame.columnconfigure(1, weight=1) # Columna del texto expande

    # --- Cargar Íconos ---
    icons = {
        "add_user": load_icon("icon_add_user.png"),
        "manage_subjects": load_icon("icon_add_subject.png"),
        "edit_subjects": load_icon("icon_edit_subject.png"),
        "edit_users": load_icon("icon_edit_user.png"),
        "assign_subject": load_icon("icon_assign.png"),
        "users": load_icon("icon_usuarios.png"),
        "salir": load_icon("icon_salir.png")
    }

    # --- Crear Botones ---
    buttons_info = [
        ("add_user", " Agregar Usuarios", "add_user"),
        ("manage_subjects", " Agregar Materias", "manage_subjects"),
        ("edit_subjects", " Editar Materias", "edit_subjects"),
        ("edit_users", " Editar Usuarios", "edit_users"),
        ("assign_subject", " Asignar Materia", "assign_subject"),
        ("users", " Usuarios", "users"),
    ]

    for i, (view_name, text, icon_key) in enumerate(buttons_info):
        icon = icons.get(icon_key)
        btn = ttk.Button(
            nav_frame,
            text=text,
            style="Sidebar.TButton",
            image=icon,
            compound=tk.LEFT,
            command=lambda v=view_name: show_admin_view(content_frame, user_data, v)
        )

        btn.grid(row=i, column=0, columnspan=2, sticky="ew", pady=5)
        if i == 0:
            btn.state(['selected'])  # Marcar como seleccionado al inicio

        _nav_buttons[view_name] = btn

    # --- Botón Salir (Abajo) ---
    bottom_frame = tk.Frame(sidebar_frame, bg="#28a745")
    bottom_frame.grid(row=2, column=0, sticky="sew", pady=20, padx=10)
    bottom_frame.columnconfigure(0, weight=1)

    btn_salir = ttk.Button(bottom_frame, text=" Salir", style="Sidebar.TButton",
                           image=icons.get("salir"), compound=tk.LEFT,
                           command=_logout_func)
    btn_salir.grid(row=0, column=0, sticky="ew")


    # --- Área de Contenido (Derecha) ---
    content_area = ttk.Frame(root, style="Main.TFrame", padding=(20, 10))
    content_area.grid(row=0, column=1, sticky="nsew")
    content_area.rowconfigure(1, weight=1); content_area.columnconfigure(0, weight=1)

    # Header
    header_frame = ttk.Frame(content_area, style="Main.TFrame")
    header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))

    # Placeholder para foto del admin (no tiene foto, usar icono)
    # Assign to global var so main.py's update function can find it
    admin_lbl_photo_header = ttk.Label(header_frame, text="👤", font=("Helvetica", 20), style="TLabel")
    admin_lbl_photo_header.pack(side=tk.RIGHT, padx=(0, 10))

    header_text = f"{user_data.get('nombre_completo', 'Admin')} ({user_data['role'].capitalize()})"
    ttk.Label(header_frame, text=header_text, font=("Helvetica", 14), style="TLabel").pack(side=tk.RIGHT, padx=(0,10))

    # Frame para vistas
    content_frame = ttk.Frame(content_area, style="Main.TFrame")
    content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    # Vista inicial: Agregar Usuarios
    show_admin_view(content_frame, user_data, "add_user")