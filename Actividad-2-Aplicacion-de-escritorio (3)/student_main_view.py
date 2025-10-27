# student_main_view.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import db_manager # Import DB manager

# Importar las vistas
from student_subjects_view import create_student_subjects_view
from tab_profile import create_profile_tab # Reutilizar lógica de perfil

# Placeholders globales
_logout_func = None
_update_header_func = None
student_lbl_photo_header = None

def show_view(content_frame, user_data, view_name):
    """Limpia el frame de contenido y muestra la vista seleccionada."""
    for widget in content_frame.winfo_children():
        widget.destroy()

    if view_name == "subjects":
        view_canvas = create_student_subjects_view(content_frame, user_data)
    elif view_name == "profile":
        view_frame = create_profile_tab(content_frame, user_data, _update_header_func)
        view_frame.pack(fill=tk.BOTH, expand=True)

def create_student_main_view(root, user_data, logout_func, update_header_func):
    """Crea el dashboard principal del alumno con sidebar y área de contenido."""
    global _logout_func, _update_header_func, student_lbl_photo_header
    _logout_func = logout_func
    _update_header_func = update_header_func # Guardar la función

    # Configurar grid de la ventana raíz
    sidebar_width = 220 # Ancho ajustado para el banner
    root.columnconfigure(0, weight=0, minsize=sidebar_width) # Sidebar con ancho fijo
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # --- Sidebar (Verde) ---
    sidebar_frame = tk.Frame(root, bg="#28a745", width=sidebar_width)
    sidebar_frame.grid(row=0, column=0, sticky="nsew")
    # Configurar filas: banner (0), nav_frame (1, expande), bottom_frame (2)
    sidebar_frame.rowconfigure(1, weight=1) # Fila del medio se expande
    sidebar_frame.pack_propagate(False)

    # Banner (Arriba)
    try:
        banner_img_path = "assets/banner.png"
        original_img = Image.open(banner_img_path)
        img_w, img_h = original_img.size
        target_w = sidebar_width - 20
        ratio = target_w / img_w
        target_h = int(img_h * ratio)
        banner_img = original_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)
        lbl_banner = tk.Label(sidebar_frame, image=banner_photo, bg="#28a745")
        lbl_banner.image = banner_photo
        # Usar grid para el banner en la fila 0
        lbl_banner.grid(row=0, column=0, pady=20, padx=10, sticky="ew")
    except Exception as e:
        print(f"Error cargando banner.png: {e}")
        ttk.Label(sidebar_frame, text="[BANNER]", background="#28a745", foreground="white", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=20, padx=10)

    # --- Frame para Materias (Se queda arriba) ---
    nav_frame = tk.Frame(sidebar_frame, bg="#28a745")
    # Usar grid para nav_frame en la fila 1 (la que se expande), pegado arriba
    nav_frame.grid(row=1, column=0, sticky="new", pady=10, padx=10)
    nav_frame.columnconfigure(1, weight=1)

    style = ttk.Style()
    style.configure("Sidebar.TButton", font=("Helvetica", 11), foreground="white",
                    background="#28a745", anchor="w", padding=(15, 10))
    style.map("Sidebar.TButton", background=[("active", "#218838")])

    separator = tk.Frame(nav_frame, bg="white", width=2, height=25)
    separator.grid(row=0, column=0, sticky="ns", padx=(5, 5))

    btn_materias = ttk.Button(nav_frame, text="Materias", style="Sidebar.TButton",
                              command=lambda: show_view(content_frame, user_data, "subjects"))
    btn_materias.grid(row=0, column=1, sticky="ew", pady=(10, 5))

    # --- CAMBIO: Frame para Botones Inferiores (Perfil y Salir) ---
    bottom_frame = tk.Frame(sidebar_frame, bg="#28a745")
    # Usar grid para bottom_frame en la fila 2 (la de abajo), pegado abajo
    bottom_frame.grid(row=2, column=0, sticky="sew", pady=20, padx=10)
    bottom_frame.columnconfigure(0, weight=1) # La columna se expande

    # Perfil Button (Dentro de bottom_frame)
    btn_perfil = ttk.Button(bottom_frame, text="Perfil", style="Sidebar.TButton",
                             command=lambda: show_view(content_frame, user_data, "profile"))
    btn_perfil.grid(row=0, column=0, sticky="ew", pady=(0,5)) # Fila 0 de bottom_frame

    # Salir Button (Dentro de bottom_frame)
    btn_salir = ttk.Button(bottom_frame, text="➔ Salir", style="Sidebar.TButton",
                           command=_logout_func)
    btn_salir.grid(row=1, column=0, sticky="ew", pady=(5,0)) # Fila 1 de bottom_frame
    # --- FIN DEL CAMBIO ---


    # --- Área de Contenido (Derecha) ---
    content_area = ttk.Frame(root, style="Main.TFrame", padding=(20, 10))
    content_area.grid(row=0, column=1, sticky="nsew")
    content_area.rowconfigure(1, weight=1); content_area.columnconfigure(0, weight=1)

    # Header en Área de Contenido
    header_frame = ttk.Frame(content_area, style="Main.TFrame")
    header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))

    student_lbl_photo_header = ttk.Label(header_frame, style="TLabel")
    student_lbl_photo_header.pack(side=tk.RIGHT, padx=(0, 10))

    _update_header_func() # Carga inicial

    header_text = f"{user_data['nombre_completo']} ({user_data['role'].capitalize()})"
    ttk.Label(header_frame, text=header_text, font=("Helvetica", 14), style="TLabel").pack(side=tk.RIGHT, padx=(0,10))

    # Frame para vistas
    content_frame = ttk.Frame(content_area, style="Main.TFrame")
    content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))

    # Vista inicial
    show_view(content_frame, user_data, "subjects")