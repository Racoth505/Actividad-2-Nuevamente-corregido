# admin_add_user_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import db_manager

def create_admin_add_user_view(parent_frame, user_data):
    """Vista para agregar nuevos usuarios, con tamaño similar a manage_subjects."""

    view_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    view_frame.columnconfigure(0, weight=1)  # Columna única se expande
    view_frame.rowconfigure(1, weight=1)     # Form se expande verticalmente

    # --- Título ---
    # --- Título ---
    title_frame = ttk.Frame(view_frame, style="Main.TFrame")
    title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0,20))
    title_frame.columnconfigure(0, weight=1)
    ttk.Label(title_frame, text="Agregar Usuarios", font=("Helvetica", 18, "bold"), style="TLabel").grid(row=0, column=0, sticky="")


    # --- Formulario ---
    form_area = ttk.Frame(view_frame, style="Main.TFrame")
    form_area.grid(row=1, column=0, sticky="n", padx=20, pady=0)
    form_area.columnconfigure(1, weight=1, minsize=350)  # Campo input expande
    form_area.columnconfigure(2, weight=0)

    # Variables
    rol_var = tk.StringVar(value="profesor")
    matricula_var = tk.StringVar()
    password_var = tk.StringVar()
    nombres_var = tk.StringVar()
    apellidos_var = tk.StringVar()
    telefono_var = tk.StringVar()
    direccion_var = tk.StringVar()
    foto_path = tk.StringVar(value="")

    # Helper
    def create_labeled_entry(parent, label_text, row, show=None, placeholder=None):
        ttk.Label(parent, text=label_text, style="TLabel").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        entry = ttk.Entry(parent, textvariable=placeholder, show=show, font=("Helvetica", 10))
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5, padx=5, ipady=4)
        if placeholder: entry.insert(0, placeholder.get())
        return entry

    # Rol
    ttk.Label(form_area, text="Rol del Usuario", style="TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    combo_rol = ttk.Combobox(
    form_area,
    textvariable=rol_var,
    values=["admin", "profesor", "alumno"],  # incluir admin
    state="readonly",
    width=37
)


    combo_rol.grid(row=0, column=1, sticky="ew", pady=5, padx=5, columnspan=2)

    # Campos
    row_idx = 1
    campos = [
        ("Matrícula", matricula_var, None),
        ("Contraseña", password_var, '*'),
        ("Nombre(s)", nombres_var, None),
        ("Apellidos", apellidos_var, None),
        ("Teléfono", telefono_var, None),
        ("Dirección", direccion_var, None)
    ]
    for label_text, var, show_char in campos:
        create_labeled_entry(form_area, label_text, row_idx, show=show_char, placeholder=var)
        row_idx += 1

    # Foto
    foto_frame = ttk.Frame(form_area, style="Main.TFrame")
    foto_frame.grid(row=row_idx, column=0, columnspan=3, pady=10)
    ttk.Label(foto_frame, text="Foto del Usuario:", style="TLabel").pack(side="left", padx=5)

    try:
        default_img = Image.open("assets/default_user.png")
    except FileNotFoundError:
        default_img = Image.new('RGB', (100,100), color='grey')
    default_img = default_img.resize((100,100))
    preview_img = ImageTk.PhotoImage(default_img)

    img_label = tk.Label(foto_frame, image=preview_img, width=100, height=100, bg="white", relief="solid")
    img_label.image = preview_img
    img_label.pack(side="left", padx=10)

    def seleccionar_foto():
        file_path = filedialog.askopenfilename(title="Seleccionar foto",
                                               filetypes=[("Archivos de imagen","*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            img = Image.open(file_path).resize((100,100))
            tk_img = ImageTk.PhotoImage(img)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            foto_path.set(file_path)

    ttk.Button(foto_frame, text="Seleccionar Foto", command=seleccionar_foto, style="Accent.TButton").pack(side="left", padx=5)

    # Guardar
    def guardar_usuario():
        rol = rol_var.get().strip()
        matricula = matricula_var.get().strip()
        password = password_var.get()
        nombres = nombres_var.get().strip()
        apellidos = apellidos_var.get().strip()
        telefono = telefono_var.get().strip() or None
        direccion = direccion_var.get().strip() or None
        ruta_foto_original = foto_path.get()
        ruta_final = None

        if not matricula or not password or not nombres:
            messagebox.showwarning("Campos Requeridos","Matrícula, Contraseña y Nombre(s) son obligatorios.")
            return

        if ruta_foto_original:
            ext = os.path.splitext(ruta_foto_original)[1]
            destino = f"assets/{matricula}{ext}"
            try: shutil.copy(ruta_foto_original, destino); ruta_final = destino
            except Exception as e:
                messagebox.showerror("Error al copiar foto", f"No se pudo guardar la foto: {e}"); ruta_final=None

        new_user_id = db_manager.create_user(username=matricula, password=password, role=rol,
                                             nombre_completo=nombres, apellidos=apellidos,
                                             telefono=telefono, direccion=direccion, ruta_foto=ruta_final)
        if new_user_id:
            messagebox.showinfo("Éxito", f"Usuario '{matricula}' agregado correctamente con ID: {new_user_id}.")
            for var in [matricula_var, password_var, nombres_var, apellidos_var, telefono_var, direccion_var]:
                var.set("")
            foto_path.set("")
            img_label.config(image=preview_img)
            img_label.image = preview_img
        else:
            messagebox.showerror("Error", f"La matrícula '{matricula}' ya existe o hubo un error.")

    ttk.Button(form_area, text="Guardar Usuario", command=guardar_usuario, style="Green.TButton").grid(
        row=row_idx+1, column=0, columnspan=3, pady=30, ipady=5, sticky="ew"
    )

    return view_frame
