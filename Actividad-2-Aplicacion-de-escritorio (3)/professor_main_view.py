# professor_main_view.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import platform
import db_manager

# Importar VISTAS del Profesor
from professor_subjects_view import create_professor_subjects_view
from professor_grade_view import create_professor_grade_view
from professor_add_activity_view import create_professor_add_activity_view
from professor_edit_activity_view import create_professor_edit_activity_view
from professor_delete_activity_view import create_professor_delete_activity_view
from tab_profile import create_profile_tab

# Placeholders globales
_logout_func = None
_update_header_func = None
professor_lbl_photo_header = None
_icon_images = {}
_nav_buttons = {}

def load_icon(filename, size=(20, 20)):
    try:
        path = os.path.join("assets", filename)
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _icon_images[filename] = photo
        return photo
    except Exception as e:
        print(f"Error icon {filename}: {e}")
        return None

def show_professor_view(content_frame, user_data, view_name, **kwargs):
    """Limpia el frame y muestra la vista de profesor seleccionada."""
    # Desmarcar/Marcar botones
    for key, btn in _nav_buttons.items():
        btn.state(['!selected'])
    button_key_to_select = view_name
    if view_name == 'grade_view':
        button_key_to_select = 'subjects'
    if button_key_to_select in _nav_buttons:
        _nav_buttons[button_key_to_select].state(['selected'])

    for widget in content_frame.winfo_children():
        widget.destroy()

    view = None
    if view_name == "subjects":
        switch_func = lambda subject_id: show_professor_view(content_frame, user_data, "grade_view", subject_id=subject_id)
        view = create_professor_subjects_view(content_frame, user_data, switch_func)
        if isinstance(view, tk.Frame) or isinstance(view, ttk.Frame):
            view.pack(fill=tk.BOTH, expand=True)

    elif view_name == "add_activity":
        view = create_professor_add_activity_view(content_frame, user_data)
        view.pack(fill=tk.BOTH, expand=True)

    elif view_name == "edit_activity":
        view = create_professor_edit_activity_view(content_frame, user_data)
        view.pack(fill=tk.BOTH, expand=True)

    elif view_name == "delete_activity":
        view = create_professor_delete_activity_view(content_frame, user_data)
        view.pack(fill=tk.BOTH, expand=True)

    elif view_name == "grade_view":
        subject_id = kwargs.get('subject_id')
        if subject_id:
            view = create_professor_grade_view(content_frame, user_data, subject_id)
            view.pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(content_frame, text="Error: ID de materia no especificado.").pack()

    elif view_name == "profile":
        view = create_profile_tab(content_frame, user_data, _update_header_func)
        view.pack(fill=tk.BOTH, expand=True)

    else:
        ttk.Label(content_frame, text=f"Vista '{view_name}' no encontrada.").pack()

