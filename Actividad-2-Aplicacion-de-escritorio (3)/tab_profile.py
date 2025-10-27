# tab_profile.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import db_manager # Importa la lógica de la BBDD

def create_profile_tab(parent_frame, user_data, update_header_callback):
    """Crea la pestaña/vista de perfil del usuario."""

    student_id = user_data['id'] # ID numérico

    profile_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    # No pack aquí, se hará en student_main_view

    ttk.Label(profile_frame, text="Mi Perfil", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10, anchor='w', padx=10)

    center_frame = ttk.Frame(profile_frame, style="Main.TFrame")
    center_frame.pack(pady=10, padx=20, expand=True) # Centrar contenido

    # --- Imagen de Perfil ---
    profile_photo_img = None
    img_label = tk.Label(center_frame, width=120, height=120, bg="lightgrey", relief="solid", bd=1) # Placeholder

    def load_profile_image():
        nonlocal profile_photo_img # Para actualizar la referencia global
        # Recargar datos del usuario por si la ruta cambió
        current_user_data = db_manager.get_user_by_id(student_id)
        img_path = current_user_data.get('ruta_foto', 'assets/default_user.png')
        if not os.path.exists(img_path):
             img_path = 'assets/default_user.png'
        try:
            img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
            profile_photo_img = ImageTk.PhotoImage(img)
            img_label.config(image=profile_photo_img, width=120, height=120, bg='white')
            img_label.image = profile_photo_img # Guardar referencia
        except Exception as e:
            print(f"Error cargando imagen de perfil: {e}")
            img_label.config(image='', text="Error", width=15, height=7) # Resetear si falla

    load_profile_image() # Carga inicial
    img_label.pack(pady=10)

    def cambiar_foto_perfil():
        filepath = filedialog.askopenfilename(
            title="Selecciona tu foto de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif")]
        )
        if not filepath: return

        # Usar ID numérico para el nombre de archivo es más robusto que username
        ext = os.path.splitext(filepath)[1]
        destino = f"assets/{student_id}{ext}" # Ej: assets/1.png

        try:
            shutil.copy(filepath, destino)
            ruta_final_relativa = destino # Guardar ruta relativa

            # Actualizar en BBDD
            db_manager.update_user_photo(student_id, ruta_final_relativa)

            # Recargar UI
            load_profile_image() # Actualizar imagen en esta vista
            if update_header_callback:
                 update_header_callback() # Llamar al callback para actualizar header

            messagebox.showinfo("Éxito", "Foto de perfil actualizada.")
        except Exception as e:
            messagebox.showerror("Error al Copiar", f"No se pudo guardar la foto: {e}")

    # Botón para cambiar foto (usando ttk)
    ttk.Button(center_frame, text="Cambiar Foto", command=cambiar_foto_perfil, style="Accent.TButton").pack(pady=(0, 15))


    # --- Formulario ---
    form_frame = ttk.Frame(center_frame, style="Main.TFrame")
    form_frame.pack(pady=10)

    # Variables de Tkinter
    nombre_var = tk.StringVar(value=user_data.get('nombre_completo', ''))
    apellidos_var = tk.StringVar(value=user_data.get('apellidos', ''))
    telefono_var = tk.StringVar(value=user_data.get('telefono', '') or '') # Asegurar string vacío si es None
    direccion_var = tk.StringVar(value=user_data.get('direccion', '') or '') # Asegurar string vacío

    fields_readonly = [
        ("Matrícula", user_data.get('username', '')),
        ("Rol", user_data.get('role', '').capitalize()),
    ]
    fields_editable = [
        ("Nombre(s)", nombre_var),
        ("Apellidos", apellidos_var),
        ("Teléfono", telefono_var),
        ("Dirección", direccion_var)
    ]

    # Campos Readonly
    for i, (label_text, value) in enumerate(fields_readonly):
        ttk.Label(form_frame, text=label_text, style="TLabel").grid(row=i, column=0, sticky='w', padx=5, pady=5)
        entry = ttk.Entry(form_frame, width=40)
        entry.insert(0, value)
        entry.config(state='readonly') # Usar readonly en lugar de disabled para poder copiar
        entry.grid(row=i, column=1, sticky='we', padx=5, pady=5)

    # Campos Editables
    current_row = len(fields_readonly)
    for i, (label_text, var) in enumerate(fields_editable):
        ttk.Label(form_frame, text=label_text, style="TLabel").grid(row=current_row + i, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=var, width=40).grid(row=current_row + i, column=1, sticky='we', padx=5, pady=5)

    def guardar_perfil():
        success = db_manager.update_user_profile_details(
            user_id=student_id,
            nombre_completo=nombre_var.get().strip(),
            apellidos=apellidos_var.get().strip(),
            telefono=telefono_var.get().strip() or None, # Guardar None si vacío
            direccion=direccion_var.get().strip() or None # Guardar None si vacío
        )
        if success:
            messagebox.showinfo("Éxito", "Tu información ha sido actualizada.")
            # Podrías querer actualizar user_data localmente si lo usas en otro lugar
            # y también el header si muestra nombre/apellidos
            if update_header_callback:
                 update_header_callback() # Actualizar por si cambió el nombre
        else:
            messagebox.showerror("Error", "No se pudo guardar la información.")

    # --- Botón Guardar ---
    ttk.Button(
        center_frame,
        text="Guardar Cambios",
        command=guardar_perfil,
        style="Green.TButton", # Usar estilo verde
        width=20
    ).pack(pady=20)

    return profile_frame # Devuelve el frame principal de esta vista