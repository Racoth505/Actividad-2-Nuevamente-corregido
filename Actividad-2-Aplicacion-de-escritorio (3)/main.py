# main.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import shutil
from PIL import Image, ImageTk
import platform

# --- Managers and Styles ---
import db_manager
# from app_styles import configure_styles -- No se utiliza para permitir al sistema hacer los cambios necesarios

# --- VISTAS PRINCIPALES POR ROL ---
from admin_main_view import create_admin_main_view  # Vista Admin con Sidebar
from professor_main_view import create_professor_main_view  # Vista Profesor con Sidebar
from student_main_view import create_student_main_view  # Vista Alumno con Sidebar

# --- Initialize DB ---
db_manager.initialize_database()

# --- Global root window ---
root = tk.Tk()

style = ttk.Style()
if platform.system() == "Darwin":  # macOS
    style.theme_use("aqua")
else:  # Windows u otros
    style.theme_use("clam")  # Tema compatible con personalización de colores

style.configure("Green.TButton", background="#f0f2f5", foreground="black", font=("Helvetica", 12, "bold"))
style.map("Green.TButton",
    background=[("active", "#28a745")], # Color al pasar el ratón
    foreground=[("active", "white")]
)

# --- Login Logic ---
def validate_login(username, password):
    """Valida credenciales contra la base de datos SQLite."""
    user_data = db_manager.validate_login(username, password)
    if user_data:
        return user_data  # user_data es un dict con id, username, role, etc.
    return None

# --- Logout Function ---
def logout():
    """Destruye la ventana principal de la app y muestra la página de login de nuevo."""
    for widget in root.winfo_children():
        widget.destroy()
    root.columnconfigure(0, weight=0); root.columnconfigure(1, weight=0); root.rowconfigure(0, weight=0)
    show_login_page()

# --- Login Page ---
def show_login_page():
    """Crea y muestra la página de inicio de sesión."""
    global root
    if root is None:
        root = tk.Tk()
        root.withdraw()
        root.configure(bg="#f0f2f5")
        # configure_styles() -- no se usa

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Inicio de Sesión - Sistema de Calificaciones")
    root.geometry("800x500")

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=2); root.columnconfigure(1, weight=3)

    # Panel Izquierdo (Verde)
    left_frame = tk.Frame(root, bg="#28a745")
    left_frame.grid(row=0, column=0, sticky="nsew")
    left_content = tk.Frame(left_frame, bg="#28a745")
    left_content.pack(expand=True)

    try:
        logo_img = Image.open("assets/logo.png").resize((120, 100), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        lbl_logo = tk.Label(left_content, image=logo_photo, bg="#28a745")
        lbl_logo.image = logo_photo
        lbl_logo.pack(pady=10)
    except Exception as e:
        print(f"Error cargando logo.png: {e}")

    tk.Label(left_content, text="TECMILENIO",
             font=("Helvetica", 24, "bold"),
             bg="#28a745", fg="white").pack(pady=10)
    tk.Label(left_content, text="Bienvenido",
             font=("Helvetica", 16),
             bg="#28a745", fg="white").pack(pady=5)

    # Panel Derecho (Gris)
    right_frame = ttk.Frame(root, style="Main.TFrame")
    right_frame.grid(row=0, column=1, sticky="nsew")
    right_content = ttk.Frame(right_frame, style="Main.TFrame", padding=50)
    right_content.pack(expand=True)

    ttk.Label(right_content, text="Ingresar", font=("Helvetica", 22, "bold")).pack(anchor="w", pady=(0, 25))
    ttk.Label(right_content, text="Matrícula").pack(anchor="w", pady=(5, 0))
    entry_username = ttk.Entry(right_content, width=40, font=("Helvetica", 11))
    entry_username.pack(fill="x", pady=(0, 10), ipady=4)
    ttk.Label(right_content, text="Contraseña").pack(anchor="w", pady=(5, 0))
    entry_password = ttk.Entry(right_content, width=40, show="*", font=("Helvetica", 11))
    entry_password.pack(fill="x", pady=(0, 20), ipady=4)

    # --- Función de login ---
    def attempt_login(event=None):  # event=None permite usar binding con Enter
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        user_data = validate_login(username, password)
        if user_data:
            left_frame.destroy()
            right_frame.destroy()
            root.columnconfigure(0, weight=0); root.columnconfigure(1, weight=0)
            show_main_app(user_data)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    # Botón de login
    ttk.Button(right_content, text="Ingresar", command=attempt_login, style="Green.TButton").pack(fill="x", ipady=8)

    # Vincular tecla Enter para login
    entry_username.bind("<Return>", attempt_login)
    entry_password.bind("<Return>", attempt_login)

    # Mostrar ventana
    root.deiconify()
    if not hasattr(root, '_mainloop_running') or not root._mainloop_running:
        root._mainloop_running = True
        root.mainloop()


# --- APP PRINCIPAL ---
def show_main_app(user_data):
    """Crea la ventana principal basada en el rol del usuario."""
    role = user_data["role"]

    for widget in root.winfo_children():
        widget.destroy()


    root.title(f"Sistema de Calificaciones - Panel: {role.capitalize()}")
    if role == 'admin':
        root.geometry("1100x700")
    elif role == 'profesor':
        root.geometry("950x700")
    else:
        root.geometry("950x700")

    # Función para actualizar foto de header
    def update_header_photo():
        target_label = None
        current_user_data = db_manager.get_user_by_id(user_data["id"])
        if not current_user_data: return

        try:
            if role == 'admin':
                import admin_main_view
                target_label = admin_main_view.admin_lbl_photo_header
            elif role == 'profesor':
                import professor_main_view
                target_label = professor_main_view.professor_lbl_photo_header
            elif role == 'alumno':
                import student_main_view
                target_label = student_main_view.student_lbl_photo_header
        except (NameError, AttributeError, ImportError):
            print("DEBUG: No se pudo encontrar la referencia al label del header.")
            target_label = None

        if target_label is None: return

        try:
            image_path = current_user_data["ruta_foto"]
            if not os.path.exists(image_path): image_path = "assets/default_user.png"
            size = (40, 40) if role == 'admin' else (50, 50)
            img = Image.open(image_path).resize(size, Image.Resampling.LANCZOS)
            photo_tk = ImageTk.PhotoImage(img)

            target_label.config(image=photo_tk)
            target_label.image = photo_tk
        except Exception as e:
            print(f"No se pudo recargar la imagen del header: {e}")

    # Renderizar UI según rol
    if role == 'admin':
        create_admin_main_view(root, user_data, logout)
    elif role == 'profesor':
        create_professor_main_view(root, user_data, logout, update_header_photo)
    elif role == 'alumno':
        create_student_main_view(root, user_data, logout, update_header_photo)


show_login_page()  # Mostrar login