def create_professor_main_view(root, user_data, logout_func, update_header_func):
    """Crea el dashboard principal del Profesor con sidebar."""
    global _logout_func, _update_header_func, professor_lbl_photo_header, _icon_images, _nav_buttons
    _logout_func = logout_func
    _update_header_func = update_header_func
    _icon_images = {}
    _nav_buttons = {}

    # Configurar el tema según el sistema operativo
    style = ttk.Style()
    if platform.system() == "Darwin":  # macOS
        style.theme_use("aqua")
    else:  # Windows u otros
        style.theme_use("clam")

    # Configurar estilo para botones
    style.configure("Sidebar.TButton", font=("Helvetica", 11), anchor="w", padding=(15, 10))

    # Configuración Root
    sidebar_width = 230
    root.columnconfigure(0, weight=0, minsize=sidebar_width)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # --- Sidebar ---
    sidebar_frame = tk.Frame(root, bg="#28a745")
    sidebar_frame.grid(row=0, column=0, sticky="nsew")
    sidebar_frame.rowconfigure(1, weight=1)
    sidebar_frame.pack_propagate(False)

    # Banner
    try:
        banner_width = sidebar_width - 20
        banner_img_path = "assets/banner.png"
        original_img = Image.open(banner_img_path)
        img_w, img_h = original_img.size
        ratio = banner_width / img_w
        banner_height = int(img_h * ratio)
        banner_img = original_img.resize((banner_width, banner_height), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)
        lbl_banner = tk.Label(sidebar_frame, image=banner_photo, bg="#28a745")
        lbl_banner.image = banner_photo
        lbl_banner.grid(row=0, column=0, pady=20, padx=10, sticky="ew")
    except Exception as e:
        print(f"Error banner: {e}")
        tk.Label(sidebar_frame, text="[BANNER]", bg="#28a745", fg="white", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=20, padx=10)

    # --- Nav Frame ---
    nav_frame = tk.Frame(sidebar_frame, bg="#28a745")
    nav_frame.grid(row=1, column=0, sticky="new", pady=10, padx=10)
    nav_frame.columnconfigure(1, weight=1)

    # Cargar Íconos
    icons = {
        "subjects": load_icon("icon_materias_prof.png"),
        "add_activity": load_icon("icon_add_activity.png"),
        "edit_activity": load_icon("icon_edit_activity.png"),
        "delete_activity": load_icon("icon_delete_activity.png"),
        "profile": load_icon("icon_perfil.png"),
        "salir": load_icon("icon_salir.png")
    }

    # Crear Botones
    buttons_info = [
        ("subjects", " Materias", "subjects"),
        ("add_activity", " Agregar Actividad", "add_activity"),
        ("edit_activity", " Editar Actividad", "edit_activity"),
        ("delete_activity", " Eliminar Actividad", "delete_activity"),
    ]
    for i, (view_name, text, icon_key) in enumerate(buttons_info):
        icon = icons.get(icon_key)
        btn = ttk.Button(
            nav_frame,
            text=text,
            style="Sidebar.TButton",
            image=icon,
            compound=tk.LEFT,
            command=lambda v=view_name: show_professor_view(content_frame, user_data, v)  # Corregido
        )
        btn.grid(row=i, column=0, columnspan=2, sticky="ew", pady=5)
        if i == 0:
            btn.state(['selected'])  # Marcar como seleccionado al inicio
        _nav_buttons[view_name] = btn

    # --- Botones Inferiores ---
    bottom_frame = tk.Frame(sidebar_frame, bg="#28a745")
    bottom_frame.grid(row=2, column=0, sticky="sew", pady=20, padx=10)
    bottom_frame.columnconfigure(0, weight=1)

    btn_perfil = ttk.Button(bottom_frame, text=" Perfil", style="Sidebar.TButton", image=icons.get("profile"), compound=tk.LEFT, command=lambda: show_professor_view(content_frame, user_data, "profile"))
    btn_perfil.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    _nav_buttons["profile"] = btn_perfil

    btn_salir = ttk.Button(bottom_frame, text=" Salir", style="Sidebar.TButton", image=icons.get("salir"), compound=tk.LEFT, command=_logout_func)
    btn_salir.grid(row=1, column=0, sticky="ew", pady=(5, 0))

    # --- Área de Contenido ---
    content_area = ttk.Frame(root, padding=(20, 10))
    content_area.grid(row=0, column=1, sticky="nsew")
    content_area.rowconfigure(1, weight=1)
    content_area.columnconfigure(0, weight=1)

    header_frame = ttk.Frame(content_area)
    header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))

    professor_lbl_photo_header = ttk.Label(header_frame)
    professor_lbl_photo_header.pack(side=tk.RIGHT, padx=(0, 10))

    _update_header_func()  # Carga inicial
    header_text = f"{user_data.get('nombre_completo', 'Profesor')} ({user_data['role'].capitalize()})"
    ttk.Label(header_frame, text=header_text, font=("Helvetica", 14)).pack(side=tk.RIGHT, padx=(0, 10))

    content_frame = ttk.Frame(content_area)
    content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Vista inicial: Materias
    show_professor_view(content_frame, user_data, "subjects")

    return content_frame