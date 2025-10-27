# admin_assign_subject_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager

def create_assign_subject_view(parent_frame):
    """Vista para asignar materias a alumnos con tamaño y estilo consistente."""

    view_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    view_frame.columnconfigure(0, weight=1)
    view_frame.rowconfigure(1, weight=1)

    # --- Título ---
    title_frame = ttk.Frame(view_frame, style="Main.TFrame")
    title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0,20))
    title_frame.columnconfigure(0, weight=1)
    ttk.Label(title_frame, text="Asignar Materias a Alumnos", font=("Helvetica", 18, "bold"), style="TLabel").grid(row=0, column=0, sticky="")

    # --- Formulario ---
    form_frame = ttk.Frame(view_frame, style="Main.TFrame")
    form_frame.grid(row=1, column=0, sticky="n", padx=20, pady=0)
    form_frame.columnconfigure(1, weight=1, minsize=350)

    matricula_alumno_var = tk.StringVar()
    materia_id_var = tk.StringVar()
    nombre_alumno_display = ttk.Label(form_frame, text="Nombre del Alumno: ", style="TLabel", foreground='gray')
    nombre_materia_display = ttk.Label(form_frame, text="Nombre de la Materia: ", style="TLabel", foreground='gray')

    validated_student_id = None
    validated_subject_id = None

    def get_user_by_username(username):
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user: return dict(user)
        return None

    def validar_alumno_y_materia(*args):
        nonlocal validated_student_id, validated_subject_id

        alumno_username = matricula_alumno_var.get().strip()
        materia_id_str = materia_id_var.get().strip()

        # Alumno
        if alumno_username:
            alumno_data = get_user_by_username(alumno_username)
            if alumno_data and alumno_data.get('role', '').lower() == 'alumno':
                nombre_completo = f"{alumno_data['nombre_completo'] or ''} {alumno_data['apellidos'] or ''}".strip()
                nombre_alumno_display.config(text=f"Alumno: {nombre_completo}", foreground='green')
                validated_student_id = alumno_data['id']
            else:
                nombre_alumno_display.config(text="✗ Matrícula no es de Alumno o no existe", foreground='red')
                validated_student_id = None
        else:
            nombre_alumno_display.config(text="Nombre del Alumno: ", foreground='gray')
            validated_student_id = None

        # Materia
        if materia_id_str:
            if not materia_id_str.isdigit():
                nombre_materia_display.config(text="✗ ID de Materia debe ser numérico", foreground='red')
                validated_subject_id = None
            else:
                mat_id = int(materia_id_str)
                materia = db_manager.get_subject_details(mat_id)
                if materia:
                    nombre_materia_display.config(text=f"Materia: {materia['nombre']}", foreground='green')
                    validated_subject_id = materia['id']
                else:
                    nombre_materia_display.config(text="✗ ID de Materia no encontrado", foreground='red')
                    validated_subject_id = None
        else:
            nombre_materia_display.config(text="Nombre de la Materia: ", foreground='gray')
            validated_subject_id = None

    matricula_alumno_var.trace_add("write", validar_alumno_y_materia)
    materia_id_var.trace_add("write", validar_alumno_y_materia)

    # --- Campos ---
    ttk.Label(form_frame, text="Matrícula del Alumno:", style="TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(form_frame, textvariable=matricula_alumno_var).grid(row=0, column=1, sticky='ew', padx=5, pady=5, ipady=4)

    nombre_alumno_display.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)

    ttk.Label(form_frame, text="ID de la Materia:", style="TLabel").grid(row=2, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(form_frame, textvariable=materia_id_var).grid(row=2, column=1, sticky='ew', padx=5, pady=5, ipady=4)

    nombre_materia_display.grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=5)

    # --- Botón ---
    ttk.Button(form_frame, text="Asignar Materia", command=lambda: asignar_materia_a_alumno(), style="Green.TButton").grid(
        row=4, column=0, columnspan=2, pady=30, sticky='ew'
    )

    def asignar_materia_a_alumno():
        if not validated_student_id or not validated_subject_id:
            messagebox.showwarning("Advertencia", "Debe ingresar una matrícula de alumno y un ID de materia válidos.")
            return
        success = db_manager.enroll_student(validated_student_id, validated_subject_id)
        if success:
            messagebox.showinfo("Éxito", "Alumno inscrito en la materia correctamente.")
            matricula_alumno_var.set("")
            materia_id_var.set("")
            validar_alumno_y_materia()
        else:
            messagebox.showwarning("Advertencia", "El alumno ya estaba inscrito en esta materia.")

    return view_frame
