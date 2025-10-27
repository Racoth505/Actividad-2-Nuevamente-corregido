# admin_users_view.py
import tkinter as tk
from tkinter import ttk
import db_manager

def create_admin_users_tab(parent):
    """
    Vista de usuarios con filtros por rol y ordenada por matrícula (usamos 'username' como matrícula).
    Botones: Profesores | Alumnos | Administradores | Todos
    """
    tab = ttk.Frame(parent, style="Main.TFrame")

    # ---------- Barra de filtros ----------
    filters_bar = ttk.Frame(tab, style="Main.TFrame")
    filters_bar.pack(fill="x", padx=16, pady=(16, 8))

    btn_prof  = ttk.Button(filters_bar, text="Profesores")
    btn_alum  = ttk.Button(filters_bar, text="Alumnos")
    btn_admin = ttk.Button(filters_bar, text="Administradores")   # <-- NUEVO
    btn_todos = ttk.Button(filters_bar, text="Todos")

    # IMPORTANTE: empacar TODOS los botones
    btn_prof.pack(side="left", padx=(0, 8))
    btn_alum.pack(side="left", padx=8)
    btn_admin.pack(side="left", padx=8)                           # <-- NUEVO
    btn_todos.pack(side="left", padx=8)

    # ---------- Tabla ----------
    cols = ("matricula", "nombre_completo", "role", "id")
    tree = ttk.Treeview(tab, columns=cols, show="headings", height=16)

    tree.heading("matricula", text="Matrícula")
    tree.heading("nombre_completo", text="Nombre Completo")
    tree.heading("role", text="Rol")
    tree.heading("id", text="ID")

    tree.column("matricula", width=180, anchor="w")
    tree.column("nombre_completo", width=260, anchor="w")
    tree.column("role", width=120, anchor="center")
    tree.column("id", width=60, anchor="center")

    tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # ---------- Estado + carga ----------
    current_filter = {"role": None}  # None = alumnos + profesores (excluye admin)

    def load_users():
        tree.delete(*tree.get_children())

        role = current_filter["role"]
        if role is None:
            users = db_manager.get_all_users_except_admin()
        else:
            users = db_manager.get_users_by_role(role)  # 'admin', 'profesor' o 'alumno'

        # Ordenar por matrícula (username); si usas campo 'matricula', cámbialo aquí
        users_sorted = sorted(users, key=lambda u: (u.get("username") or "").lower())

        if not users_sorted:
            tree.insert("", "end", values=("—", "No hay usuarios para este filtro", "—", "—"))
            return

        for u in users_sorted:
            tree.insert("", "end", values=(
                u.get("username", ""),                 # matrícula (username)
                (u.get("nombre_completo") or ""),
                u.get("role", ""),
                u.get("id", "")
            ))

    # ---------- Botones -> comandos ----------
    def set_filter_to_prof():
        current_filter["role"] = "profesor"
        load_users()

    def set_filter_to_alum():
        current_filter["role"] = "alumno"
        load_users()

    def set_filter_to_admin():                         # <-- NUEVO
        current_filter["role"] = "admin"
        load_users()

    def set_filter_to_all():
        current_filter["role"] = "ALL"  # marca especial
        tree.delete(*tree.get_children())
        import sqlite3
        conn = db_manager.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, nombre_completo FROM Usuarios ORDER BY username")
        users = [dict(r) for r in cur.fetchall()]
        conn.close()
        for u in users:
            tree.insert("", "end", values=(u["username"], u["nombre_completo"] or "", u["role"], u["id"]))


    btn_prof.config(command=set_filter_to_prof)
    btn_alum.config(command=set_filter_to_alum)
    btn_admin.config(command=set_filter_to_admin)       # <-- NUEVO
    btn_todos.config(command=set_filter_to_all)

    # Por defecto mostrar "Todos" (sin admin)
    set_filter_to_all()
    return tab