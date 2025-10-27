# professor_subjects_view.py
import tkinter as tk
from tkinter import ttk
import db_manager  # Importar lógica de la base de datos
import app_styles  # Para colores y estilos personalizados

def create_professor_subjects_view(parent_frame, user_data, show_view_func):
    """Crea la vista que muestra las tarjetas de materias asignadas al profesor, con diseño mejorado."""
    
    professor_id = user_data["id"]  # ID numérico del profesor
    
    # --- Frame principal ---
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    main_frame.columnconfigure(0, weight=1)
    
    # --- Título ---
    ttk.Label(
        main_frame,
        text="Materias Asignadas",
        font=("Helvetica", 18, "bold"),
        style="TLabel"
    ).pack(pady=15, anchor="w", padx=15)
    
    # --- Contenedor de tarjetas ---
    cards_container = ttk.Frame(main_frame, style="Main.TFrame")
    cards_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # --- Obtener materias del profesor ---
    materias_profesor = db_manager.get_subjects_by_professor(professor_id)
    
    if not materias_profesor:
        ttk.Label(
            cards_container,
            text="No tienes materias asignadas.",
            style="TLabel"
        ).pack(pady=20)
        return main_frame
    
    # --- Colores de tarjetas ---
    colores = ["#007bff", "#6f42c1", "#fd7e14"]  # Azul, Morado, Naranja
    estilos = ["BlueCard.TLabelframe", "MaroonCard.TLabelframe", "YellowCard.TLabelframe"]
    
    # --- Distribución ---
    max_cols = 3  # Tarjetas por fila
    for i, materia in enumerate(materias_profesor):
        row = i // max_cols
        col = i % max_cols
        
        materia_id = materia["id"]
        nombre = materia.get("nombre", "Sin nombre")
        
        color = colores[i % len(colores)]
        style_name = estilos[i % len(estilos)]
        
        # --- Tarjeta principal (LabelFrame) ---
        card_frame = ttk.LabelFrame(
            cards_container,
            style=style_name,
            labelwidget=tk.Label(),  # Reemplazado luego
            width=300,
            height=100
        )
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card_frame.grid_propagate(False)
        
        # --- Cabecera de la tarjeta ---
        lbl_title_widget = tk.Label(
            text=nombre,
            font=("Helvetica", 11, "bold"),
            background=color,
            foreground="white",
            anchor="center",
            padx=10,
            pady=5
        )
        card_frame.configure(labelwidget=lbl_title_widget)
        
        # --- Cuerpo interno ---
        inner_frame = ttk.Frame(card_frame, style="CardBody.TFrame")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # --- Detalle o ID ---
        ttk.Label(
            inner_frame,
            text=f"ID: {materia_id}",
            style="CardDetail.TLabel"
        ).pack(anchor="sw", padx=10, pady=(10, 5))
        
        # --- Click callback ---
        def create_callback(mid):
            return lambda e: show_view_func(mid)
        
        click_callback = create_callback(materia_id)
        
        # Hacer clickeables todos los elementos
        for widget in [card_frame, inner_frame, lbl_title_widget, *inner_frame.winfo_children()]:
            widget.bind("<Button-1>", click_callback)
    
    # --- Configurar peso de columnas ---
    for c in range(max_cols):
        cards_container.columnconfigure(c, weight=1)
    
    return main_frame
